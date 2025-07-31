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

def get_custom_month(date_value):
    """
    Retorna o mês no formato MM/YYYY considerando o mês da empresa (26 ao 25).
    Lógica: Se dia >= 26, pertence ao mês seguinte. Se dia < 26, pertence ao mês atual.
    Exemplo: Abril vai de 26/03 até 25/04
    """
    try:
        if not date_value or pd.isna(date_value):
            return 'Sem Data'
        
        # Converter para datetime se necessário
        if isinstance(date_value, str):
            date_value = pd.to_datetime(date_value)
        
        day = date_value.day
        month = date_value.month
        year = date_value.year
        
        # LÓGICA CORRETA: Se dia >= 26, pertence ao mês seguinte
        if day >= 26:
            if month == 12:
                target_month = 1
                target_year = year + 1
            else:
                target_month = month + 1
                target_year = year
        else:
            target_month = month
            target_year = year
        
        month_key = f"{target_month:02d}/{target_year}"
        logger.info(f"📅 {date_value} (dia {day}) → {month_key}")
        
        return month_key
        
    except Exception as e:
        logger.error(f"Erro ao converter data {date_value}: {str(e)}")
        return 'Sem Data'

# Manter a função antiga para compatibilidade, mas usar a nova
def get_month_from_date(date_value):
    """Alias para get_custom_month - manter compatibilidade"""
    return get_custom_month(date_value)

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
        
        # ✅ ADICIONAR: Set para evitar registros duplicados
        processed_records = set()
        
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
                
                # ✅ RESTAURAR: Processamento de registros individuais
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
                    
                    # ✅ ADICIONAR: Verificar duplicação
                    record_key = f"{date_value}_{points_value}_{employee_name}"
                    if record_key in processed_records:
                        logger.warning(f"⚠️ Registro duplicado no arquivo: {record_key}")
                        continue
                    processed_records.add(record_key)
                    
                    # ✅ REMOVER: Verificação de pontos suspeitos (usuário confirmou que são válidos)
                    # if points_value > 2000:
                    #     logger.warning(f"⚠️ Pontos muito altos detectados: {points_value} para {employee_name} em {date_value}")
                    #     # Verificar se é realmente válido
                    #     if points_value > 5000:
                    #         logger.warning(f"❌ Pontos extremamente altos ignorados: {points_value}")
                    #         continue
                    
                    logger.info(f"📊 Processando linha {index}: {employee_name} - {points_value} pontos - {month_key}")
                    
                    # Adicionar ao funcionário
                    if employee_name not in file_data['employees']:
                        file_data['employees'][employee_name] = {
                            'total': 0,
                            'records': 0,
                            'refineries': {},
                            'months': {}
                        }
                        logger.info(f"✅ Novo funcionário criado: {employee_name}")
                    
                    old_total = file_data['employees'][employee_name]['total']
                    file_data['employees'][employee_name]['total'] += points_value
                    file_data['employees'][employee_name]['records'] += 1
                    logger.info(f"📊 Total atualizado: {old_total} + {points_value} = {file_data['employees'][employee_name]['total']}")
                    
                    # Adicionar refinaria
                    if refinery_value:
                        if refinery_value not in file_data['employees'][employee_name]['refineries']:
                            file_data['employees'][employee_name]['refineries'][refinery_value] = 0
                        file_data['employees'][employee_name]['refineries'][refinery_value] += points_value
                        logger.info(f"🏭 Refinaria atualizada: {refinery_value} = {file_data['employees'][employee_name]['refineries'][refinery_value]}")
                    
                    # Adicionar registro individual
                    record_data = {
                        'employee': employee_name,
                        'date': date_value,
                        'points': points_value,
                        'month': month_key,
                        'refinery': refinery_value
                    }
                    file_data['records'].append(record_data)
                    logger.info(f"📋 Registro adicionado: {record_data}")
                else:
                    logger.warning(f"❌ Dados inválidos na linha {index}: employee={employee_name}, points={points_value}")
                
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
        logger.info(f"🔍 === DEBUG: MESCLANDO DADOS ===")
        logger.info(f"📊 Dados do arquivo: {file_data}")
        
        # ✅ SIMPLIFICAÇÃO: Processar apenas registros individuais
        for record in file_data.get('records', []):
            employee_name = record.get('employee')
            logger.info(f"📋 Processando registro: {record}")
            
            if employee_name not in excel_data['employees']:
                logger.info(f"✅ Novo funcionário: {employee_name}")
                excel_data['employees'][employee_name] = {
                    'totalPoints': 0,
                    'totalRecords': 0,
                    'records': [],
                    'months': {}
                }
            
            # ✅ ADICIONAR: Verificar duplicação
            record_key = f"{record.get('date')}_{record.get('points')}_{employee_name}"
            existing_records = excel_data['employees'][employee_name]['records']
            
            # Verificar se registro já existe
            is_duplicate = False
            for existing_record in existing_records:
                existing_key = f"{existing_record.get('date')}_{existing_record.get('points')}_{employee_name}"
                if record_key == existing_key:
                    logger.warning(f"⚠️ Registro duplicado detectado: {record_key}")
                    is_duplicate = True
                    break
            
            # ✅ ADICIONAR: Verificar duplicação por data e hora (mesmo dia, mesma hora)
            if not is_duplicate:
                for existing_record in existing_records:
                    if (existing_record.get('date') == record.get('date') and 
                        existing_record.get('points') == record.get('points')):
                        logger.warning(f"⚠️ Registro duplicado por data/hora: {record.get('date')} - {record.get('points')} pontos")
                        is_duplicate = True
                        break
            
            if not is_duplicate:
                # Adicionar registro individual
                excel_data['employees'][employee_name]['records'].append({
                    'date': record.get('date'),
                    'points': record.get('points'),
                    'refinery': record.get('refinery'),
                    'month': record.get('month')
                })
                logger.info(f"✅ Registro adicionado para {employee_name}")
            else:
                logger.info(f"⏭️ Registro duplicado ignorado: {employee_name}")
        
        logger.info(f"✅ Mesclagem concluída")
        
    except Exception as e:
        logger.error(f"Erro ao mesclar dados: {str(e)}")

def calculate_final_statistics():
    """Calcular estatísticas finais"""
    try:
        excel_data['statistics']['total_employees'] = len(excel_data['employees'])
        excel_data['statistics']['total_months'] = len(excel_data['months'])
        
        # ✅ CORREÇÃO: Calcular total de pontos a partir dos registros individuais
        total_points = 0
        total_records = 0
        
        logger.info(f"🔍 === DEBUG: CALCULANDO ESTATÍSTICAS FINAIS ===")
        
        for employee_name, employee_data in excel_data['employees'].items():
            logger.info(f"\n👤 === FUNCIONÁRIO: {employee_name} ===")
            
            # Calcular total a partir dos registros individuais
            employee_points = 0
            employee_records = len(employee_data.get('records', []))
            
            logger.info(f"📋 Registros encontrados: {employee_records}")
            
            # ✅ ADICIONAR: Debug detalhado para cada registro
            for i, record in enumerate(employee_data.get('records', [])):
                points = record.get('points', 0)
                date = record.get('date')
                month = record.get('month')
                
                logger.info(f"  📋 Registro {i+1}: {date} - {points} pontos - {month}")
                employee_points += points
                logger.info(f"  📊 Subtotal {employee_name}: {employee_points} pontos")
            
            # Atualizar totalPoints com o valor calculado
            old_total = employee_data.get('totalPoints', 0)
            employee_data['totalPoints'] = employee_points
            employee_data['totalRecords'] = employee_records
            
            logger.info(f"📊 {employee_name}: {old_total} → {employee_points} pontos ({employee_records} registros)")
            
            total_points += employee_points
            total_records += employee_records
            
            logger.info(f"📊 Total acumulado: {total_points} pontos")
        
        excel_data['statistics']['total_points'] = total_points
        excel_data['statistics']['total_records'] = total_records
        
        # Calcular média por registro
        if total_records > 0:
            excel_data['statistics']['average_points_per_record'] = total_points / total_records
        else:
            excel_data['statistics']['average_points_per_record'] = 0
        
        logger.info(f"\n📊 === RESUMO FINAL ===")
        logger.info(f"📊 Total de pontos: {total_points}")
        logger.info(f"📊 Total de registros: {total_records}")
        logger.info(f"📊 Média por registro: {excel_data['statistics']['average_points_per_record']}")
        logger.info(f"Estatísticas finais: {excel_data['statistics']}")
        
    except Exception as e:
        logger.error(f"Erro ao calcular estatísticas: {str(e)}")

def clear_all_data():
    """Limpar todos os dados em memória"""
    global excel_data
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
    logger.info("🧹 Dados limpos com sucesso")

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
        
        logger.info(f"🔍 === DEBUG: CARREGANDO PASTA ===")
        logger.info(f"📁 Pasta: {folder_path}")
        
        # Verificar se a pasta existe
        if not os.path.exists(folder_path):
            return jsonify({
                'status': 'error',
                'message': f'Pasta "{folder_path}" não encontrada'
            }), 404
        
        # ✅ CORREÇÃO: Limpar dados completamente
        clear_all_data()
        
        # Contar e processar arquivos Excel
        excel_files = []
        logger.info(f"🔍 === BUSCANDO ARQUIVOS EXCEL ===")
        
        for root, dirs, files in os.walk(folder_path):
            logger.info(f"📁 Diretório: {root}")
            logger.info(f"📁 Subdiretórios: {dirs}")
            logger.info(f"📄 Arquivos: {files}")
            
            for file in files:
                if file.endswith(('.xlsx', '.xls')):
                    file_path = os.path.join(root, file)
                    excel_files.append(file_path)
                    logger.info(f"✅ Arquivo Excel encontrado: {file_path}")
        
        logger.info(f"📊 Total de arquivos Excel encontrados: {len(excel_files)}")
        
        # ✅ ADICIONAR: Verificar se há arquivos duplicados
        file_names = [os.path.basename(f) for f in excel_files]
        unique_names = set(file_names)
        if len(file_names) != len(unique_names):
            logger.warning(f"⚠️ ARQUIVOS DUPLICADOS DETECTADOS!")
            logger.warning(f"📊 Arquivos encontrados: {file_names}")
            logger.warning(f"📊 Arquivos únicos: {list(unique_names)}")
        
        excel_data['statistics']['total_files'] = len(excel_files)
        
        # Processar cada arquivo
        processed_files = 0
        processed_file_names = set()  # ✅ ADICIONAR: Para evitar duplicação
        
        for file_path in excel_files:
            try:
                file_name = os.path.basename(file_path)
                
                # ✅ ADICIONAR: Verificar se arquivo já foi processado
                if file_name in processed_file_names:
                    logger.warning(f"⚠️ Arquivo já processado: {file_name}")
                    continue
                processed_file_names.add(file_name)
                
                logger.info(f"\n📄 === PROCESSANDO ARQUIVO ===")
                logger.info(f"📄 Arquivo: {file_name}")
                logger.info(f"📄 Caminho completo: {file_path}")
                
                file_result = extract_data_from_excel(file_path)
                if file_result['status'] == 'success':
                    logger.info(f"✅ Arquivo processado com sucesso")
                    logger.info(f"📊 Dados extraídos: {file_result['data']}")
                    
                    merge_excel_data(file_result['data'])
                    processed_files += 1
                    logger.info(f"✅ Arquivo mesclado: {file_name}")
                else:
                    logger.warning(f"❌ Erro ao processar {file_path}: {file_result['message']}")
            except Exception as e:
                logger.error(f"❌ Erro ao processar {file_path}: {str(e)}")
        
        # ✅ ADICIONAR: Limpar registros duplicados específicos
        # clean_duplicate_records() # Removido
        
        # ✅ ADICIONAR: Remover TODOS os dados de março
        # clean_march_data() # Removido
        
        # ✅ ADICIONAR: Forçar apenas dados de abril a julho
        # force_april_to_july_only() # Removido
        
        # ✅ ADICIONAR: Reclassificar março como abril
        # reclassify_march_as_april() # Removido
        
        logger.info(f"\n📊 === RESUMO DO PROCESSAMENTO ===")
        logger.info(f"📄 Arquivos encontrados: {len(excel_files)}")
        logger.info(f"✅ Arquivos processados: {processed_files}")
        logger.info(f"📊 Funcionários: {len(excel_data['employees'])}")
        logger.info(f"📋 Registros totais: {excel_data['statistics']['total_records']}")
        
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