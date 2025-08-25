from models import db, Employee, Entry
from app import app
from utils.calculations import get_week_dates, calculate_weekly_progress
from datetime import datetime
from sqlalchemy import func

with app.app_context():
    print('=== ANÁLISE COMPLETA DO PROBLEMA DE MAPEAMENTO DE SEMANAS ===')
    print(f'Data atual: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    
    # 1. Buscar Maurício
    mauricio = Employee.query.filter(Employee.real_name == 'Maurício').first()
    if not mauricio:
        mauricio = Employee.query.filter(Employee.name == 'Maurício').first()
    
    if not mauricio:
        print('❌ Maurício não encontrado!')
        exit()
    
    print(f'✅ Maurício encontrado - ID: {mauricio.id}, Nome: {mauricio.real_name}')
    
    # 2. Verificar TODOS os registros do Maurício
    print('\n=== TODOS OS REGISTROS DO MAURÍCIO ===')
    all_entries = Entry.query.filter(Entry.employee_id == mauricio.id).all()
    print(f'Total de registros: {len(all_entries)}')
    
    total_points = 0
    for entry in all_entries:
        print(f'  - ID: {entry.id}, Data: {entry.date}, Pontos: {entry.points}')
        total_points += entry.points
    
    print(f'\n💯 TOTAL GERAL DE PONTOS: {total_points}')
    
    # 3. Testar TODAS as semanas (1-5)
    print('\n=== ANÁLISE DE TODAS AS SEMANAS ===')
    for week_num in range(1, 6):
        print(f'\n--- SEMANA {week_num} ---')
        
        try:
            start_date, end_date = get_week_dates(str(week_num))
            print(f'Período: {start_date} até {end_date}')
            
            # Consulta com func.date() (corrigida)
            week_entries = Entry.query.filter(
                Entry.employee_id == mauricio.id,
                func.date(Entry.date) >= start_date,
                func.date(Entry.date) <= end_date
            ).all()
            
            week_points = sum(entry.points for entry in week_entries)
            print(f'Registros encontrados: {len(week_entries)}')
            print(f'Pontos da semana: {week_points}')
            
            if week_entries:
                for entry in week_entries:
                    print(f'  - Data: {entry.date}, Pontos: {entry.points}')
            
            # Testar também a função calculate_weekly_progress
            calc_result = calculate_weekly_progress(week_num, mauricio.id)
            calc_total = sum(calc_result.values()) if calc_result else 0
            print(f'calculate_weekly_progress resultado: {calc_total}')
            
            if week_points != calc_total:
                print(f'⚠️  DISCREPÂNCIA: Manual={week_points}, Função={calc_total}')
            
        except Exception as e:
            print(f'❌ Erro na semana {week_num}: {str(e)}')
    
    # 4. Verificar especificamente o registro de 523 pontos
    print('\n=== ANÁLISE DO REGISTRO DE 523 PONTOS ===')
    entry_523 = Entry.query.filter(
        Entry.employee_id == mauricio.id,
        Entry.points == 523
    ).first()
    
    if entry_523:
        print(f'✅ Registro de 523 pontos encontrado:')
        print(f'  - ID: {entry_523.id}')
        print(f'  - Data: {entry_523.date}')
        print(f'  - Pontos: {entry_523.points}')
        
        # Verificar em qual semana este registro deveria estar
        entry_date = entry_523.date
        if isinstance(entry_date, str):
            entry_date_str = entry_date[:10]  # Pegar apenas YYYY-MM-DD
        else:
            entry_date_str = entry_date.strftime('%Y-%m-%d')
        
        print(f'  - Data formatada: {entry_date_str}')
        
        # Testar em qual semana esta data se encaixa
        print('\n🔍 TESTANDO EM QUAL SEMANA ESTA DATA SE ENCAIXA:')
        for week_num in range(1, 6):
            start_date, end_date = get_week_dates(str(week_num))
            if start_date <= entry_date_str <= end_date:
                print(f'  ✅ Data {entry_date_str} está na SEMANA {week_num} ({start_date} - {end_date})')
            else:
                print(f'  ❌ Data {entry_date_str} NÃO está na SEMANA {week_num} ({start_date} - {end_date})')
    
    else:
        print('❌ Registro de 523 pontos não encontrado!')
    
    # 5. Verificar data de hoje especificamente
    print('\n=== VERIFICAÇÃO DA DATA DE HOJE ===')
    today_str = '2025-08-25'
    print(f'Data de hoje: {today_str}')
    
    for week_num in range(1, 6):
        start_date, end_date = get_week_dates(str(week_num))
        if start_date <= today_str <= end_date:
            print(f'  ✅ Hoje ({today_str}) deveria estar na SEMANA {week_num}')
        else:
            print(f'  ❌ Hoje ({today_str}) NÃO está na SEMANA {week_num} ({start_date} - {end_date})')
    
    print('\n=== FIM DA ANÁLISE ===')