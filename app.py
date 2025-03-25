from flask import Flask, render_template, request, redirect, url_for, session, send_file, flash
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from datetime import datetime, timedelta
from io import BytesIO
from sqlalchemy import text
import zipfile
import pandas as pd
import pytz
import os
from dotenv import load_dotenv
from threading import Thread

# Carrega variáveis de ambiente
load_dotenv()

# Configuração do Flask
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'uma-chave-secreta-padrao-segura')

# Configuração do banco de dados
database_url = os.getenv('DATABASE_URL', '').replace("postgres://", "postgresql://", 1)
if 'postgresql://' in database_url:
    database_url += "?sslmode=require"
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Configuração de email
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
mail = Mail(app)

# Fuso horário
timezone = pytz.timezone('America/Sao_Paulo')

# Modelos do banco de dados
class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    weekly_goal = db.Column(db.Integer, default=800)
    access_key = db.Column(db.String(50), unique=True, nullable=False)
    entries = db.relationship('Entry', backref='employee', lazy=True)

class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    refinery = db.Column(db.String(100), nullable=False)
    points = db.Column(db.Integer, nullable=False)
    observations = db.Column(db.String(200), nullable=False)

# Funções auxiliares
def init_db():
    """Inicializa o banco de dados"""
    with app.app_context():
        db.create_all()
        create_initial_employees()

def create_initial_employees():
    """Cria os funcionários iniciais se não existirem"""
    employees = [
        {'name': 'Rodrigo', 'weekly_goal': 800, 'access_key': 'rodrigo123'},
        {'name': 'Maurício', 'weekly_goal': 800, 'access_key': 'mauricio123'},
        {'name': 'Matheus', 'weekly_goal': 800, 'access_key': 'matheus123'}
    ]
    
    for emp in employees:
        if not Employee.query.filter_by(name=emp['name']).first():
            new_employee = Employee(
                name=emp['name'],
                weekly_goal=emp['weekly_goal'],
                access_key=emp['access_key']
            )
            db.session.add(new_employee)
    db.session.commit()

def send_async_email(app, msg):
    """Envia email em segundo plano"""
    with app.app_context():
        try:
            mail.send(msg)
        except Exception as e:
            app.logger.error(f"Erro ao enviar email: {str(e)}")

def send_confirmation_email(employee_name, date, points, refinery, observations):
    """Envia email de confirmação"""
    recipient = {
        'Rodrigo': 'rodrigo@monitorarconsultoria.com.br',
        'Maurício': 'carlos.mauricio.prestserv@petrobras.com.br',
        'Matheus': 'Matheus.e.lima.prestserv@petrobras.com.br'
    }.get(employee_name)
    
    if recipient:
        msg = Message(
            subject="Confirmação de Ponto Registrado",
            sender=app.config['MAIL_USERNAME'],
            recipients=[recipient],
            cc=[app.config['MAIL_USERNAME']]
        )
        msg.body = f"""
        Olá {employee_name},
        
        Seu ponto foi registrado com sucesso:
        
        Data/Hora: {date}
        Refinaria: {refinery}
        Pontos: {points}
        Observações: {observations}
        
        Atenciosamente,
        Sistema de Pontos
        """
        Thread(target=send_async_email, args=(app, msg)).start()

def export_weekly_reports():
    """Exporta relatórios em Excel"""
    employees = Employee.query.all()
    zip_buffer = BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        for employee in employees:
            entries = Entry.query.filter_by(employee_id=employee.id).all()
            
            if entries:
                data = [{
                    'Data': entry.date,
                    'Refinaria': entry.refinery,
                    'Pontos': entry.points,
                    'Observações': entry.observations
                } for entry in entries]
                
                df = pd.DataFrame(data)
                total_points = df['Pontos'].sum()
                remaining_points = max(0, employee.weekly_goal - total_points)
                
                progress_row = {
                    'Data': 'Total',
                    'Refinaria': '',
                    'Pontos': total_points,
                    'Observações': f'Restante: {remaining_points}'
                }
                df = df._append(progress_row, ignore_index=True)
                
                excel_file = BytesIO()
                with pd.ExcelWriter(excel_file, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False, sheet_name=employee.name)
                    
                    workbook = writer.book
                    worksheet = writer.sheets[employee.name]
                    
                    header_format = workbook.add_format({
                        'bold': True,
                        'bg_color': '#4F81BD',
                        'font_color': 'white',
                        'border': 1
                    })
                    
                    for col_num, value in enumerate(df.columns.values):
                        worksheet.write(0, col_num, value, header_format)
                    
                    for i, col in enumerate(df.columns):
                        max_len = max(df[col].astype(str).apply(len).max(), len(col)) + 2
                        worksheet.set_column(i, i, max_len)
                
                excel_file.seek(0)
                zip_file.writestr(f"{employee.name}.xlsx", excel_file.read())
    
    zip_buffer.seek(0)
    return send_file(zip_buffer, as_attachment=True, download_name='relatorios_funcionarios.zip', mimetype='application/zip')

# Rotas
@app.route('/')
def index():
    """Página inicial com opções de login"""
    return render_template('index.html')

@app.route('/employee_login', methods=['GET', 'POST'])
def employee_login():
    """Login de funcionário com chave de acesso"""
    if request.method == 'POST':
        access_key = request.form['access_key']
        employee = Employee.query.filter_by(access_key=access_key).first()
        
        if employee:
            session['role'] = 'employee'
            session['employee_id'] = employee.id
            return redirect(url_for('employee_dashboard'))
        else:
            flash('Chave de acesso inválida', 'error')
    
    return render_template('employee_login.html')

@app.route('/employee_dashboard', methods=['GET', 'POST'])
def employee_dashboard():
    """Painel do funcionário"""
    if 'role' not in session or session['role'] != 'employee':
        return redirect(url_for('index'))
    
    employee = Employee.query.get(session['employee_id'])
    
    if request.method == 'POST':
        try:
            new_entry = Entry(
                employee_id=employee.id,
                date=datetime.now(timezone).strftime('%Y-%m-%d %H:%M:%S'),
                refinery=request.form['refinery'],
                points=int(request.form['points']),
                observations=request.form['observations']
            )
            db.session.add(new_entry)
            db.session.commit()
            
            send_confirmation_email(
                employee.name,
                new_entry.date,
                new_entry.points,
                new_entry.refinery,
                new_entry.observations
            )
            
            flash('Registro adicionado com sucesso!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Erro ao adicionar registro', 'error')
        
        return redirect(url_for('employee_dashboard'))
    
    entries = Entry.query.filter_by(employee_id=employee.id).order_by(Entry.date.desc()).all()
    return render_template('employee_dashboard.html', employee=employee, entries=entries)

@app.route('/delete_entry/<int:entry_id>', methods=['POST'])
def delete_entry(entry_id):
    """Exclusão de registro"""
    if 'role' not in session or session['role'] != 'employee':
        return redirect(url_for('index'))
    
    entry = Entry.query.get_or_404(entry_id)
    if entry.employee_id == session['employee_id']:
        db.session.delete(entry)
        db.session.commit()
        flash('Registro excluído com sucesso!', 'success')
    
    return redirect(url_for('employee_dashboard'))

# Rotas do CEO
@app.route('/ceo_login', methods=['GET', 'POST'])
def ceo_login():
    """Login do CEO"""
    if request.method == 'POST':
        if request.form['username'] == "Luis" and request.form['password'] == "Moni4242":
            session['role'] = 'ceo'
            return redirect(url_for('ceo_dashboard'))
        flash('Credenciais inválidas', 'error')
    return render_template('ceo_login.html')

@app.route('/ceo_dashboard')
def ceo_dashboard():
    """Painel do CEO"""
    if 'role' not in session or session['role'] != 'ceo':
        return redirect(url_for('index'))
    
    employee_id = request.args.get('employee_id')
    entries = Entry.query.filter_by(employee_id=employee_id).all() if employee_id else Entry.query.all()
    return render_template('ceo_dashboard.html', 
                         employees=Employee.query.all(),
                         entries=entries,
                         selected_employee_id=employee_id)

@app.route('/add_employee', methods=['GET', 'POST'])
def add_employee():
    """Adicionar novo funcionário"""
    if 'role' not in session or session['role'] != 'ceo':
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        try:
            new_employee = Employee(
                name=request.form['name'],
                weekly_goal=int(request.form.get('weekly_goal', 800)),
                access_key=request.form['access_key']
            )
            db.session.add(new_employee)
            db.session.commit()
            flash('Funcionário adicionado com sucesso!', 'success')
            return redirect(url_for('ceo_dashboard'))
        except Exception as e:
            db.session.rollback()
            flash('Erro ao adicionar funcionário', 'error')
    
    return render_template('add_employee.html')

@app.route('/delete_all_entries', methods=['POST'])
def delete_all_entries():
    """Excluir todos os registros"""
    if 'role' not in session or session['role'] != 'ceo':
        return redirect(url_for('index'))
    
    employee_id = request.form.get('employee_id')
    
    try:
        if employee_id and employee_id not in ['None', '']:
            Entry.query.filter_by(employee_id=int(employee_id)).delete()
        else:
            Entry.query.delete()
        db.session.commit()
        flash('Registros excluídos com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Erro ao excluir registros', 'error')
    
    return redirect(url_for('ceo_dashboard'))

@app.route('/export')
def export():
    """Exportar dados para Excel"""
    if 'role' not in session or session['role'] != 'ceo':
        return redirect(url_for('index'))
    return export_weekly_reports()

# Inicialização
if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true')