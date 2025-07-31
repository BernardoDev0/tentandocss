from flask import Blueprint, render_template, request, jsonify
import os
import logging
import pandas as pd
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Criar blueprint
excel_dashboard_simple_bp = Blueprint('excel_dashboard_simple', __name__)

# Dados em memória
excel_data = {
    'employees': {},
    'months': {},
    'statistics': {
        'total_files': 0,
        'total_employees': 0,
        'total_months': 0,
        'total_records': 0,
        'total_points': 0
    }
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
        
        # Mapear colunas baseado na estrutura conhecida
        date_column = None
        points_column = None
        refinery_column = None
        
        for col in columns:
            col_lower = col.lower()
            if any(keyword in col_lower for keyword in ['data', 'date', 'dia']):
                date_column = col
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
        
        # Processar cada linha do DataFrame
        for index, row in df.iterrows():
            try:
                # Pular linha de cabeçalho se necessário
                if index == 0 and isinstance(row.iloc[0], str) and 'Data' in str(row.iloc[0]):
                    continue
                
                # Pular linha de total se existir
                if any(col and pd.notna(row[col]) and str(row[col]).lower() == 'total' for col in [date_column, points_column]):
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

def merge_excel_data(file_data):
    """Mesclar dados de um arquivo com os dados globais"""
    try:
        # Mesclar funcionários
        for employee, data in file_data.get('employees', {}).items():
            if employee not in excel_data['employees']:
                excel_data['employees'][employee] = {
                    'totalPoints': data.get('total', 0),
                    'totalRecords': data.get('records', 0),
                    'records': [],  # Array de registros individuais
                    'months': {}    # Dados por mês
                }
            else:
                # Somar dados existentes
                excel_data['employees'][employee]['totalPoints'] += data.get('total', 0)
                excel_data['employees'][employee]['totalRecords'] += data.get('records', 0)
        
        # Mesclar registros individuais
        for record in file_data.get('records', []):
            employee_name = record.get('employee')
            if employee_name in excel_data['employees']:
                # Adicionar registro individual
                excel_data['employees'][employee_name]['records'].append({
                    'date': record.get('date'),
                    'points': record.get('points'),
                    'refinery': record.get('refinery'),
                    'month': record.get('month')
                })
        
        # Mesclar dados por mês
        for month, month_data in file_data.get('months', {}).items():
            for employee, employee_data in month_data.items():
                if employee in excel_data['employees']:
                    if 'months' not in excel_data['employees'][employee]:
                        excel_data['employees'][employee]['months'] = {}
                    
                    if month not in excel_data['employees'][employee]['months']:
                        excel_data['employees'][employee]['months'][month] = {
                            'points': 0,
                            'records': 0
                        }
                    
                    excel_data['employees'][employee]['months'][month]['points'] += employee_data.get('total', 0)
                    excel_data['employees'][employee]['months'][month]['records'] += employee_data.get('records', 0)
        
        # Adicionar registros
        excel_data['statistics']['total_records'] += len(file_data.get('records', []))
        
    except Exception as e:
        logger.error(f"Erro ao mesclar dados: {str(e)}")

def calculate_final_statistics():
    """Calcular estatísticas finais"""
    try:
        excel_data['statistics']['total_employees'] = len(excel_data['employees'])
        excel_data['statistics']['total_months'] = len(excel_data['months'])
        
        # Calcular total de pontos
        total_points = 0
        for employee_data in excel_data['employees'].values():
            total_points += employee_data.get('totalPoints', 0)
        
        excel_data['statistics']['total_points'] = total_points
        
        # Calcular média por registro
        if excel_data['statistics']['total_records'] > 0:
            excel_data['statistics']['average_points_per_record'] = total_points / excel_data['statistics']['total_records']
        else:
            excel_data['statistics']['average_points_per_record'] = 0
        
        logger.info(f"Estatísticas finais: {excel_data['statistics']}")
        
    except Exception as e:
        logger.error(f"Erro ao calcular estatísticas: {str(e)}")

@excel_dashboard_simple_bp.route('/excel')
def excel_dashboard():
    """Rota principal da aba Excel"""
    try:
        logger.info("Acessando dashboard Excel")
        return render_template('ceo_dashboard_enhanced.html', 
                             header_only=False, 
                             excel_tab_active=True)
    except Exception as e:
        logger.error(f"Erro ao carregar dashboard Excel: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@excel_dashboard_simple_bp.route('/api/excel/status')
def excel_status():
    """Endpoint para verificar status da aba Excel"""
    try:
        return jsonify({
            'status': 'success',
            'message': 'Aba Excel carregada com sucesso'
        })
    except Exception as e:
        logger.error(f"Erro no status Excel: {str(e)}")
        return jsonify({'error': 'Erro interno'}), 500

@excel_dashboard_simple_bp.route('/api/excel/load_folder', methods=['POST'])
def load_folder():
    """Endpoint para carregar pasta de arquivos Excel"""
    try:
        data = request.get_json()
        folder_path = data.get('folder_path', 'registros monitorar')
        
        logger.info(f"Processando pasta: {folder_path}")
        
        # Verificar se a pasta existe
        if not os.path.exists(folder_path):
            return jsonify({
                'status': 'error',
                'message': f'Pasta "{folder_path}" não encontrada'
            }), 404
        
        # Limpar dados anteriores
        excel_data['employees'] = {}
        excel_data['months'] = {}
        excel_data['statistics']['total_files'] = 0
        excel_data['statistics']['total_records'] = 0
        excel_data['statistics']['total_points'] = 0
        
        # Contar e processar arquivos Excel
        excel_files = []
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.endswith(('.xlsx', '.xls')):
                    excel_files.append(os.path.join(root, file))
        
        excel_data['statistics']['total_files'] = len(excel_files)
        
        # Processar cada arquivo
        processed_files = 0
        for file_path in excel_files:
            try:
                file_result = extract_data_from_excel(file_path)
                if file_result['status'] == 'success':
                    merge_excel_data(file_result['data'])
                    processed_files += 1
                    logger.info(f"Arquivo processado: {os.path.basename(file_path)}")
                else:
                    logger.warning(f"Erro ao processar {file_path}: {file_result['message']}")
            except Exception as e:
                logger.error(f"Erro ao processar {file_path}: {str(e)}")
        
        # Calcular estatísticas finais
        calculate_final_statistics()
        
        return jsonify({
            'status': 'success',
            'message': f'Processados {processed_files}/{len(excel_files)} arquivos',
            'data': excel_data,
            'statistics': excel_data['statistics']
        })
            
    except Exception as e:
        logger.error(f"Erro ao carregar pasta: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Erro interno: {str(e)}'
        }), 500 