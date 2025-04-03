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
    weekly_goal = db.Column(db.Integer, default=2375)
    access_key = db.Column(db.String(50), unique=True, nullable=False)
    default_refinery = db.Column(db.String(100))  # Nova coluna
    entries = db.relationship('Entry', backref='employee', lazy=True)

    @property
    def monthly_goal(self):
        return 9500  # Meta mensal fixa
    
    @property
    def daily_goal(self):
        return 475  # Meta diária fixa (2375/5)

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
        db.drop_all()
        db.create_all()
        create_initial_employees()

def create_initial_employees():
    """Cria os funcionários iniciais"""
    employees = [
        {'name': 'Rodrigo', 'weekly_goal': 2375, 'access_key': 'rodrigo123', 'default_refinery': 'RECAP'},
        {'name': 'Maurício', 'weekly_goal': 2375, 'access_key': 'mauricio123', 'default_refinery': 'REVAP'},
        {'name': 'Matheus', 'weekly_goal': 2375, 'access_key': 'matheus123', 'default_refinery': 'RPBC'},
        {'name': 'Wesley', 'weekly_goal': 2375, 'access_key': 'wesley123', 'default_refinery': 'REPLAN'}
    ]
    
    for emp in employees:
        if not Employee.query.filter_by(name=emp['name']).first():
            new_employee = Employee(
                name=emp['name'],
                weekly_goal=emp['weekly_goal'],
                access_key=emp['access_key'],
                default_refinery=emp['default_refinery']
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
        'Wesley'
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
                remaining_weekly = max(0, employee.weekly_goal - total_points)
                remaining_monthly = max(0, employee.monthly_goal - total_points)
                
                progress_row = {
                    'Data': 'Total',
                    'Refinaria': '',
                    'Pontos': total_points,
                    'Observações': f'Restante semanal: {remaining_weekly} | Restante mensal: {remaining_monthly}'
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


def get_current_week():
    """Retorna a semana atual do mês (1-4)"""
    today = datetime.now(timezone)
    first_day = today.replace(day=1)
    week_number = (today - first_day).days // 7 + 1
    return min(week_number, 4)  # Limita a 4 semanas

def get_week_from_date(date_str):
    """Retorna a semana do mês (1-4) baseada na data"""
    date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
    first_day = date.replace(day=1)
    week_number = (date - first_day).days // 7 + 1
    return min(week_number, 4)

class MonthReset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reset_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

# Rotas
@app.route('/')
def index():
    """Página inicial"""
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login único para todos os usuários"""
    if request.method == 'POST':
        try:
            # Verifica se os campos foram preenchidos
            if not request.form.get('usuario') or not request.form.get('senha'):
                flash('Por favor, preencha todos os campos', 'error')
                return redirect(url_for('login'))
                
            username = request.form['usuario'].strip()
            password = request.form['senha'].strip()
            
            # Verifica se é CEO
            if username == "Luis" and password == "Moni4242":
                session.clear()
                session['role'] = 'ceo'
                session['user'] = username
                return redirect(url_for('ceo_dashboard'))
            
            # Verifica se é funcionário (com tratamento case-insensitive)
            employee = Employee.query.filter(
                db.func.lower(Employee.name) == username.lower(),
                Employee.access_key == password
            ).first()
            
            if employee:
                session.clear()
                session['role'] = 'employee'
                session['employee_id'] = employee.id
                session['employee_name'] = employee.name
                return redirect(url_for('employee_dashboard'))
            
            flash('Usuário ou senha inválidos', 'error')
            return redirect(url_for('login'))
        
        except Exception as e:
            app.logger.error(f"Erro durante o login: {str(e)}")
            flash('Ocorreu um erro durante o login. Por favor, tente novamente.', 'error')
            return redirect(url_for('login'))
    
    return render_template('login.html')

@app.route('/employee_dashboard', methods=['GET', 'POST'])
def employee_dashboard():
    if 'role' not in session or session['role'] != 'employee':
        return redirect(url_for('index'))
    
    try:
        employee = db.session.get(Employee, session['employee_id'])
        if not employee:
            session.clear()
            flash('Sessão inválida. Por favor, faça login novamente.', 'error')
            return redirect(url_for('index'))
        
        if request.method == 'POST':
            try:
                points = int(request.form['points'])
                if points < 0:
                    raise ValueError("Pontos não podem ser negativos")
                    
                new_entry = Entry(
                    employee_id=employee.id,
                    date=datetime.now(timezone).strftime('%Y-%m-%d %H:%M:%S'),
                    refinery=request.form['refinery'],
                    points=points,
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
                return redirect(url_for('employee_dashboard'))
                
            except ValueError:
                db.session.rollback()
                flash('Por favor, insira um valor válido para os pontos', 'error')
            except Exception as e:
                db.session.rollback()
                app.logger.error(f"Erro ao adicionar registro: {str(e)}")
                flash('Erro ao adicionar registro', 'error')
        
        entries = Entry.query.filter_by(employee_id=employee.id).order_by(Entry.date.desc()).all()
        return render_template('employee_dashboard.html', 
                            employee=employee, 
                            entries=entries,
                            default_refinery=employee.default_refinery) 
        
    except Exception as e:
        app.logger.error(f"Erro no dashboard do funcionário: {str(e)}")
        session.clear()
        flash('Ocorreu um erro ao acessar o painel. Por favor, faça login novamente.', 'error')
        return redirect(url_for('index'))

@app.route('/edit_entry/<int:entry_id>', methods=['GET', 'POST'])
def edit_entry(entry_id):
    if 'role' not in session or session['role'] != 'ceo':
        flash('Acesso não autorizado', 'error')
        return redirect(url_for('index'))
    
    entry = Entry.query.get_or_404(entry_id)
    
    if request.method == 'POST':
        try:
            entry.refinery = request.form['refinery']
            entry.points = int(request.form['points'])
            entry.observations = request.form['observations']
            db.session.commit()
            flash('Registro atualizado com sucesso!', 'success')
            return redirect(url_for('ceo_dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar registro: {str(e)}', 'error')
    
    return render_template('edit_entry.html', entry=entry)

@app.route('/delete_entry/<int:entry_id>', methods=['POST'])
def delete_entry(entry_id):
    """Exclusão de registro"""
    if 'role' not in session or session['role'] != 'ceo':  # Alterado de 'employee' para 'ceo'
        flash('Acesso não autorizado', 'error')
        return redirect(url_for('index'))
    
    try:
        entry = Entry.query.get_or_404(entry_id)
        db.session.delete(entry)
        db.session.commit()
        flash('Registro excluído com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir registro: {str(e)}', 'error')
    
    return redirect(url_for('ceo_dashboard'))  # Redireciona de volta para o dashboard do CEO

@app.route('/ceo_dashboard')
def ceo_dashboard():
    if 'role' not in session or session['role'] != 'ceo':
        return redirect(url_for('index'))
    
    employee_id = request.args.get('employee_id')
    selected_week = request.args.get('week', str(get_current_week()))
    
    # Filtros
    entries_query = Entry.query
    if employee_id:
        entries_query = entries_query.filter_by(employee_id=employee_id)
    
    # Aplica filtro de semana
    all_entries = entries_query.all()
    entries = [e for e in all_entries if get_week_from_date(e.date) == int(selected_week)]
    
    # Cálculos
    employees = Employee.query.all()
    employee_totals = {}
    weekly_goal = 2375
    monthly_goal = 9500
    
    # Obtém a data do último reset ou usa 1º dia do mês atual como padrão
    reset_date_str = session.get('last_reset')
    if reset_date_str:
        reset_date = timezone.localize(datetime.strptime(reset_date_str, '%Y-%m-%d %H:%M:%S'))
    else:
        reset_date = timezone.localize(datetime.now().replace(day=1, hour=0, minute=0, second=0))

    for employee in employees:
        weekly_points = [0, 0, 0, 0]
        monthly_total = 0
        
        for entry in Entry.query.filter_by(employee_id=employee.id).all():
            entry_date = timezone.localize(datetime.strptime(entry.date, '%Y-%m-%d %H:%M:%S'))
            if entry_date >= reset_date:
                week = get_week_from_date(entry.date)
                weekly_points[week-1] += entry.points
                monthly_total += entry.points
        
        # Progresso da semana selecionada
        current_week_points = weekly_points[int(selected_week)-1]
        weekly_percentage = min((current_week_points / weekly_goal) * 100, 100)
        monthly_percentage = min((monthly_total / monthly_goal) * 100, 100)
        
        # Status de cor
        status_color = "green" if weekly_percentage >= 100 else "orange" if weekly_percentage >= 50 else "red"

        
        employee_totals[employee.id] = {
            'weekly_points': weekly_points,
            'current_week_points': current_week_points,
            'weekly_percentage': weekly_percentage,
            'monthly_total': monthly_total,
            'monthly_percentage': monthly_percentage,
            'status_color': status_color
        }
    
    return render_template('ceo_dashboard.html',
                         employees=employees,
                         entries=entries,
                         employee_totals=employee_totals,
                         selected_employee_id=employee_id,
                         selected_week=selected_week,
                         weekly_goal=weekly_goal,
                         monthly_goal=monthly_goal,
                         last_reset=reset_date_str)

# Mantenha a rota reset_month como está
@app.route('/reset_month', methods=['POST'])
def reset_month():
    if 'role' not in session or session['role'] != 'ceo':
        return redirect(url_for('index'))
    
    try:
        # Armazena o momento atual do reset na sessão
        session['last_reset'] = datetime.now(timezone).strftime('%Y-%m-%d %H:%M:%S')
        flash('Progresso resetado com sucesso! As metas começam a ser contadas a partir de agora.', 'success')
    except Exception as e:
        flash(f'Erro ao resetar o progresso: {str(e)}', 'error')
    
    return redirect(url_for('ceo_dashboard'))

@app.route('/add_employee', methods=['GET', 'POST'])
def add_employee():
    """Adicionar novo funcionário"""
    if 'role' not in session or session['role'] != 'ceo':
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        try:
            new_employee = Employee(
                name=request.form['name'],
                weekly_goal=int(request.form.get('weekly_goal', 2375)),
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
    with app.app_context():
        db.create_all()
        create_initial_employees()
    app.run(host='0.0.0.0', debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true')