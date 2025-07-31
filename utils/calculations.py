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
            
            # CORREÇÃO: Calcular semanas corretamente
            # Semana 1: ciclo_start até ciclo_start + 6 dias
            # Semana 2: ciclo_start - 7 dias até ciclo_start - 1 dia
            # Semana 3: ciclo_start - 14 dias até ciclo_start - 8 dias
            # etc.
            
            if week_num == 1:
                week_start = cycle_start
                week_end = cycle_start + timedelta(days=6)
            else:
                # Para semanas anteriores, voltar no tempo
                days_back = (week_num - 1) * 7
                week_start = cycle_start - timedelta(days=days_back)
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

        # Se o dia cair exatamente no múltiplo de 7 (ex.: 7, 14, 21...) **e** não for o primeiro dia do ciclo,
        # consideramos ainda a semana anterior (mantém 26-02 como Semana 1, 03-09 Semana 2, etc.)
        if delta_days != 0 and delta_days % 7 == 0:
            week_number -= 1

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
        # Se não for informado, usar semana atual
        if not week_num:
            week_num = get_current_week()

        # Sempre trabalhar com a versão em string para reutilizar a função get_week_dates
        week_str = str(week_num)

        # Obter intervalo (26-do-mês a 25-do-mês) correspondente à semana desejada
        start_date, end_date = get_week_dates(week_str)
        current_app.logger.info(
            f"Calculando progresso semanal (semana {week_str}) – período {start_date} a {end_date}"
        )

        # Construir consulta filtrando pelo intervalo de datas
        query = Entry.query.filter(Entry.date >= start_date, Entry.date <= end_date)

        # Se for um funcionário específico, limitar
        if employee_id:
            query = query.filter(Entry.employee_id == employee_id)
            current_app.logger.info(f"Filtrando por funcionário ID: {employee_id}")

        entries = query.all()
        current_app.logger.info(f"Entradas encontradas: {len(entries)}")

        # Se for um funcionário específico, retornar dados estruturados
        if employee_id:
            # Calcular pontos totais
            total_points = sum(entry.points for entry in entries)
            
            # Buscar funcionário para obter meta semanal
            employee = Employee.query.get(employee_id)
            weekly_goal = employee.weekly_goal if employee else 0

            # Calcular porcentagem de progresso
            progress_percentage = (total_points / weekly_goal * 100) if weekly_goal > 0 else 0
            remaining_points = max(0, weekly_goal - total_points)

            return {
                'current_points': total_points,
                'weekly_goal': weekly_goal,
                'progress_percentage': progress_percentage,
                'remaining_points': remaining_points
            }
        else:
            # Para todos os funcionários, retornar dicionário por nome
            employee_totals = {}
            for entry in entries:
                emp_name = entry.employee.real_name
                if emp_name not in employee_totals:
                    employee_totals[emp_name] = 0
                employee_totals[emp_name] += entry.points
            
            current_app.logger.info(f"Totais semanais por funcionário: {employee_totals}")
            return employee_totals

    except Exception as e:
        current_app.logger.error(f"Erro ao calcular progresso semanal: {str(e)}")
        if employee_id:
            return {
                'current_points': 0,
                'weekly_goal': 0,
                'progress_percentage': 0,
                'remaining_points': 0
            }
        else:
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