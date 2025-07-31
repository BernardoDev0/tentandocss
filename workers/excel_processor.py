from celery import Celery
import os
import logging
import pandas as pd
from datetime import datetime
import redis
import json

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurar Celery
celery = Celery('excel_processor')
celery.conf.update(
    broker_url=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    result_backend=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='America/Sao_Paulo',
    enable_utc=True,
)

# Configurar Redis para cache de resultados
redis_client = redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379/0'))

def get_month_from_date(date_value):
    """Converter data para mês no formato 26º ao 25º"""
    try:
        if not date_value or pd.isna(date_value):
            return 'Sem Data'
        
        # Converter para datetime se necessário
        if isinstance(date_value, str):
            date_value = pd.to_datetime(date_value)
        
        # Extrair dia e mês
        day = date_value.day
        month = date_value.month
        year = date_value.year
        
        # Lógica: se dia >= 26, pertence ao mês atual
        # Se dia < 26, pertence ao mês anterior
        if day >= 26:
            target_month = month
            target_year = year
        else:
            if month == 1:
                target_month = 12
                target_year = year - 1
            else:
                target_month = month - 1
                target_year = year
        
        # Formatar como "MM/YYYY"
        month_key = f"{target_month:02d}/{target_year}"
        
        return month_key
        
    except Exception as e:
        logger.error(f"Erro ao converter data {date_value}: {str(e)}")
        return 'Sem Data'

def extract_data_from_excel_async(file_path):
    """Extrair dados de um arquivo Excel - versão assíncrona"""
    try:
        logger.info(f"Processando arquivo: {file_path}")
        
        # Ler arquivo Excel
        df = pd.read_excel(file_path, engine='openpyxl')
        
        # Verificar se o DataFrame tem dados
        if df.empty:
            return {
                'status': 'error',
                'message': 'Arquivo vazio'
            }
        
        # Extrair nome do funcionário do nome do arquivo (remover mês)
        file_name = os.path.basename(file_path)
        employee_name = file_name.replace('.xlsx', '').replace('.xls', '')
        
        # Remover mês do nome do funcionário
        month_patterns = [' Abril', ' Maio', ' Junho', ' Julho', ' Agosto', ' Setembro', ' Outubro', ' Novembro', ' Dezembro']
        for pattern in month_patterns:
            if pattern in employee_name:
                employee_name = employee_name.replace(pattern, '')
                break
        
        # Processar dados específicos
        file_data = {
            'employees': {},
            'months': {},
            'records': []
        }
        
        # Tentar identificar colunas relevantes
        columns = df.columns.tolist()
        logger.info(f"Colunas encontradas: {columns}")
        
        # Processar cada linha do DataFrame
        for index, row in df.iterrows():
            try:
                # Tentar identificar colunas de data e pontos
                date_col = None
                points_col = None
                
                for col in columns:
                    col_lower = str(col).lower()
                    if 'data' in col_lower or 'date' in col_lower:
                        date_col = col
                    elif 'ponto' in col_lower or 'pontos' in col_lower:
                        points_col = col
                
                if date_col and points_col:
                    date_value = row[date_col]
                    points_value = row[points_col]
                    
                    # Converter pontos para número
                    try:
                        points = float(points_value) if pd.notna(points_value) else 0
                    except (ValueError, TypeError):
                        points = 0
                    
                    if points > 0:
                        month_key = get_month_from_date(date_value)
                        
                        # Adicionar ao funcionário
                        if employee_name not in file_data['employees']:
                            file_data['employees'][employee_name] = {
                                'total_points': 0,
                                'records': 0
                            }
                        
                        file_data['employees'][employee_name]['total_points'] += points
                        file_data['employees'][employee_name]['records'] += 1
                        
                        # Adicionar ao mês
                        if month_key not in file_data['months']:
                            file_data['months'][month_key] = {
                                'total_points': 0,
                                'records': 0
                            }
                        
                        file_data['months'][month_key]['total_points'] += points
                        file_data['months'][month_key]['records'] += 1
                        
                        # Adicionar registro
                        record = {
                            'employee': employee_name,
                            'date': str(date_value) if pd.notna(date_value) else 'Sem Data',
                            'points': points,
                            'month': month_key
                        }
                        file_data['records'].append(record)
                
            except Exception as e:
                logger.error(f"Erro ao processar linha {index}: {str(e)}")
                continue
        
        return {
            'status': 'success',
            'data': file_data,
            'file_name': file_name
        }
        
    except Exception as e:
        logger.error(f"Erro ao processar arquivo {file_path}: {str(e)}")
        return {
            'status': 'error',
            'message': f'Erro ao processar arquivo: {str(e)}'
        }

@celery.task(bind=True)
def process_excel_folder(self, folder_path):
    """Processar pasta de arquivos Excel de forma assíncrona"""
    try:
        logger.info(f"Iniciando processamento assíncrono da pasta: {folder_path}")
        
        # Verificar se a pasta existe
        if not os.path.exists(folder_path):
            return {
                'status': 'error',
                'message': f'Pasta "{folder_path}" não encontrada'
            }
        
        # Contar arquivos Excel
        excel_files = []
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.endswith(('.xlsx', '.xls')):
                    excel_files.append(os.path.join(root, file))
        
        total_files = len(excel_files)
        logger.info(f"Encontrados {total_files} arquivos Excel para processar")
        
        # Inicializar dados agregados
        aggregated_data = {
            'employees': {},
            'months': {},
            'statistics': {
                'total_files': total_files,
                'processed_files': 0,
                'total_employees': 0,
                'total_months': 0,
                'total_records': 0,
                'total_points': 0
            }
        }
        
        # Processar cada arquivo
        for i, file_path in enumerate(excel_files):
            try:
                # Atualizar progresso
                progress = (i / total_files) * 100
                self.update_state(
                    state='PROGRESS',
                    meta={'current': i, 'total': total_files, 'progress': progress}
                )
                
                # Processar arquivo
                file_result = extract_data_from_excel_async(file_path)
                
                if file_result['status'] == 'success':
                    # Agregar dados
                    file_data = file_result['data']
                    
                    # Agregar funcionários
                    for emp_name, emp_data in file_data['employees'].items():
                        if emp_name not in aggregated_data['employees']:
                            aggregated_data['employees'][emp_name] = {
                                'total_points': 0,
                                'records': 0
                            }
                        aggregated_data['employees'][emp_name]['total_points'] += emp_data['total_points']
                        aggregated_data['employees'][emp_name]['records'] += emp_data['records']
                    
                    # Agregar meses
                    for month_key, month_data in file_data['months'].items():
                        if month_key not in aggregated_data['months']:
                            aggregated_data['months'][month_key] = {
                                'total_points': 0,
                                'records': 0
                            }
                        aggregated_data['months'][month_key]['total_points'] += month_data['total_points']
                        aggregated_data['months'][month_key]['records'] += month_data['records']
                    
                    aggregated_data['statistics']['processed_files'] += 1
                    logger.info(f"Arquivo processado: {os.path.basename(file_path)}")
                else:
                    logger.warning(f"Erro ao processar {file_path}: {file_result['message']}")
                
            except Exception as e:
                logger.error(f"Erro ao processar {file_path}: {str(e)}")
        
        # Calcular estatísticas finais
        aggregated_data['statistics']['total_employees'] = len(aggregated_data['employees'])
        aggregated_data['statistics']['total_months'] = len(aggregated_data['months'])
        aggregated_data['statistics']['total_records'] = sum(emp['records'] for emp in aggregated_data['employees'].values())
        aggregated_data['statistics']['total_points'] = sum(emp['total_points'] for emp in aggregated_data['employees'].values())
        
        # Salvar resultado no Redis
        result_key = f"excel_processing_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        redis_client.setex(
            result_key,
            3600,  # Expirar em 1 hora
            json.dumps(aggregated_data)
        )
        
        logger.info(f"Processamento concluído: {aggregated_data['statistics']['processed_files']}/{total_files} arquivos")
        
        return {
            'status': 'success',
            'message': f'Processados {aggregated_data["statistics"]["processed_files"]}/{total_files} arquivos',
            'data': aggregated_data,
            'statistics': aggregated_data['statistics'],
            'result_key': result_key
        }
        
    except Exception as e:
        logger.error(f"Erro no processamento assíncrono: {str(e)}")
        return {
            'status': 'error',
            'message': f'Erro interno: {str(e)}'
        }

@celery.task
def cleanup_excel_cache():
    """Limpar cache de processamento Excel antigo"""
    try:
        # Remover chaves de cache antigas (mais de 1 hora)
        keys = redis_client.keys("excel_processing_result_*")
        for key in keys:
            # Verificar se a chave expirou
            ttl = redis_client.ttl(key)
            if ttl == -1:  # Sem TTL definido
                redis_client.expire(key, 3600)  # Definir TTL de 1 hora
        
        logger.info("Cache de Excel limpo com sucesso")
        return {'status': 'success', 'message': 'Cache limpo'}
        
    except Exception as e:
        logger.error(f"Erro ao limpar cache: {str(e)}")
        return {'status': 'error', 'message': str(e)}

# Agendar limpeza de cache diariamente
@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        86400.0,  # 24 horas
        cleanup_excel_cache.s(),
        name='cleanup-excel-cache-daily'
    ) 