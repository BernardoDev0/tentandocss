from flask import Blueprint, session, redirect, url_for, jsonify
from models import Employee, Entry
from utils.calculations import get_available_weeks, get_current_week, get_week_dates

diagnostics_bp = Blueprint('diagnostics', __name__)

@diagnostics_bp.route('/diagnostico')
def diagnostico():
    if 'role' not in session or session['role'] != 'ceo':
        return redirect(url_for('auth.index'))
    
    try:
        # Verificar funcionários
        employees = Employee.query.all()
        employee_count = len(employees)
        
        # Verificar entradas
        entries = Entry.query.all()
        entry_count = len(entries)
        
        # Verificar semanas disponíveis
        available_weeks = get_available_weeks()
        
        # Verificar semana atual
        current_week = get_current_week()
        start_date, end_date = get_week_dates(current_week)
        
        # Verificar entradas da semana atual
        current_entries = Entry.query.filter(
            Entry.date >= start_date,
            Entry.date <= end_date
        ).all()
        current_entry_count = len(current_entries)
        
        # Preparar resultado
        result = {
            "funcionarios": {
                "total": employee_count,
                "detalhes": [{
                    "id": emp.id,
                    "nome": emp.real_name,
                    "username": emp.username
                } for emp in employees]
            },
            "entradas": {
                "total": entry_count,
                "semana_atual": current_entry_count,
                "detalhes": [{
                    "id": entry.id,
                    "funcionario": entry.employee.real_name,
                    "data": entry.date,
                    "pontos": entry.points
                } for entry in entries[:10]]  # Mostrar apenas as 10 primeiras
            },
            "semanas": {
                "atual": current_week,
                "periodo": f"{start_date} até {end_date}",
                "disponiveis": available_weeks
            }
        }
        return jsonify(result)
    except Exception as e:
        return jsonify({"erro": str(e)})