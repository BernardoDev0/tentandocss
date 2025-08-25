from models import db, Employee, Entry
from app import app
from utils.data_processing import get_weekly_evolution_data
from utils.calculations import get_week_dates

with app.app_context():
    print('=== ANÁLISE DETALHADA DO PROBLEMA ===')
    
    # Verificar registros por funcionário
    employees = Employee.query.all()
    for emp in employees:
        count = Entry.query.filter(Entry.employee_id == emp.id).count()
        print(f'Funcionário {emp.real_name} (ID: {emp.id}): {count} registros')
        
        # Mostrar alguns registros deste funcionário
        entries = Entry.query.filter(Entry.employee_id == emp.id).limit(3).all()
        for entry in entries:
            print(f'  - Data: {entry.date}, Pontos: {entry.points}')
    
    print('\n=== VERIFICAÇÃO ESPECÍFICA DO RODRIGO ===')
    rodrigo = Employee.query.filter(Employee.real_name == 'Rodrigo').first()
    if rodrigo:
        print(f'Rodrigo encontrado - ID: {rodrigo.id}, Nome: {rodrigo.real_name}')
        rodrigo_entries = Entry.query.filter(Entry.employee_id == rodrigo.id).all()
        print(f'Total de registros do Rodrigo: {len(rodrigo_entries)}')
        
        if rodrigo_entries:
            print('Registros do Rodrigo:')
            for entry in rodrigo_entries[:5]:  # Mostrar apenas os primeiros 5
                print(f'  - ID: {entry.id}, Data: {entry.date}, Pontos: {entry.points}')
    else:
        print('Rodrigo não encontrado!')
    
    print('\n=== VERIFICAÇÃO DA LÓGICA DE PROCESSAMENTO ===')
    # Simular o processamento manual
    from utils.calculations import get_week_dates
    
    for week in range(1, 6):
        start_date, end_date = get_week_dates(str(week))
        print(f'\nSemana {week}: {start_date} até {end_date}')
        
        for emp in employees:
            # Buscar registros desta semana para este funcionário
            entries = Entry.query.filter(
                Entry.employee_id == emp.id,
                Entry.date >= start_date,
                Entry.date <= end_date
            ).all()
            
            total_points = sum(entry.points for entry in entries)
            print(f'  {emp.real_name}: {len(entries)} registros, {total_points} pontos')
            
            if entries:
                for entry in entries:
                    entry_date_str = entry.date.strftime('%Y-%m-%d') if hasattr(entry.date, 'strftime') else str(entry.date)[:10]
                    print(f'    - {entry_date_str}: {entry.points} pontos')