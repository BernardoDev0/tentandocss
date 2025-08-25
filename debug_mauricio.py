from models import db, Employee, Entry
from app import app
from utils.calculations import get_week_dates
from datetime import datetime
from sqlalchemy import func

with app.app_context():
    print('=== ANÁLISE ESPECÍFICA DO MAURÍCIO ===')
    
    # Buscar Maurício no banco
    mauricio = Employee.query.filter(Employee.real_name == 'Maurício').first()
    if not mauricio:
        mauricio = Employee.query.filter(Employee.name == 'Maurício').first()
    
    if mauricio:
        print(f'✅ Maurício encontrado - ID: {mauricio.id}, Nome: {mauricio.real_name}')
        
        # Buscar TODOS os registros do Maurício
        mauricio_entries = Entry.query.filter(Entry.employee_id == mauricio.id).all()
        print(f'📊 Total de registros do Maurício: {len(mauricio_entries)}')
        
        if mauricio_entries:
            print('\n📋 TODOS OS REGISTROS DO MAURÍCIO:')
            total_points = 0
            for entry in mauricio_entries:
                print(f'  - ID: {entry.id}, Data: {entry.date}, Pontos: {entry.points}, Refinaria: {entry.refinery}')
                total_points += entry.points
            
            print(f'\n💯 TOTAL DE PONTOS DO MAURÍCIO: {total_points}')
            
            # Verificar registros de hoje (25/08/2025)
            today = '2025-08-25'
            today_entries = Entry.query.filter(
                Entry.employee_id == mauricio.id,
                func.date(Entry.date) == today
            ).all()
            
            print(f'\n📅 REGISTROS DE HOJE ({today}):')
            today_points = 0
            for entry in today_entries:
                print(f'  - Data: {entry.date}, Pontos: {entry.points}')
                today_points += entry.points
            
            print(f'💯 PONTOS DE HOJE: {today_points}')
            
            # Verificar Semana 5 (23-25/08/2025)
            start_date, end_date = get_week_dates('5')
            print(f'\n📊 SEMANA 5: {start_date} até {end_date}')
            
            week5_entries = Entry.query.filter(
                Entry.employee_id == mauricio.id,
                Entry.date >= start_date,
                Entry.date <= end_date
            ).all()
            
            print(f'📋 REGISTROS DA SEMANA 5:')
            week5_points = 0
            for entry in week5_entries:
                print(f'  - Data: {entry.date}, Pontos: {entry.points}')
                week5_points += entry.points
            
            print(f'💯 PONTOS DA SEMANA 5: {week5_points}')
            
            # Verificar se há registros com string de data simples
            print('\n🔍 VERIFICANDO FORMATOS DE DATA:')
            for entry in mauricio_entries:
                date_str = str(entry.date)
                if '2025-08-25' in date_str:
                    print(f'  ⚠️  ENCONTRADO REGISTRO COM 25/08: {entry.date} - {entry.points} pontos')
        
    else:
        print('❌ Maurício não encontrado no banco!')
        
        # Listar todos os funcionários
        print('\n👥 FUNCIONÁRIOS NO BANCO:')
        employees = Employee.query.all()
        for emp in employees:
            print(f'  - ID: {emp.id}, Nome: {emp.real_name}, Username: {emp.username}')