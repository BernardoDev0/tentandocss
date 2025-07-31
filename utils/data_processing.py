from datetime import datetime, timedelta
from sqlalchemy import func
from models import db, Employee, Entry
from utils.calculations import get_week_dates, get_current_week
from flask import current_app

def get_weekly_progress_data():
    """OTIMIZADO: Busca dados semanais com consulta única"""
    try:
        current_app.logger.info("Iniciando busca de dados semanais otimizada")
        
        # Buscar todos os funcionários de uma vez
        employees = Employee.query.all()
        current_app.logger.info(f"Funcionários encontrados: {len(employees)}")
        
        # Buscar TODOS os registros de uma vez (otimização agressiva)
        all_entries = Entry.query.all()
        current_app.logger.info(f"Total de registros carregados: {len(all_entries)}")
        
        # Processar dados em memória (muito mais rápido)
        employee_data = {emp.id: emp.real_name for emp in employees}
        weekly_data = {emp.id: [0] * 5 for emp in employees}  # 5 semanas
        
        # Calcular datas das semanas
        from utils.calculations import get_week_dates
        week_dates = []
        for week in range(1, 6):
            start_date, end_date = get_week_dates(str(week))
            week_dates.append((start_date, end_date))
            current_app.logger.info(f"Processando semana {week}: {start_date} até {end_date}")
        
        # Processar todos os registros de uma vez
        for entry in all_entries:
            entry_date = entry.date
            if hasattr(entry_date, 'strftime'):
                entry_date_str = entry_date.strftime('%Y-%m-%d')
            else:
                entry_date_str = str(entry_date)[:10]  # Pegar apenas a data
            
            # Encontrar em qual semana está
            for week_idx, (start_date, end_date) in enumerate(week_dates):
                if start_date <= entry_date_str <= end_date:
                    if entry.employee_id in weekly_data:
                        weekly_data[entry.employee_id][week_idx] += entry.points
                    break
        
        # Preparar dados para Chart.js
        datasets = []
        labels = [f"Semana {i}" for i in range(1, 6)]
        
        for employee in employees:
            if employee.id in weekly_data:
                # ✅ CORES FIXAS E DISTINTAS PARA CADA FUNCIONÁRIO
                employee_colors = get_employee_color(employee.real_name)
                dataset = {
                    'label': employee.real_name,
                    'data': weekly_data[employee.id],
                    'borderColor': employee_colors['border'],
                    'backgroundColor': employee_colors['bg'],
                    'tension': 0.4
                }
                datasets.append(dataset)
            
        current_app.logger.info(f"Resultado final semanal: {len(datasets)} datasets, {len(labels)} labels")
        
        return {
            'labels': labels,
            'datasets': datasets
        }
        
    except Exception as e:
        current_app.logger.error(f"Erro ao obter dados semanais: {str(e)}")
        return {'labels': [], 'datasets': []}

def get_monthly_evolution_data():
    """OTIMIZADO: Busca dados mensais com consulta única"""
    try:
        current_app.logger.info("Iniciando busca de dados mensais otimizada")
        
        # Buscar todos os funcionários de uma vez
        employees = Employee.query.all()
        current_app.logger.info(f"Funcionários para dados mensais: {len(employees)}")
        
        # Buscar TODOS os registros de uma vez
        all_entries = Entry.query.all()
        current_app.logger.info(f"Total de registros para processamento mensal: {len(all_entries)}")
        
        # Processar dados em memória
        employee_data = {emp.id: emp.real_name for emp in employees}
        monthly_data = {emp.id: [0] * 5 for emp in employees}  # 5 meses
        
        # Calcular datas dos meses (últimos 5 meses)
        from datetime import datetime, timedelta
        month_dates = []
        today = datetime.now()
        
        for i in range(5):
            month_date = today - timedelta(days=30*i)
            month_start = month_date.replace(day=26)
            if i == 0:
                month_end = today
            else:
                month_end = month_start + timedelta(days=30)
            month_dates.append((month_start.strftime('%Y-%m-%d'), month_end.strftime('%Y-%m-%d')))
        
        # Processar todos os registros de uma vez
        for entry in all_entries:
            entry_date = entry.date
            if hasattr(entry_date, 'strftime'):
                entry_date_str = entry_date.strftime('%Y-%m-%d')
            else:
                entry_date_str = str(entry_date)[:10]
            
            # Encontrar em qual mês está
            for month_idx, (start_date, end_date) in enumerate(month_dates):
                if start_date <= entry_date_str <= end_date:
                    if entry.employee_id in monthly_data:
                        monthly_data[entry.employee_id][month_idx] += entry.points
                    break
        
        # Preparar dados para Chart.js
        datasets = []
        labels = [f"Semana {i+1}" for i in range(5)]
        
        for employee in employees:
            if employee.id in monthly_data:
                # ✅ CORES FIXAS E DISTINTAS PARA CADA FUNCIONÁRIO
                employee_colors = get_employee_color(employee.real_name)
                dataset = {
                    'label': employee.real_name,
                    'data': monthly_data[employee.id],
                    'borderColor': employee_colors['border'],
                    'backgroundColor': employee_colors['bg'],
                    'tension': 0.4
                }
                datasets.append(dataset)
                current_app.logger.info(f"Dataset criado para {employee.real_name}: {monthly_data[employee.id]}")
        
        current_app.logger.info(f"Resultado final mensal: {len(datasets)} datasets")
        
        return {
            'labels': labels,
            'datasets': datasets
        }
        
    except Exception as e:
        current_app.logger.error(f"Erro ao obter dados mensais: {str(e)}")
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
    # ✅ CORES MAIS DISTINTAS E FÁCEIS DE DIFERENCIAR
    colors = {
        'Rodrigo': {'border': '#8B5CF6', 'bg': 'rgba(139, 92, 246, 0.6)'},   # ✅ ROXO ESCURO
        'Maurício': {'border': '#F59E0B', 'bg': 'rgba(245, 158, 11, 0.6)'},   # ✅ LARANJA (era azul)
        'Matheus': {'border': '#10B981', 'bg': 'rgba(16, 185, 129, 0.6)'},    # ✅ VERDE ESCURO
        'Wesley': {'border': '#EF4444', 'bg': 'rgba(239, 68, 68, 0.6)'}       # ✅ VERMELHO
    }
    return colors.get(employee_name, {'border': '#6B7280', 'bg': 'rgba(107, 114, 128, 0.6)'})