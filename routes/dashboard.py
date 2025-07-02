from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, session
from models import db, Employee, Entry
from utils.calculations import (
    calculate_weekly_progress,
    calculate_monthly_progress,
    calculate_executive_kpis,
    get_current_week,
    get_week_dates,
    get_available_weeks
)
from utils.data_processing import (
    get_weekly_progress_data,
    get_employee_color,
    get_monthly_evolution_data,
    get_daily_data,
    get_weekly_evolution_data,
    get_daily_data_by_employee
)
from utils.helpers import safe_json_dumps, timezone
from datetime import datetime, timedelta
import traceback
from sqlalchemy import func

# Change this line from 'dashboard_bp' to 'dashboard'
dashboard_bp = Blueprint('dashboard', __name__)

# Update all route decorators from @dashboard.route to @dashboard_bp.route
@dashboard_bp.route('/employee_dashboard_enhanced')
def employee_dashboard_enhanced():
    if 'role' not in session or session['role'] != 'employee':
        return redirect(url_for('auth.index'))
    
    try:
        employee_id = session['user_id']
        current_week = get_current_week()
        selected_week = request.args.get('week', current_week)
        
        # Calcular progresso semanal
        weekly_progress = calculate_weekly_progress(employee_id, selected_week)
        employee_name = session['real_name']
        weekly_points = weekly_progress.get(employee_name, 0)
        
        # Calcular progresso mensal
        now = datetime.now(timezone)
        monthly_progress = calculate_monthly_progress(employee_id, now.month, now.year)
        monthly_points = monthly_progress.get(employee_name, 0)
        
        # Buscar entradas da semana selecionada
        start_date, end_date = get_week_dates(selected_week)
        entries = Entry.query.filter(
            Entry.employee_id == employee_id,
            Entry.date >= start_date,
            Entry.date <= end_date
        ).order_by(Entry.date.desc()).all()
        
        # Buscar todas as entradas para histórico
        all_entries = Entry.query.filter(
            Entry.employee_id == employee_id
        ).order_by(Entry.date.desc()).limit(50).all()
        
        # Obter semanas disponíveis
        available_weeks = get_available_weeks()
        
        # Dados para gráficos
        weekly_data = get_weekly_evolution_data(employee_id)
        monthly_data = get_monthly_evolution_data(employee_id)
        daily_data = get_daily_data_by_employee(employee_id, selected_week)
        
        return render_template('employee_dashboard_enhanced.html',
                             weekly_points=weekly_points,
                             monthly_points=monthly_points,
                             entries=entries,
                             all_entries=all_entries,
                             selected_week=selected_week,
                             available_weeks=available_weeks,
                             weekly_evolution_data=safe_json_dumps(weekly_data),
                             monthly_evolution_data=safe_json_dumps(monthly_data),
                             daily_data=safe_json_dumps(daily_data))
    except Exception as e:
        current_app.logger.error(f"Erro no dashboard do funcionário: {str(e)}")
        flash('Erro ao carregar dashboard', 'error')
        return redirect(url_for('auth.index'))

@dashboard_bp.route('/ceo_dashboard_enhanced')
def ceo_dashboard_enhanced():
    """Dashboard do CEO – versão original sem streaming/caching."""

    # Permissão: apenas usuários com papel 'ceo'
    if 'role' not in session or session['role'] != 'ceo':
        return redirect(url_for('auth.index'))

    try:
        # Semana selecionada (padrão = semana corrente)
        current_week = get_current_week()
        selected_week = request.args.get('week', current_week)

        # Listagem de funcionários ativos
        employees = Employee.query.all()

        # Progresso semanal agregado da equipe
        weekly_progress = calculate_weekly_progress(None, selected_week)
        total_points = sum(weekly_progress.values()) if weekly_progress else 0

        # Progresso mensal por funcionário (retorna dict {nome: pontos})
        now = datetime.now(timezone)
        monthly_progress = calculate_monthly_progress(None, now.month, now.year)

        # Construir estrutura consolidada por funcionário
        employee_totals = {}
        for emp in employees:
            name = emp.real_name
            weekly_points = weekly_progress.get(name, 0)
            monthly_points = monthly_progress.get(name, 0)
            weekly_goal = emp.weekly_goal or 1
            monthly_goal = emp.monthly_goal or 1
            # Porcentagem de progresso semanal
            percentage = (weekly_points / weekly_goal) * 100 if weekly_goal else 0
            # Status
            if percentage >= 100:
                status = 'success'
            elif percentage >= 50:
                status = 'warning'
            else:
                status = 'danger'
            employee_totals[name] = {
                'weekly_points': weekly_points,
                'weekly_goal': weekly_goal,
                'monthly_points': monthly_points,
                'monthly_goal': monthly_goal,
                'status': status
            }
        # Calcular total mensal da equipe
        monthly_team_total = sum(monthly_progress.values()) if monthly_progress else 0

        # Média de porcentagem da equipe
        if employee_totals:
            team_average_percentage = sum(
                (v['weekly_points'] / v['weekly_goal']) * 100 if v['weekly_goal'] else 0
                for v in employee_totals.values()
            ) / len(employee_totals)
        else:
            team_average_percentage = 0

        # KPIs executivos avançados
        executive_kpis = calculate_executive_kpis()

        return render_template(
            'ceo_dashboard_enhanced.html',
            employees=employees,
            employee_totals=employee_totals,
            total_points=total_points,
            team_average_percentage=team_average_percentage,
            selected_week=selected_week,
            kpis=executive_kpis,
            monthly_team_total=monthly_team_total,
            header_only=False  # Garante render completo do template
        )
    except Exception as e:
        current_app.logger.error(f"Erro no dashboard do CEO: {str(e)}")
        traceback.print_exc()
        flash('Erro ao carregar dashboard do CEO', 'error')
        return redirect(url_for('auth.index'))

# ================= helper removido =================