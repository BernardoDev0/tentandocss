from flask import Flask, render_template, request, redirect, url_for, session, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from datetime import datetime, timedelta
from io import BytesIO
import zipfile
import pandas as pd
import pytz
import os
from dotenv import load_dotenv
from threading import Thread

# Load environment variables
load_dotenv()

# Flask configuration
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', '3a2a136cee90c4375c8b759a65591c1a8f30145874ef8881146f16c29f599183')

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL').replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Email configuration
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
mail = Mail(app)
mail.init_app(app)

# Set timezone to Brasilia
os.environ['TZ'] = 'America/Sao_Paulo'
timezone = pytz.timezone('America/Sao_Paulo')

# Employee emails
EMPLOYEE_EMAILS = {
    'Rodrigo': 'rodrigo@monitorarconsultoria.com.br',
    'Maurício': 'carlos.mauricio.prestserv@petrobras.com.br',
    'Matheus': 'Matheus.e.lima.prestserv@petrobras.com.br'
}

# Database models
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
    points = db.Column(db.BigInteger, nullable=False)
    observations = db.Column(db.String(200), nullable=False)

# Initialize database
def init_db():
    with app.app_context():
        db.create_all()
        add_initial_employees()

def add_initial_employees():
    employees = [
        {'name': 'Rodrigo', 'weekly_goal': 800, 'access_key': 'rodrigo123'},
        {'name': 'Maurício', 'weekly_goal': 800, 'access_key': 'mauricio123'},
        {'name': 'Matheus', 'weekly_goal': 800, 'access_key': 'matheus123'}
    ]
    for emp in employees:
        existing = Employee.query.filter_by(name=emp['name']).first()
        if not existing:
            new_employee = Employee(
                name=emp['name'],
                weekly_goal=emp['weekly_goal'],
                access_key=emp['access_key']
            )
            db.session.add(new_employee)
    db.session.commit()

def get_week_range(date):
    start_of_week = date - timedelta(days=date.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    return start_of_week.strftime('%Y-%m-%d'), end_of_week.strftime('%Y-%m-%d')

def send_async_email(app, msg):
    with app.app_context():
        try:
            mail.connect()
            mail.send(msg)
            app.logger.info("Email enviado com sucesso")
        except Exception as e:
            app.logger.error(f"Erro ao enviar email: {str(e)}")
            app.logger.error(f"Configurações SMTP: {app.config['MAIL_SERVER']}:{app.config['MAIL_PORT']}")
            app.logger.error(f"Usuário: {app.config['MAIL_USERNAME']}")

def send_confirmation_email(employee_name, date, points, refinery, observations):
    recipient = EMPLOYEE_EMAILS.get(employee_name)
    if not recipient:
        return False
    
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
    return True

def export_weekly_reports():
    employees = Employee.query.all()
    zip_buffer = BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        for employee in employees:
            entries = Entry.query.filter_by(employee_id=employee.id).all()
            
            if entries:
                data = [{
                    'id': entry.id,
                    'employee_id': entry.employee_id,
                    'date': entry.date,
                    'refinery': entry.refinery,
                    'points': entry.points,
                    'observations': entry.observations
                } for entry in entries]
                
                df = pd.DataFrame(data)
                total_points = df['points'].sum()
                remaining_points = max(0, employee.weekly_goal - total_points)
                
                progress_row = {
                    'id': '',
                    'employee_id': '',
                    'date': 'Total',
                    'refinery': '',
                    'points': total_points,
                    'observations': f'Restante: {remaining_points}'
                }
                df = df._append(progress_row, ignore_index=True)
                
                df.rename(columns={
                    'id': 'ID',
                    'employee_id': 'ID do Funcionário',
                    'date': 'Data',
                    'refinery': 'Refinaria',
                    'points': 'Pontos',
                    'observations': 'Observações'
                }, inplace=True)
                
                excel_file = BytesIO()
                writer = pd.ExcelWriter(excel_file, engine='xlsxwriter')
                df.to_excel(writer, index=False, sheet_name=employee.name)
                
                workbook = writer.book
                worksheet = writer.sheets[employee.name]
                
                header_format = workbook.add_format({
                    'bold': True,
                    'text_wrap': True,
                    'valign': 'top',
                    'fg_color': '#4F81BD',
                    'font_color': 'white',
                    'font_size': 12,
                    'border': 1
                })
                
                total_format = workbook.add_format({
                    'bold': True,
                    'fg_color': '#C5D9F1',
                    'font_size': 12,
                    'border': 1
                })
                
                for col_num, value in enumerate(df.columns.values):
                    worksheet.write(0, col_num, value, header_format)
                
                last_row = len(df)
                for col_num in range(len(df.columns)):
                    worksheet.write(last_row, col_num, df.iloc[-1, col_num], total_format)
                
                for i, col in enumerate(df.columns):
                    max_len = max(df[col].astype(str).apply(len).max(), len(col)) + 2
                    worksheet.set_column(i, i, max_len)
                
                writer.close()
                excel_file.seek(0)
                zip_file.writestr(f"{employee.name}.xlsx", excel_file.read())
    
    zip_buffer.seek(0)
    return send_file(zip_buffer, as_attachment=True, download_name='relatorios_funcionarios.zip', mimetype='application/zip')

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/employee_login/<access_key>')
def employee_private_login(access_key):
    employee = Employee.query.filter_by(access_key=access_key).first()
    if not employee:
        return redirect(url_for('index'))
    session['role'] = 'employee'
    session['employee_id'] = employee.id
    return redirect(url_for('employee_dashboard'))

@app.route('/employee_dashboard', methods=['GET', 'POST'])
def employee_dashboard():
    if session.get('role') != 'employee':
        return redirect(url_for('index'))
    
    employee_id = session.get('employee_id')
    employee = Employee.query.get(employee_id)
    
    if request.method == 'POST':
        refinery = request.form['refinery']
        points = request.form['points']
        observations = request.form['observations']
        date = datetime.now(timezone).strftime('%Y-%m-%d %H:%M:%S')
        
        new_entry = Entry(
            employee_id=employee_id,
            date=date,
            refinery=refinery,
            points=points,
            observations=observations
        )
        db.session.add(new_entry)
        db.session.commit()
        
        send_confirmation_email(
            employee_name=employee.name,
            date=date,
            points=points,
            refinery=refinery,
            observations=observations
        )
        
        return redirect(url_for('employee_dashboard'))
    
    entries = Entry.query.filter_by(employee_id=employee_id).order_by(Entry.date.desc()).all()
    return render_template('employee_dashboard.html', employee=employee, entries=entries)

@app.route('/edit_entry/<int:entry_id>', methods=['GET', 'POST'])
def edit_entry(entry_id):
    if session.get('role') != 'employee':
        return redirect(url_for('index'))
    
    entry = Entry.query.get_or_404(entry_id)
    if entry.employee_id != session.get('employee_id'):
        return redirect(url_for('employee_dashboard'))
    
    if request.method == 'POST':
        entry.refinery = request.form['refinery']
        entry.points = request.form['points']
        entry.observations = request.form['observations']
        db.session.commit()
        return redirect(url_for('employee_dashboard'))
    
    return render_template('edit_entry.html', entry=entry)

@app.route('/delete_entry/<int:entry_id>', methods=['POST'])
def delete_entry(entry_id):
    if session.get('role') != 'employee':
        return redirect(url_for('index'))
    
    entry = Entry.query.get_or_404(entry_id)
    if entry.employee_id != session.get('employee_id'):
        return redirect(url_for('employee_dashboard'))
    
    db.session.delete(entry)
    db.session.commit()
    return redirect(url_for('employee_dashboard'))

@app.route('/ceo_login', methods=['GET', 'POST'])
def ceo_login():
    error = None

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username != "Luis":
            error = "Usuário incorreto"
        elif password != "Moni4242":
            error = "Senha incorreta"
        else:
            session['role'] = 'ceo'
            return redirect(url_for('ceo_dashboard'))

    return render_template('ceo_login.html', error=error)

@app.route('/ceo_dashboard')
def ceo_dashboard():
    if session.get('role') != 'ceo':
        return redirect(url_for('index'))
    
    selected_employee_id = request.args.get('employee_id')
    if selected_employee_id:
        entries = Entry.query.filter_by(employee_id=selected_employee_id).all()
    else:
        entries = Entry.query.all()
    
    employees = Employee.query.all()
    return render_template('ceo_dashboard.html', employees=employees, entries=entries, selected_employee_id=selected_employee_id)

@app.route('/add_employee', methods=['GET', 'POST'])
def add_employee():
    if session.get('role') != 'ceo':
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        name = request.form['name']
        weekly_goal = request.form.get('weekly_goal', 800)
        access_key = request.form['access_key']
        new_employee = Employee(name=name, weekly_goal=weekly_goal, access_key=access_key)
        db.session.add(new_employee)
        db.session.commit()
        return redirect(url_for('ceo_dashboard'))
    
    return render_template('add_employee.html')

@app.route('/delete_all_entries', methods=['POST'])
def delete_all_entries():
    if session.get('role') != 'ceo':
        return redirect(url_for('index'))

    selected_employee_id = request.form.get('employee_id')

    if not selected_employee_id or selected_employee_id in ['None', '']:
        Entry.query.delete()
    else:
        try:
            Entry.query.filter_by(employee_id=int(selected_employee_id)).delete()
        except ValueError:
            return "Erro: employee_id deve ser um número inteiro.", 400

    db.session.commit()
    return redirect(url_for('ceo_dashboard'))

@app.route('/export')
def export():
    if session.get('role') != 'ceo':
        return redirect(url_for('index'))
    return export_weekly_reports()

# Initialize database
init_db()

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true')