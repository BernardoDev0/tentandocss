from flask import Blueprint, request, render_template, redirect, url_for, session, flash
from models.employee import Employee

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def index():
    # Sempre limpar sessão ao acessar página inicial para forçar novo login
    session.clear()
    return render_template('login.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        # 1) Verificar CEO
        if username.lower() == 'luis' and password == 'Moni4242':
            session.clear()
            session.update({
                'role': 'ceo',
                'user': username,
                'real_name': 'Luis',
                'user_id': 'ceo_001'
            })
            return redirect(url_for('dashboard.ceo_dashboard_enhanced'))

        # 2) Verificar funcionário
        employee = Employee.query.filter_by(username=username, access_key=password).first()
        if employee:
            session.clear()
            session.update({
                'user_id': employee.id,
                'username': employee.username,
                'real_name': employee.real_name,
                'role': 'employee'
            })
            return redirect(url_for('dashboard.employee_dashboard_enhanced'))

        flash('Credenciais inválidas!', 'error')

    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.index'))