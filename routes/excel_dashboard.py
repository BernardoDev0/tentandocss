from flask import Blueprint, render_template, request, jsonify
import os
import logging
import pandas as pd
from datetime import datetime
import glob
import time
import traceback

# Configurar logging estruturado
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Criar blueprint
excel_dashboard_bp = Blueprint('excel_dashboard', __name__)

# Dados em memória para armazenar resultados do processamento
excel_data = {
    'employees': {},
    'months': {},
    'statistics': {
        'total_files': 0,
        'total_employees': 0,
        'total_months': 0,
        'total_records': 0
    }
}

# Cache para performance
_processing_cache = {}

@excel_dashboard_bp.route('/excel')
def excel_dashboard():
    """Rota principal da aba Excel"""
    try:
        logger.info("Acessando dashboard Excel")
        return render_template('ceo_dashboard_enhanced.html', 
                             header_only=False, 
                             excel_tab_active=True)
    except Exception as e:
        logger.error(f"Erro ao carregar dashboard Excel: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@excel_dashboard_bp.route('/api/excel/status')
def excel_status():
    """Endpoint para verificar status da aba Excel"""
    try:
        return jsonify({
            'status': 'success',
            'message': 'Aba Excel carregada com sucesso',
            'cache_size': len(_processing_cache)
        })
    except Exception as e:
        logger.error(f"Erro no status Excel: {str(e)}")
        return jsonify({'error': 'Erro interno'}), 500

@excel_dashboard_bp.route('/api/excel/load_folder', methods=['POST'])
def load_folder():
    """Endpoint para carregar pasta de arquivos Excel"""
    start_time = time.time()
    
    try:
        data = request.get_json()
        folder_path = data.get('folder_path', 'registros monitorar')
        
        logger.info(f"Iniciando processamento da pasta: {folder_path}")
        
        # Verificar se a pasta existe
        if not os.path.exists(folder_path):
            logger.warning(f"Pasta não encontrada: {folder_path}")
            return jsonify({
                'status': 'error',
                'message': f'Pasta "{folder_path}" não encontrada'
            }), 404
        
        # Verificar cache
        cache_key = f"{folder_path}_{os.path.getmtime(folder_path)}"
        if cache_key in _processing_cache:
            logger.info("Retornando dados do cache")
            return jsonify({
                'status': 'success',
                'message': 'Dados carregados do cache',
                'data': _processing_cache[cache_key],
                'statistics': _processing_cache[cache_key]['statistics'],
                'cached': True
            })
        
        # Processar arquivos Excel
        result = process_excel_files(folder_path)
        
        if result['status'] == 'success':
            # Atualizar dados em memória
            global excel_data
            excel_data.update(result['data'])
            
            # Salvar no cache
            _processing_cache[cache_key] = excel_data.copy()
            
            processing_time = time.time() - start_time
            logger.info(f"Processamento concluído em {processing_time:.2f}s")
            
            return jsonify({
                'status': 'success',
                'message': 'Arquivos processados com sucesso',
                'data': excel_data,
                'statistics': excel_data['statistics'],
                'processing_time': processing_time
            })
        else:
            return jsonify(result), 400
            
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"Erro ao carregar pasta após {processing_time:.2f}s: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            'status': 'error',
            'message': f'Erro interno: {str(e)}'
        }), 500

def process_excel_files(folder_path):
    """Processar arquivos Excel da pasta especificada"""
    start_time = time.time()
    
    try:
        # Buscar arquivos Excel
        excel_files = glob.glob(os.path.join(folder_path, "*.xlsx"))
        excel_files.extend(glob.glob(os.path.join(folder_path, "*.xls")))
        
        if not excel_files:
            logger.warning(f"Nenhum arquivo Excel encontrado em: {folder_path}")
            return {
                'status': 'error',
                'message': 'Nenhum arquivo Excel encontrado na pasta'
            }
        
        logger.info(f"Encontrados {len(excel_files)} arquivos Excel")
        
        # Limpar dados anteriores
        excel_data['employees'] = {}
        excel_data['months'] = {}
        excel_data['statistics']['total_files'] = len(excel_files)
        excel_data['statistics']['total_records'] = 0
        
        # Processar cada arquivo
        processed_files = 0
        total_records = 0
        
        for file_path in excel_files:
            try:
                file_start_time = time.time()
                file_result = extract_data_from_excel(file_path)
                
                if file_result['status'] == 'success':
                    # Mesclar dados
                    merge_excel_data(file_result['data'])
                    processed_files += 1
                    total_records += len(file_result['data'].get('records', []))
                    
                    file_time = time.time() - file_start_time
                    logger.info(f"Arquivo {os.path.basename(file_path)} processado em {file_time:.2f}s")
                else:
                    logger.warning(f"Erro ao processar {file_path}: {file_result['message']}")
                    
            except Exception as e:
                logger.error(f"Erro ao processar {file_path}: {str(e)}")
        
        # Calcular estatísticas finais
        calculate_final_statistics()
        
        total_time = time.time() - start_time
        logger.info(f"Processamento concluído: {processed_files}/{len(excel_files)} arquivos, {total_records} registros em {total_time:.2f}s")
        
        return {
            'status': 'success',
            'message': f'Processados {processed_files}/{len(excel_files)} arquivos',
            'data': excel_data,
            'processing_stats': {
                'files_processed': processed_files,
                'total_files': len(excel_files),
                'total_records': total_records,
                'processing_time': total_time
            }
        }
        
    except Exception as e:
        total_time = time.time() - start_time
        logger.error(f"Erro no processamento após {total_time:.2f}s: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return {
            'status': 'error',
            'message': f'Erro no processamento: {str(e)}'
        }

def extract_data_from_excel(file_path):
    """Extrair dados de um arquivo Excel"""
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
        
        # Processar dados específicos
        file_data = {
            'employees': {},
            'months': {},
            'records': []
        }
        
        # Tentar identificar colunas relevantes
        columns = df.columns.tolist()
        logger.info(f"Colunas encontradas: {columns}")
        
        # Mapear colunas baseado na estrutura conhecida
        date_column = None
        employee_column = None
        points_column = None
        refinery_column = None
        
        for col in columns:
            col_lower = col.lower()
            if any(keyword in col_lower for keyword in ['data', 'date', 'dia']):
                date_column = col
            elif any(keyword in col_lower for keyword in ['funcionario', 'employee', 'nome', 'name']):
                employee_column = col
            elif any(keyword in col_lower for keyword in ['ponto', 'pontos', 'valor', 'value', 'total']):
                points_column = col
            elif any(keyword in col_lower for keyword in ['refinaria', 'refinery']):
                refinery_column = col
        
        # Se não encontrou colunas específicas, usar padrões conhecidos
        if not date_column and 'Data' in columns:
            date_column = 'Data'
        if not points_column and 'Pontos' in columns:
            points_column = 'Pontos'
        if not refinery_column and 'Refinaria' in columns:
            refinery_column = 'Refinaria'
        
        # Extrair nome do funcionário do nome do arquivo
        file_name = os.path.basename(file_path)
        employee_name = file_name.replace('.xlsx', '').replace('.xls', '')
        
        # Processar cada linha do DataFrame
        for index, row in df.iterrows():
            try:
                # Pular linha de cabeçalho se necessário
                if index == 0 and isinstance(row.iloc[0], str) and 'Data' in str(row.iloc[0]):
                    continue
                
                # Extrair dados da linha
                date_value = None
                points_value = 0
                refinery_value = None
                
                # Extrair data
                if date_column and pd.notna(row[date_column]):
                    try:
                        date_value = pd.to_datetime(row[date_column])
                    except:
                        logger.warning(f"Erro ao converter data: {row[date_column]}")
                
                # Extrair pontos
                if points_column and pd.notna(row[points_column]):
                    try:
                        points_value = float(row[points_column])
                    except:
                        logger.warning(f"Erro ao converter pontos: {row[points_column]}")
                
                # Extrair refinaria
                if refinery_column and pd.notna(row[refinery_column]):
                    refinery_value = str(row[refinery_column]).strip()
                
                # Processar dados se válidos
                if employee_name and points_value > 0:
                    # Determinar mês baseado na data (26º ao 25º)
                    month_key = get_month_from_date(date_value) if date_value else 'Sem Data'
                    
                    # Adicionar ao funcionário
                    if employee_name not in file_data['employees']:
                        file_data['employees'][employee_name] = {
                            'total': 0,
                            'records': 0,
                            'refineries': {}
                        }
                    
                    file_data['employees'][employee_name]['total'] += points_value
                    file_data['employees'][employee_name]['records'] += 1
                    
                    # Adicionar refinaria
                    if refinery_value:
                        if refinery_value not in file_data['employees'][employee_name]['refineries']:
                            file_data['employees'][employee_name]['refineries'][refinery_value] = 0
                        file_data['employees'][employee_name]['refineries'][refinery_value] += points_value
                    
                    # Adicionar ao mês
                    if month_key not in file_data['months']:
                        file_data['months'][month_key] = {}
                    
                    if employee_name not in file_data['months'][month_key]:
                        file_data['months'][month_key][employee_name] = {
                            'total': 0,
                            'records': 0
                        }
                    
                    file_data['months'][month_key][employee_name]['total'] += points_value
                    file_data['months'][month_key][employee_name]['records'] += 1
                    
                    # Adicionar registro
                    file_data['records'].append({
                        'employee': employee_name,
                        'date': date_value,
                        'points': points_value,
                        'month': month_key,
                        'refinery': refinery_value
                    })
                
            except Exception as e:
                logger.warning(f"Erro ao processar linha {index}: {str(e)}")
                continue
        
        logger.info(f"Processado arquivo com {len(file_data['records'])} registros válidos")
        
        return {
            'status': 'success',
            'data': file_data,
            'message': f'Processado com {len(file_data["records"])} registros válidos'
        }
        
    except Exception as e:
        logger.error(f"Erro ao extrair dados de {file_path}: {str(e)}")
        return {
            'status': 'error',
            'message': f'Erro ao ler arquivo: {str(e)}'
        }

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
            # Permanecer no mês atual
            target_month = month
            target_year = year
        else:
            # Ir para o mês anterior
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

def merge_excel_data(file_data):
    """Mesclar dados de um arquivo com os dados globais"""
    try:
        # Mesclar funcionários
        for employee, data in file_data.get('employees', {}).items():
            if employee not in excel_data['employees']:
                excel_data['employees'][employee] = data
            else:
                # Somar dados existentes
                excel_data['employees'][employee]['total'] += data.get('total', 0)
        
        # Mesclar meses
        for month, data in file_data.get('months', {}).items():
            if month not in excel_data['months']:
                excel_data['months'][month] = data
            else:
                # Mesclar dados do mês
                for employee, employee_data in data.items():
                    if employee not in excel_data['months'][month]:
                        excel_data['months'][month][employee] = employee_data
                    else:
                        excel_data['months'][month][employee]['total'] += employee_data.get('total', 0)
        
        # Adicionar registros
        excel_data['statistics']['total_records'] += file_data.get('records', 0)
        
    except Exception as e:
        logger.error(f"Erro ao mesclar dados: {str(e)}")

def calculate_final_statistics():
    """Calcular estatísticas finais"""
    try:
        excel_data['statistics']['total_employees'] = len(excel_data['employees'])
        excel_data['statistics']['total_months'] = len(excel_data['months'])
        
        # Calcular estatísticas adicionais
        total_points = 0
        total_records = 0
        employee_stats = {}
        
        # Calcular totais por funcionário
        for employee, data in excel_data['employees'].items():
            total_points += data.get('total', 0)
            total_records += data.get('records', 0)
            
            # Estatísticas por funcionário
            employee_stats[employee] = {
                'total_points': data.get('total', 0),
                'total_records': data.get('records', 0),
                'average_points': data.get('total', 0) / max(data.get('records', 1), 1),
                'refineries': data.get('refineries', {})
            }
        
        # Calcular estatísticas por mês
        month_stats = {}
        for month, data in excel_data['months'].items():
            month_total = 0
            month_records = 0
            for employee_data in data.values():
                month_total += employee_data.get('total', 0)
                month_records += employee_data.get('records', 0)
            
            month_stats[month] = {
                'total_points': month_total,
                'total_records': month_records,
                'average_points': month_total / max(month_records, 1)
            }
        
        # Adicionar estatísticas detalhadas
        excel_data['statistics'].update({
            'total_points': total_points,
            'total_records': total_records,
            'average_points_per_record': total_points / max(total_records, 1),
            'employee_stats': employee_stats,
            'month_stats': month_stats,
            'top_employee': max(employee_stats.items(), key=lambda x: x[1]['total_points'])[0] if employee_stats else None,
            'top_month': max(month_stats.items(), key=lambda x: x[1]['total_points'])[0] if month_stats else None
        })
        
        logger.info(f"Estatísticas finais: {excel_data['statistics']}")
        
    except Exception as e:
        logger.error(f"Erro ao calcular estatísticas: {str(e)}")

@excel_dashboard_bp.route('/api/excel/data')
def get_excel_data():
    """Endpoint para obter dados processados"""
    try:
        return jsonify({
            'status': 'success',
            'data': excel_data
        })
    except Exception as e:
        logger.error(f"Erro ao obter dados: {str(e)}")
        return jsonify({'error': 'Erro interno'}), 500 