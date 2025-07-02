from flask import Blueprint, request, render_template, redirect, url_for, session, flash
from models.employee import Employee

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def index():
    return render_template('index.html')

@auth_bp.route('/employee_login', methods=['GET', 'POST'])
def employee_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']  # O nome do campo no formulário pode continuar sendo password
        
        # Usar access_key em vez de password e remover o filtro role='employee'
        employee = Employee.query.filter_by(username=username, access_key=password).first()
        
        if employee:
            session['user_id'] = employee.id
            session['username'] = employee.username
            session['real_name'] = employee.real_name
            session['role'] = 'employee'  # Definir role diretamente na sessão
            return redirect(url_for('dashboard.employee_dashboard_enhanced'))
        else:
            flash('Credenciais inválidas!', 'error')
    
    return render_template('employee_login.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        
        # Verificar se é o CEO
        if username == "Luis" and password == "Moni4242":
            session.clear()
            session['role'] = 'ceo'
            session['user'] = username
            session['real_name'] = 'Luis'  # Add real_name to session
            session['user_id'] = 'ceo_001'  # Add user_id for consistency
            return redirect(url_for('dashboard.ceo_dashboard_enhanced'))
        else:
            flash('Credenciais inválidas!', 'error')
    
    return render_template('ceo_login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.index'))