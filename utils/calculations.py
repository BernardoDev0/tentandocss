from models import db, Employee, Entry
from utils.helpers import timezone, get_week_dates, get_current_week
from sqlalchemy import func
from flask import current_app
from datetime import datetime, timedelta  # Adicionar esta importação

def get_week_dates(week_str):
    """Converte string de semana para datas de início e fim"""
    try:
        # Se for um número (1-5), usar o sistema de ciclos
        if week_str.isdigit():
            week_num = int(week_str)
            
            # Obter data atual
            today = datetime.now()
            
            # Calcular início do ciclo (dia 26 do mês atual ou anterior)
            if today.day >= 26:
                cycle_start = today.replace(day=26)
            else:
                if today.month == 1:
                    cycle_start = today.replace(year=today.year-1, month=12, day=26)
                else:
                    cycle_start = today.replace(month=today.month-1, day=26)
            
            # Calcular início da semana específica
            week_start = cycle_start + timedelta(days=(week_num - 1) * 7)
            week_end = week_start + timedelta(days=6)
            
            return week_start.strftime('%Y-%m-%d'), week_end.strftime('%Y-%m-%d')
        
        # Sistema antigo para compatibilidade
        year, week = map(int, week_str.split('-W'))
        start_of_week = datetime.strptime(f'{year}-W{week:02d}-1', '%Y-W%W-%w')
        end_of_week = start_of_week + timedelta(days=6)
        return start_of_week.strftime('%Y-%m-%d'), end_of_week.strftime('%Y-%m-%d')
    except:
        # Fallback para semana atual
        today = datetime.now()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        return start_of_week.strftime('%Y-%m-%d'), end_of_week.strftime('%Y-%m-%d')

def get_current_week():
    today = datetime.now(timezone)
    return get_week_from_date(today.strftime('%Y-%m-%d %H:%M:%S'))

def get_week_from_date(date_str):
    """
    Calcula a semana com base no ciclo 26/mês_atual → 25/mês_seguinte.
    Retorna a semana atual (1 a 5).
    """
    try:
        # Aceitar tanto formato com hora quanto sem hora
        if ' ' in date_str:
            date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        else:
            date = datetime.strptime(date_str, '%Y-%m-%d')

        # Define o início do ciclo (dia 26 do mês atual ou anterior)
        if date.day >= 26:
            cycle_start = date.replace(day=26)
        else:
            # Retrocede para o dia 26 do mês anterior
            if date.month == 1:
                cycle_start = date.replace(year=date.year-1, month=12, day=26)
            else:
                cycle_start = date.replace(month=date.month-1, day=26)

        # Calcula a diferença em dias
        delta_days = (date - cycle_start).days

        # Semana = (dias de diferença // 7) + 1
        week_number = (delta_days // 7) + 1

        # Garantir que a semana 2 seja calculada corretamente
        if 7 <= delta_days < 14:
            week_number = 2

        return min(week_number, 5)  # Limita a 5 semanas
    except Exception as e:
        current_app.logger.error(f"Erro ao calcular semana: {str(e)}")  # Corrigir: era app.logger
        return 1  # Retorna semana 1 em caso de erro

def get_available_weeks():
    """Retorna lista de semanas disponíveis baseada nos registros"""
    try:
        # Retorna as 5 semanas do ciclo atual
        return ['1', '2', '3', '4', '5']
    except Exception as e:
        current_app.logger.error(f"Erro ao obter semanas disponíveis: {str(e)}")  # Corrigir: era app.logger
        return ['1', '2', '3', '4', '5']

# Substituir todas as ocorrências de app.logger por current_app.logger
# Por exemplo:
def calculate_weekly_progress(employee_id=None, week_num=None):
    try:
        if not week_num:  # Corrigir: era 'week', agora é 'week_num'
            week_num = get_current_week()
        
        # Se week_num for um número, usar o sistema de semanas do ciclo
        if isinstance(week_num, int) or (isinstance(week_num, str) and week_num.isdigit()):
            week_number = int(week_num)
            
            query = Entry.query
            if employee_id:
                query = query.filter(Entry.employee_id == employee_id)
                current_app.logger.info(f"Filtrando por funcionário ID: {employee_id}")  # Corrigir: era app.logger
            
            entries = query.all()
            
            # Filtrar entradas pela semana específica
            week_entries = []
            for entry in entries:
                try:
                    entry_week = get_week_from_date(entry.date)
                    if entry_week == week_number:
                        week_entries.append(entry)
                except:
                    continue
            
            current_app.logger.info(f"Entradas encontradas para semana {week_number}: {len(week_entries)}")
            
            # Calcular totais por funcionário
            employee_totals = {}
            for entry in week_entries:
                emp_name = entry.employee.real_name
                if emp_name not in employee_totals:
                    employee_totals[emp_name] = 0
                employee_totals[emp_name] += entry.points
            
            current_app.logger.info(f"Totais semanais calculados: {employee_totals}")
            return employee_totals
        else:
            # Usar o sistema antigo para compatibilidade
            start_date, end_date = get_week_dates(str(week_num))  # Corrigir: era 'week'
            current_app.logger.info(f"Calculando progresso semanal de {start_date} até {end_date}")  # Corrigir: era app.logger
            
            query = Entry.query.filter(
                Entry.date >= start_date,
                Entry.date <= end_date
            )
            
            if employee_id:
                query = query.filter(Entry.employee_id == employee_id)
                current_app.logger.info(f"Filtrando por funcionário ID: {employee_id}")  # Corrigir: era app.logger
            
            entries = query.all()
            current_app.logger.info(f"Entradas encontradas para cálculo semanal: {len(entries)}")  # Corrigir: era app.logger
            
            # Calcular totais por funcionário
            employee_totals = {}
            for entry in entries:
                emp_name = entry.employee.real_name
                if emp_name not in employee_totals:
                    employee_totals[emp_name] = 0
                employee_totals[emp_name] += entry.points
            
            current_app.logger.info(f"Totais semanais calculados: {employee_totals}")  # Corrigir: era app.logger
            return employee_totals
    except Exception as e:
        current_app.logger.error(f"Erro ao calcular progresso semanal: {str(e)}")
        return {}

def calculate_monthly_progress(employee_id=None, month=None, year=None):
    """Calcula o progresso mensal usando ciclos de 26 a 25"""
    try:
        if not month or not year:
            now = datetime.now(timezone)
            month = month or now.month
            year = year or now.year
        
        # Sistema de ciclos: 26 do mês anterior a 25 do mês atual
        # Mas se estamos após o dia 25, incluir também o período atual
        current_day = datetime.now().day
        
        if month == 1:
            start_date = f"{year-1}-12-26"
        else:
            start_date = f"{year}-{month-1:02d}-26"
        
        # Se estamos após o dia 25, estender até hoje
        if current_day > 25:
            end_date = datetime.now().strftime('%Y-%m-%d')
        else:
            end_date = f"{year}-{month:02d}-25"
        
        current_app.logger.info(f"Calculando progresso mensal de {start_date} até {end_date}")
        
        query = Entry.query.filter(
            Entry.date >= start_date,
            Entry.date <= end_date
        )
        
        if employee_id:
            query = query.filter(Entry.employee_id == employee_id)
        
        entries = query.all()
        current_app.logger.info(f"Entradas encontradas para cálculo mensal: {len(entries)}")
        
        # Calcular totais por funcionário
        employee_totals = {}
        for entry in entries:
            emp_name = entry.employee.real_name
            if emp_name not in employee_totals:
                employee_totals[emp_name] = 0
            employee_totals[emp_name] += entry.points
        
        current_app.logger.info(f"Totais por funcionário: {employee_totals}")
        return employee_totals
    except Exception as e:
        current_app.logger.error(f"Erro ao calcular progresso mensal: {str(e)}")
        return {}

def calculate_executive_kpis():
    """Calcula KPIs executivos avançados para o dashboard do CEO"""
    try:
        employees = Employee.query.all()
        now = datetime.now()
        
        # KPIs de Performance da Equipe
        total_team_points = 0
        employees_meeting_goals = 0
        total_employees = len(employees)
        
        # KPIs de Tendências
        employees_at_risk = []
        top_performers = []
        
        # Calcular métricas para cada funcionário
        for employee in employees:
            # Pontos da semana atual
            current_week = get_current_week()
            start_date, end_date = get_week_dates(current_week)
            
            weekly_points = db.session.query(func.sum(Entry.points)).filter(
                Entry.employee_id == employee.id,
                Entry.date >= start_date,
                Entry.date <= end_date
            ).scalar() or 0
            
            total_team_points += weekly_points
            
            # Verificar se está atingindo a meta (70% da meta semanal)
            weekly_goal = employee.weekly_goal or 2375
            goal_percentage = (weekly_points / weekly_goal) * 100 if weekly_goal > 0 else 0
            
            if goal_percentage >= 70:
                employees_meeting_goals += 1
            
            # Classificar funcionários
            if goal_percentage < 70:
                employees_at_risk.append({
                    'name': employee.real_name,
                    'percentage': goal_percentage,
                    'points': weekly_points
                })
            elif goal_percentage >= 110:
                top_performers.append({
                    'name': employee.real_name,
                    'percentage': goal_percentage,
                    'points': weekly_points
                })
        
        # Calcular KPIs comparativos (semana anterior)
        current_week_str = str(current_week) if current_week is not None else "1"
        previous_week = str(int(current_week_str) - 1) if current_week_str.isdigit() and int(current_week_str) > 1 else "1"
        
        try:
            prev_start_date, prev_end_date = get_week_dates(previous_week)
        except Exception:
            # Se houver erro ao obter datas, usar valores padrão
            prev_start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            prev_end_date = datetime.now().strftime('%Y-%m-%d')
        
        previous_week_points = db.session.query(func.sum(Entry.points)).filter(
            Entry.date >= prev_start_date,
            Entry.date <= prev_end_date
        ).scalar() or 0
        
        # Calcular variação percentual
        week_variation = 0
        if previous_week_points > 0:
            week_variation = ((total_team_points - previous_week_points) / previous_week_points) * 100
        
        # KPIs finais
        kpis = {
            'team_performance': {
                'total_points': total_team_points,
                'avg_points_per_employee': total_team_points / total_employees if total_employees > 0 else 0,
                'goal_achievement_rate': (employees_meeting_goals / total_employees) * 100 if total_employees > 0 else 0,
                'employees_meeting_goals': employees_meeting_goals,
                'total_employees': total_employees
            },
            'trends_and_alerts': {
                'employees_at_risk': employees_at_risk[:3],  # Top 3 em risco
                'top_performers': sorted(top_performers, key=lambda x: x['percentage'], reverse=True)[:3],  # Top 3 performers
                'critical_alerts_count': len(employees_at_risk),
                'week_variation': week_variation
            },
            'comparative': {
                'current_week_points': total_team_points,
                'previous_week_points': previous_week_points,
                'week_variation_percentage': week_variation,
                'trend_direction': 'up' if week_variation > 0 else 'down' if week_variation < 0 else 'stable'
            }
        }
        
        return kpis
        
    except Exception as e:
        current_app.logger.error(f"Erro ao calcular KPIs executivos: {str(e)}")
        return {}