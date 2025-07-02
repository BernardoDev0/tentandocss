from flask import Blueprint, request, jsonify, send_file, current_app, session, redirect, url_for, flash
from models import db, Employee, Entry
from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from utils.data_processing import get_weekly_evolution_data
import tempfile
from utils.calculations import calculate_weekly_progress, get_current_week, get_week_from_date

api_bp = Blueprint('api', __name__)

@api_bp.route('/register_points', methods=['POST'])
def register_points():
    if 'role' not in session or session['role'] != 'employee':
        return redirect(url_for('auth.index'))
    
    try:
        employee_id = session['user_id']
        date = request.form['date']
        refinery = request.form['refinery']
        points = int(request.form['points'])
        observations = request.form.get('observations', '')
        
        # Verificar se já existe um registro para esta data
        existing_entry = Entry.query.filter_by(
            employee_id=employee_id,
            date=date
        ).first()
        
        if existing_entry:
            flash('Já existe um registro para esta data!', 'error')
        else:
            new_entry = Entry(
                employee_id=employee_id,
                date=date,
                refinery=refinery,
                points=points,
                observations=observations
            )
            
            db.session.add(new_entry)
            db.session.commit()
            flash('Pontos registrados com sucesso!', 'success')
        
        return redirect(url_for('dashboard.employee_dashboard_enhanced'))
    except Exception as e:
        current_app.logger.error(f"Erro ao registrar pontos: {str(e)}")
        return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500

@api_bp.route('/edit_entry/<int:entry_id>', methods=['GET', 'POST'])
def edit_entry(entry_id):
    if 'role' not in session:
        return redirect(url_for('auth.index'))
    
    entry = Entry.query.get_or_404(entry_id)
    
    # Verificar permissões
    if session['role'] == 'employee' and entry.employee_id != session['user_id']:
        flash('Você não tem permissão para editar este registro!', 'error')
        return redirect(url_for('dashboard.employee_dashboard_enhanced'))
    
    if request.method == 'POST':
        try:
            entry.date = request.form['date']
            entry.refinery = request.form['refinery']
            entry.points = int(request.form['points'])
            entry.observations = request.form.get('observations', '')
            
            db.session.commit()
            flash('Registro atualizado com sucesso!', 'success')
            
            # Redirecionar baseado no papel do usuário
            if session['role'] == 'ceo':
                week = request.form.get('week')
                employee_id = request.form.get('employee_id')
                return redirect(url_for('dashboard.ceo_dashboard_enhanced', week=week, employee_id=employee_id))
            else:
                return redirect(url_for('dashboard.employee_dashboard_enhanced'))
        except Exception as e:
            current_app.logger.error(f"Erro ao editar entrada: {str(e)}")
            return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500

@api_bp.route('/api/delete_entry/<int:entry_id>', methods=['POST'])
@api_bp.route('/delete_entry/<int:entry_id>', methods=['POST'])
def delete_entry(entry_id):
    if 'role' not in session:
        return redirect(url_for('auth.index'))
    
    entry = Entry.query.get_or_404(entry_id)
    
    # Verificar permissões
    if session['role'] == 'employee' and entry.employee_id != session['user_id']:
        flash('Você não tem permissão para excluir este registro!', 'error')
        return redirect(url_for('dashboard.employee_dashboard_enhanced'))
    
    try:
        db.session.delete(entry)
        db.session.commit()
        flash('Registro excluído com sucesso!', 'success')
    except Exception as e:
        current_app.logger.error(f"Erro ao excluir entrada: {str(e)}")
        return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500

@api_bp.route('/api/delete_all_entries', methods=['POST'])
@api_bp.route('/delete_all_entries', methods=['POST'])
def delete_all_entries():
    if 'role' not in session or session['role'] != 'ceo':
        return redirect(url_for('auth.index'))
    
    try:
        # Excluir todos os registros
        Entry.query.delete()
        db.session.commit()
        flash('Todos os registros foram excluídos com sucesso!', 'success')
    except Exception as e:
        current_app.logger.error(f"Erro ao excluir todos os registros: {str(e)}")
        return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500

@api_bp.route('/api/export')
@api_bp.route('/export')
def export():
    if 'role' not in session or session['role'] != 'ceo':
        return redirect(url_for('auth.index'))
    
    try:
        # Criar um novo workbook
        wb = Workbook()
        ws = wb.active
        ws.title = "Relatório de Pontos"
        
        # Cabeçalhos
        headers = ['Data', 'Funcionário', 'Refinaria', 'Pontos', 'Observações']
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.font = Font(bold=True)
            cell.fill = PatternFill(start_color="CCCCCC", end_color="CCCCCC", fill_type="solid")
            cell.alignment = Alignment(horizontal="center")
        
        # Buscar todos os registros
        entries = Entry.query.join(Employee).order_by(Entry.date.desc()).all()
        
        # Adicionar dados
        for row, entry in enumerate(entries, 2):
            ws.cell(row=row, column=1, value=entry.date)
            ws.cell(row=row, column=2, value=entry.employee.real_name)
            ws.cell(row=row, column=3, value=entry.refinery)
            ws.cell(row=row, column=4, value=entry.points)
            ws.cell(row=row, column=5, value=entry.observations or '')
        
        # Ajustar largura das colunas
        for column in ws.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            ws.column_dimensions[column_letter].width = adjusted_width
        
        # Salvar em arquivo temporário
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
        wb.save(temp_file.name)
        temp_file.close()
        
        # Enviar arquivo
        return send_file(
            temp_file.name,
            as_attachment=True,
            download_name=f'relatorio_pontos_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        current_app.logger.error(f"Erro ao exportar relatório: {str(e)}")
        flash('Erro ao exportar relatório', 'error')
        return redirect(url_for('dashboard.ceo_dashboard_enhanced'))

@api_bp.route('/team-progress')
def get_team_progress():
    """Retorna dados de progresso da equipe para uma semana específica"""
    week = request.args.get('week', 1, type=int)
    
    employees = Employee.query.all()
    team_data = []
    
    for employee in employees:
        # Calcular pontos da semana usando a lógica existente
        weekly_data = get_weekly_evolution_data(employee.id)
        
        # Extrair pontos da semana específica
        week_points = 0
        if weekly_data and 'datasets' in weekly_data:
            for dataset in weekly_data['datasets']:
                if len(dataset['data']) >= week:
                    week_points = dataset['data'][week - 1]
        
        # Calcular porcentagem usando a meta individual do funcionário
        percentage = (week_points / employee.weekly_goal) * 100
        
        team_data.append({
            'id': employee.id,
            'name': employee.real_name,
            'points': week_points,
            'percentage': percentage
        })
    
    return jsonify({
        'employees': team_data,
        'week': week
    })

@api_bp.route('/employees')
@api_bp.route('/api/employees')
def get_employees_summary():
    """Retorna resumo (points, percentage) dos funcionários para a semana selecionada."""
    week = request.args.get('week', 1, type=int)

    employees = Employee.query.all()

    # Obter progresso semanal agregado usando utilidade existente
    current_week = get_current_week()
    selected_week_str = request.args.get('week_str')
    if selected_week_str:
        selected_week = selected_week_str
    else:
        selected_week = current_week

    weekly_progress = calculate_weekly_progress(None, selected_week)

    data = []
    for emp in employees:
        points = weekly_progress.get(emp.real_name, 0)
        percentage = (points / emp.weekly_goal * 100) if emp.weekly_goal else 0
        data.append({
            'id': emp.id,
            'name': emp.real_name,
            'weekly_points': points,
            'percentage': percentage,
            'weekly_goal': emp.weekly_goal
        })

    return jsonify({'employees': data})

@api_bp.route('/api/weekly_data')
def api_weekly_data():
    from utils.data_processing import get_weekly_progress_data
    return jsonify(get_weekly_progress_data())

@api_bp.route('/api/monthly_data')
def api_monthly_data():
    from utils.data_processing import get_monthly_evolution_data
    return jsonify(get_monthly_evolution_data())

@api_bp.route('/api/daily_data')
def api_daily_data():
    from utils.data_processing import get_daily_data
    return jsonify(get_daily_data())

@api_bp.route('/api/entries')
def api_entries():
    """Retorna lista de registros em JSON; se ?week=n é passado, filtra pela semana do mês (1-5)."""
    if 'role' not in session or session['role'] != 'ceo':
        return jsonify({'error': 'Unauthorized'}), 401

    week = request.args.get('week', type=int)

    # Consulta base
    query = Entry.query.join(Employee)

    # Obter lista ordenada
    entries_query = query.order_by(Entry.date.desc()).all()

    # Se houver parâmetro de semana, filtrar usando lógica de ciclo 26-25.
    if week:
        try:
            week_int = int(week)
        except (TypeError, ValueError):
            week_int = None
        if week_int:
            filtered_entries = []
            for e in entries_query:
                try:
                    if get_week_from_date(str(e.date)) == week_int:
                        filtered_entries.append(e)
                except Exception as parse_err:
                    current_app.logger.warning(f"Não foi possível calcular semana para data '{e.date}': {parse_err}")
            entries = filtered_entries
        else:
            entries = entries_query
    else:
        entries = entries_query

    data = []
    for e in entries:
        data.append({
            'id': e.id,
            'date': e.date if isinstance(e.date, str) else e.date.strftime('%Y-%m-%d %H:%M:%S'),
            'employee': e.employee.real_name,
            'refinery': e.refinery,
            'points': e.points,
            'observations': e.observations or ''
        })

    return jsonify({'entries': data})