from models import db, Employee, Entry
from app import app
from utils.calculations import get_week_dates, calculate_weekly_progress
from datetime import datetime
from sqlalchemy import func

with app.app_context():
    print('=== DEBUG PROBLEMA SEMANA 5 ===\n')
    
    # 1. Verificar registros de hoje
    today = datetime.now().strftime('%Y-%m-%d')
    print(f'Data de hoje: {today}')
    
    # Buscar Rodrigo
    rodrigo = Employee.query.filter(Employee.real_name == 'Rodrigo').first()
    if not rodrigo:
        print('❌ Rodrigo não encontrado!')
        exit()
    
    print(f'Funcionário: {rodrigo.real_name} (ID: {rodrigo.id})')
    
    # 2. Verificar registros de hoje no banco
    print('\n=== REGISTROS DE HOJE NO BANCO ===')
    today_entries = Entry.query.filter(
        Entry.employee_id == rodrigo.id,
        Entry.date.like(f'{today}%')  # Buscar por data que começa com hoje
    ).all()
    
    print(f'Registros encontrados: {len(today_entries)}')
    total_today = 0
    for entry in today_entries:
        print(f'  - Data: {entry.date}, Pontos: {entry.points}')
        total_today += entry.points
    
    print(f'Total de pontos hoje: {total_today}')
    
    # 3. Verificar datas da Semana 5
    print('\n=== DATAS DA SEMANA 5 ===')
    week5_start, week5_end = get_week_dates('5')
    print(f'Semana 5: {week5_start} até {week5_end}')
    print(f'Hoje ({today}) está no intervalo? {week5_start <= today <= week5_end}')
    
    # 4. Testar consulta da função calculate_weekly_progress
    print('\n=== CONSULTA ATUAL (PROBLEMÁTICA) ===')
    problematic_entries = Entry.query.filter(
        Entry.employee_id == rodrigo.id,
        Entry.date >= week5_start,
        Entry.date <= week5_end
    ).all()
    
    print(f'Registros encontrados com consulta atual: {len(problematic_entries)}')
    for entry in problematic_entries:
        print(f'  - Data: {entry.date}, Pontos: {entry.points}')
    
    # 5. Testar consulta corrigida
    print('\n=== CONSULTA CORRIGIDA ===')
    corrected_entries = Entry.query.filter(
        Entry.employee_id == rodrigo.id,
        func.date(Entry.date) >= week5_start,
        func.date(Entry.date) <= week5_end
    ).all()
    
    print(f'Registros encontrados com consulta corrigida: {len(corrected_entries)}')
    total_corrected = 0
    for entry in corrected_entries:
        print(f'  - Data: {entry.date}, Pontos: {entry.points}')
        total_corrected += entry.points
    
    print(f'Total de pontos Semana 5 (corrigido): {total_corrected}')
    
    # 6. Comparar com resultado atual da função
    print('\n=== COMPARAÇÃO ===')
    current_result = calculate_weekly_progress(rodrigo.id, 5)
    current_total = sum(current_result.values()) if current_result else 0
    
    print(f'Resultado atual calculate_weekly_progress: {current_total}')
    print(f'Resultado esperado (corrigido): {total_corrected}')
    
    if current_total != total_corrected:
        print('\n❌ PROBLEMA CONFIRMADO: A função não está usando func.date() para comparar datas!')
        print('\n🔧 SOLUÇÃO: Modificar calculate_weekly_progress para usar func.date() nas comparações')
    else:
        print('\n✅ Função está funcionando corretamente')