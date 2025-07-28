from flask import Blueprint, request, jsonify, send_file, current_app, session, redirect, url_for, flash, render_template
from models import db, Employee, Entry
from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from utils.data_processing import get_weekly_evolution_data
from utils.email_utils import send_confirmation_email
import tempfile
from utils.calculations import calculate_weekly_progress, get_current_week, get_week_from_date
import io
import zipfile
from calendar import monthrange

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
        
        # Permitir múltiplos registros na mesma data (não checamos duplicidade)
        new_entry = Entry(
            employee_id=employee_id,
            date=date,
            refinery=refinery,
            points=points,
            observations=observations
        )

        db.session.add(new_entry)
        db.session.commit()
        
        # Buscar informações do funcionário para o email
        employee = Employee.query.get(employee_id)
        if employee:
            # Enviar email de confirmação
            send_confirmation_email(
                employee.real_name,
                date,
                points,
                refinery,
                observations
            )
        
        flash('Ponto registrado com sucesso! Até amanhã!', 'success')
        
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
            # Combina data e hora (se fornecido)
            date_part = request.form['date']
            time_part = request.form.get('time', '').strip()
            if time_part and len(time_part)==5:  # HH:MM
                time_part += ':00'
            entry.date = f"{date_part} {time_part}" if time_part else date_part
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
    else:
        # Método GET: renderizar formulário de edição
        # Extrair partes de data e hora para pré-preencher inputs
        if hasattr(entry.date, 'strftime'):
            iso_date = entry.date.strftime('%Y-%m-%d')
            iso_time = entry.date.strftime('%H:%M:%S')
        else:
            date_str = str(entry.date)
            iso_date = date_str[:10]
            iso_time = date_str[11:19] if ' ' in date_str else ''

        return render_template('edit_entry.html', entry=entry, iso_date=iso_date, iso_time=iso_time)

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
        # Buscar registros e agrupar por funcionário
        from collections import defaultdict
        import os

        entries = Entry.query.join(Employee).order_by(Entry.date.desc()).all()

        entries_by_employee = defaultdict(list)
        for e in entries:
            entries_by_employee[e.employee.real_name].append(e)

        # Criar diretório temporário e arquivo zip
        with tempfile.TemporaryDirectory() as tmpdir:
            zip_path = os.path.join(tmpdir, 'relatorios_pontos.zip')
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for emp_name, emp_entries in entries_by_employee.items():
                    wb = Workbook()
                    ws = wb.active
                    ws.title = "Relatório de Pontos"

                    headers = ['Data', 'Refinaria', 'Pontos', 'Observações']
                    for col, header in enumerate(headers, 1):
                        cell = ws.cell(row=1, column=col, value=header)
                        cell.font = Font(bold=True)
                        cell.fill = PatternFill(start_color="CCCCCC", end_color="CCCCCC", fill_type="solid")
                        cell.alignment = Alignment(horizontal="center")

                    for row_idx, ent in enumerate(emp_entries, 2):
                        ws.cell(row=row_idx, column=1, value=ent.date)
                        ws.cell(row=row_idx, column=2, value=ent.refinery)
                        ws.cell(row=row_idx, column=3, value=ent.points)
                        ws.cell(row=row_idx, column=4, value=ent.observations or '')

                    # ======= RESUMO DO MÊS =======
                    # Base simplificada: DB contém apenas o mês corrente (dados apagados todo dia 26)
                    total_mes = sum(ent.points for ent in emp_entries)

                    meta_mensal = 10500 if emp_name.lower().startswith("matheus") else 9500
                    restante = max(meta_mensal - total_mes, 0)

                    summary_start = ws.max_row + 2  # uma linha em branco após dados
                    ws.cell(row=summary_start, column=1, value="Total no mês")
                    ws.cell(row=summary_start, column=3, value=total_mes)

                    ws.cell(row=summary_start + 1, column=1, value="Restante para meta")
                    ws.cell(row=summary_start + 1, column=3, value=restante)

                    # Ajustar larguras
                    for column in ws.columns:
                        max_len = 0
                        col_letter = column[0].column_letter
                        for c in column:
                            try:
                                max_len = max(max_len, len(str(c.value)))
                            except:
                                pass
                        ws.column_dimensions[col_letter].width = min(max_len + 2, 50)

                    # Salvar arquivo xlsx do funcionário
                    safe_name = emp_name.replace(' ', '_')
                    excel_path = os.path.join(tmpdir, f"{safe_name}.xlsx")
                    wb.save(excel_path)
                    zipf.write(excel_path, arcname=f"{safe_name}.xlsx")

            # Ler o zip em memória para evitar problemas de remoção do diretório temporário
            with open(zip_path, 'rb') as f:
                data = f.read()

            mem_file = io.BytesIO(data)
            mem_file.seek(0)

            return send_file(
                mem_file,
                as_attachment=True,
                download_name=f'relatorios_pontos_{datetime.now().strftime("%Y%m%d_%H%M%S")}.zip',
                mimetype='application/zip'
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
    employee_id_filter = request.args.get('employee_id', type=int)

    # Consulta base
    query = Entry.query.join(Employee)
    if employee_id_filter:
        query = query.filter(Employee.id == employee_id_filter)

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