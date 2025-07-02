from datetime import datetime, timedelta
from sqlalchemy import func
from models import db, Employee, Entry
from utils.calculations import get_week_dates, get_current_week
from flask import current_app

def get_weekly_progress_data():
    """Retorna dados de progresso semanal para gráficos"""
    try:
        employees = Employee.query.all()
        current_app.logger.info(f"Funcionários encontrados: {len(employees)}")
        
        if not employees:
            return {'labels': [], 'datasets': []}
        
        # Últimas 5 semanas - ATUALIZADO
        current_week = get_current_week()
        weeks = []
        
        # Gerar semanas de 1 a 5 sempre, independente da semana atual
        for i in range(1, 6):  # Mudança: de range(1, 5) para range(1, 6)
            weeks.append(str(i))
        
        current_app.logger.info(f"Semanas para análise: {weeks}")
        
        datasets = []
        
        for employee in employees:
            if not employee or not employee.real_name:
                continue
                
            data = []
            has_data = False
            
            for week in weeks:
                try:
                    start_date, end_date = get_week_dates(week)
                    current_app.logger.info(f"Buscando dados de {employee.real_name} para semana {week}: {start_date} até {end_date}")
                    
                    # Buscar entradas diretamente
                    entries = Entry.query.filter(
                        Entry.employee_id == employee.id,
                        Entry.date >= start_date,
                        Entry.date <= end_date
                    ).all()
                    
                    weekly_points = sum(entry.points for entry in entries)
                    current_app.logger.info(f"Pontos encontrados para {employee.real_name} semana {week}: {weekly_points}")
                    
                    data.append(float(weekly_points))
                    
                    if weekly_points > 0:
                        has_data = True
                        
                except Exception as e:
                    current_app.logger.error(f"Erro ao processar semana {week} para {employee.real_name}: {str(e)}")
                    data.append(0.0)
            
            # Adicionar dataset mesmo se não tiver dados (para mostrar funcionário)
            colors = get_employee_color(employee.real_name)
            
            datasets.append({
                'label': str(employee.real_name),
                'data': data,
                'borderColor': colors['border'],
                'backgroundColor': colors['bg'],
                'tension': 0.4,
                'fill': False
            })
            
            current_app.logger.info(f"Dataset criado para {employee.real_name}: {data}")
        
        result = {
            'labels': [f'Semana {w}' for w in weeks],
            'datasets': datasets
        }
        
        current_app.logger.info(f"Resultado final semanal: {len(datasets)} datasets, {len(weeks)} labels")
        return result
        
    except Exception as e:
        current_app.logger.error(f"Erro ao obter dados de progresso semanal: {str(e)}")
        import traceback
        current_app.logger.error(f"Traceback: {traceback.format_exc()}")
        return {'labels': [], 'datasets': []}

def get_monthly_evolution_data(employee_id=None):
    """Retorna dados de evolução mensal"""
    try:
        if employee_id:
            employees = [Employee.query.get(employee_id)]
        else:
            employees = Employee.query.all()
        
        current_app.logger.info(f"Funcionários para dados mensais: {len(employees)}")
        
        if not employees:
            return {'labels': [], 'datasets': []}
        
        # Sempre mostrar 5 semanas (semanas 1-5)
        weeks_in_month = ['1', '2', '3', '4', '5']
        
        current_app.logger.info(f"Semanas do mês: {weeks_in_month}")
        
        datasets = []
        
        for employee in employees:
            if not employee or not employee.real_name:
                continue
                
            data = []
            
            for week in weeks_in_month:
                try:
                    start_date, end_date = get_week_dates(week)
                    
                    entries = Entry.query.filter(
                        Entry.employee_id == employee.id,
                        Entry.date >= start_date,
                        Entry.date <= end_date
                    ).all()
                    
                    weekly_points = sum(entry.points for entry in entries)
                    data.append(float(weekly_points))
                    
                except Exception as e:
                    current_app.logger.error(f"Erro ao processar semana {week} para {employee.real_name}: {str(e)}")
                    data.append(0.0)
            
            colors = get_employee_color(employee.real_name)
            
            datasets.append({
                'label': str(employee.real_name),
                'data': data,
                'borderColor': colors['border'],
                'backgroundColor': colors['bg'],
                'tension': 0.4
            })
        
        result = {
            'labels': [f'Semana {w}' for w in weeks_in_month],
            'datasets': datasets
        }
        
        current_app.logger.info(f"Resultado final mensal: {len(datasets)} datasets")
        return result
        
    except Exception as e:
        current_app.logger.error(f"Erro ao obter evolução mensal: {str(e)}")
        import traceback
        current_app.logger.error(f"Traceback: {traceback.format_exc()}")
        return {'labels': [], 'datasets': []}

def get_daily_data(employee_id=None, week=None):
    """Retorna dados diários para o ciclo atual (desde dia 26)"""
    try:
        # Calcular início do ciclo atual (dia 26)
        today = datetime.now().date()
        
        if today.day >= 26:
            # Se hoje é dia 26 ou depois, o ciclo começou no dia 26 deste mês
            cycle_start = today.replace(day=26)
        else:
            # Se hoje é antes do dia 26, o ciclo começou no dia 26 do mês anterior
            if today.month == 1:
                cycle_start = today.replace(year=today.year-1, month=12, day=26)
            else:
                cycle_start = today.replace(month=today.month-1, day=26)
        
        start_date = cycle_start
        end_date = today
        
        current_app.logger.info(f"Buscando dados diários do ciclo: {start_date} até {end_date}")
        
        if employee_id:
            employees = Employee.query.filter(Employee.id == employee_id).all()
        else:
            employees = Employee.query.all()
            
        current_app.logger.info(f"Funcionários para dados diários: {len(employees)}")
        
        if not employees:
            return {'labels': [], 'datasets': []}
            
        datasets = []
        
        # Criar labels desde o início do ciclo até hoje
        labels = []
        dates = []
        current_date = start_date
        
        while current_date <= end_date:
            labels.append(current_date.strftime('%d/%m'))
            dates.append(current_date.strftime('%Y-%m-%d'))
            current_date += timedelta(days=1)
        
        current_app.logger.info(f"Datas para análise: {dates}")
        
        for employee in employees:
            if not employee or not employee.real_name:
                continue
                
            data = []
            
            for date_str in dates:
                try:
                    # Buscar entradas do dia
                    entries = Entry.query.filter(
                        Entry.employee_id == employee.id,
                        func.date(Entry.date) == date_str
                    ).all()
                    
                    daily_points = sum(entry.points for entry in entries)
                    data.append(float(daily_points))
                    
                    current_app.logger.info(f"Pontos de {employee.real_name} em {date_str}: {daily_points}")
                    
                except Exception as e:
                    current_app.logger.error(f"Erro ao processar dia {date_str} para {employee.real_name}: {str(e)}")
                    data.append(0.0)
            
            colors = get_employee_color(employee.real_name)
            
            datasets.append({
                'label': str(employee.real_name),
                'data': data,
                'borderColor': colors['border'],
                'backgroundColor': colors['bg'],
                'tension': 0.4,
                'fill': False
            })
        
        result = {
            'labels': labels,
            'datasets': datasets
        }
        
        current_app.logger.info(f"Resultado final diário: {len(datasets)} datasets, {len(labels)} labels")
        return result
        
    except Exception as e:
        current_app.logger.error(f"Erro ao obter dados diários: {str(e)}")
        import traceback
        current_app.logger.error(f"Traceback: {traceback.format_exc()}")
        return {'labels': [], 'datasets': []}

def get_daily_data_by_employee(employee_id, week):
    """Retorna dados diários para um funcionário específico em uma semana"""
    return get_daily_data(employee_id, week)

def get_weekly_evolution_data(employee_id=None):
    """Retorna dados de evolução semanal para um funcionário específico ou todos"""
    return get_weekly_progress_data()  # Usar a mesma função

def get_employee_color(employee_name):
    """Retorna um esquema de cores para o funcionário"""
    # Cores mais vibrantes e menos transparentes
    colors = {
        'Bernardo': {'border': '#4A90E2', 'bg': 'rgba(74, 144, 226, 0.6)'},
        'Matheus': {'border': '#50E3C2', 'bg': 'rgba(80, 227, 194, 0.6)'},
        'João': {'border': '#F5A623', 'bg': 'rgba(245, 166, 35, 0.6)'},
        'Maria': {'border': '#BD10E0', 'bg': 'rgba(189, 16, 224, 0.6)'},
        'Pessoa Teste': {'border': '#9B9B9B', 'bg': 'rgba(155, 155, 155, 0.6)'},
        'Luiza': {'border': '#7ED321', 'bg': 'rgba(126, 211, 33, 0.6)'},
        'Carlos': {'border': '#F8E71C', 'bg': 'rgba(248, 231, 28, 0.6)'},
        'Ana': {'border': '#FF69B4', 'bg': 'rgba(255, 105, 180, 0.6)'},
        'Pedro': {'border': '#8B572A', 'bg': 'rgba(139, 87, 42, 0.6)'},
        'Juliana': {'border': '#4A4A4A', 'bg': 'rgba(74, 74, 74, 0.6)'},
        'Rodrigo': {'border': '#FF6384', 'bg': 'rgba(255, 99, 132, 0.6)'}, 
        'Maurício': {'border': '#36A2EB', 'bg': 'rgba(54, 162, 235, 0.6)'}, 
        'Wesley': {'border': '#FFCE56', 'bg': 'rgba(255, 206, 86, 0.6)'}   
    }
    return colors.get(employee_name, {'border': '#9B9B9B', 'bg': 'rgba(155, 155, 155, 0.6)'})