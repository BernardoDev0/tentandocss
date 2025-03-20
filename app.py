from flask import Flask, render_template, request, redirect, url_for, session, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from io import BytesIO
import zipfile
import pandas as pd
import pytz
import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Configuração do Flask
app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'  # Substitua por uma chave segura

# Configuração do banco de dados PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL').replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Configura o fuso horário de Brasília
os.environ['TZ'] = 'America/Sao_Paulo'
timezone = pytz.timezone('America/Sao_Paulo')

# Definição dos modelos do banco de dados
class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    weekly_goal = db.Column(db.Integer, default=800)
    entries = db.relationship('Entry', backref='employee', lazy=True)

class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    refinery = db.Column(db.String(100), nullable=False)
    points = db.Column(db.Integer, nullable=False)
    observations = db.Column(db.String(200), nullable=False)

# Inicialização do banco de dados
def init_db():
    with app.app_context():
        db.create_all()
        add_initial_employees()

# Adicionar funcionários iniciais
def add_initial_employees():
    employees = [
        {'name': 'Rodrigo', 'weekly_goal': 800},
        {'name': 'Maurício', 'weekly_goal': 800},
        {'name': 'Matheus', 'weekly_goal': 800}
    ]
    for emp in employees:
        existing = Employee.query.filter_by(name=emp['name']).first()
        if not existing:
            new_employee = Employee(name=emp['name'], weekly_goal=emp['weekly_goal'])
            db.session.add(new_employee)
    db.session.commit()

# Retorna o início (segunda-feira) e o fim (domingo) da semana da data fornecida
def get_week_range(date):
    start_of_week = date - timedelta(days=date.weekday())  # Segunda-feira
    end_of_week = start_of_week + timedelta(days=6)        # Domingo
    return start_of_week.strftime('%Y-%m-%d'), end_of_week.strftime('%Y-%m-%d')

# Exporta relatórios semanais
def export_weekly_reports():
    employees = Employee.query.all()
    
    # Cria o arquivo ZIP com os dados semanais
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        for employee in employees:
            entries = Entry.query.filter_by(employee_id=employee.id).all()
            
            if entries:
                # Cria o DataFrame com os dados
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
                
                # Adiciona uma linha com o progresso (em português)
                progress_row = {'id': '', 'employee_id': '', 'date': 'Total', 'refinery': '', 'points': total_points, 'observations': f'Restante: {remaining_points}'}
                df = df._append(progress_row, ignore_index=True)
                
                # Renomeia as colunas para português
                df.rename(columns={
                    'id': 'ID',
                    'employee_id': 'ID do Funcionário',
                    'date': 'Data',
                    'refinery': 'Refinaria',
                    'points': 'Pontos',
                    'observations': 'Observações'
                }, inplace=True)
                
                # Cria um escritor Excel do Pandas usando XlsxWriter como engine
                excel_file = BytesIO()
                writer = pd.ExcelWriter(excel_file, engine='xlsxwriter')
                df.to_excel(writer, index=False, sheet_name=employee.name)
                
                # Obtém os objetos workbook e worksheet do xlsxwriter
                workbook = writer.book
                worksheet = writer.sheets[employee.name]
                
                # Formato para o cabeçalho
                header_format = workbook.add_format({
                    'bold': True,
                    'text_wrap': True,
                    'valign': 'top',
                    'fg_color': '#4F81BD',  # Cor de fundo do cabeçalho
                    'font_color': 'white',  # Cor do texto do cabeçalho
                    'font_size': 12,  # Tamanho da fonte aumentado
                    'border': 1
                })
                
                # Formato para a linha de total
                total_format = workbook.add_format({
                    'bold': True,
                    'fg_color': '#C5D9F1',  # Cor de fundo da linha de total
                    'font_size': 12,  # Tamanho da fonte aumentado
                    'border': 1
                })
                
                # Escreve os cabeçalhos das colunas com o formato definido
                for col_num, value in enumerate(df.columns.values):
                    worksheet.write(0, col_num, value, header_format)
                
                # Aplica o formato de total à última linha
                last_row = len(df)
                for col_num in range(len(df.columns)):
                    worksheet.write(last_row, col_num, df.iloc[-1, col_num], total_format)
                
                # Ajusta a largura das colunas
                for i, col in enumerate(df.columns):
                    max_len = max(df[col].astype(str).apply(len).max(), len(col)) + 2
                    worksheet.set_column(i, i, max_len)
                
                # Fecha o escritor Excel do Pandas e prepara o arquivo para leitura
                writer.close()
                excel_file.seek(0)
                zip_file.writestr(f"{employee.name}.xlsx", excel_file.read())
    
    zip_buffer.seek(0)
    
    # Envia o arquivo ZIP como resposta para download
    return send_file(zip_buffer, as_attachment=True, download_name='relatorios_funcionarios.zip', mimetype='application/zip')

# Rotas do Flask
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/employee_login', methods=['GET', 'POST'])
def employee_login():
    if request.method == 'POST':
        # Autenticação simples (para fins de demonstração)
        session['role'] = 'employee'
        return redirect(url_for('employee_dashboard'))
    return render_template('employee_login.html')

@app.route('/ceo_login', methods=['GET', 'POST'])
def ceo_login():
    error = None  # Variável para armazenar mensagens de erro

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Valida o nome de usuário e a senha
        if username != "Luis":
            error = "Usuário incorreto"
        elif password != "Moni4242":
            error = "Senha incorreta"
        else:
            # Autenticação bem-sucedida
            session['role'] = 'ceo'
            return redirect(url_for('ceo_dashboard'))

    # Exibe a página de login com mensagens de erro, se houver
    return render_template('ceo_login.html', error=error)

@app.route('/add_employee', methods=['GET', 'POST'])
def add_employee():
    if session.get('role') != 'ceo':
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        name = request.form['name']
        weekly_goal = request.form.get('weekly_goal', 800)  # Meta semanal padrão é 800
        
        # Adiciona o novo funcionário ao banco de dados
        new_employee = Employee(name=name, weekly_goal=weekly_goal)
        db.session.add(new_employee)
        db.session.commit()
        return redirect(url_for('index'))
    
    return render_template('add_employee.html')

@app.route('/employee_dashboard', methods=['GET', 'POST'])
def employee_dashboard():
    if session.get('role') != 'employee':
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        employee_id = request.form['employee_id']
        refinery = request.form['refinery']
        points = request.form['points']
        observations = request.form['observations']
        date = datetime.now(timezone).strftime('%Y-%m-%d %H:%M:%S')
        
        # Adiciona uma nova entrada ao banco de dados
        new_entry = Entry(employee_id=employee_id, date=date, refinery=refinery, points=points, observations=observations)
        db.session.add(new_entry)
        db.session.commit()
        return redirect(url_for('employee_dashboard'))
    
    # Lista os funcionários para seleção
    employees = Employee.query.all()
    return render_template('employee_dashboard.html', employees=employees)

@app.route('/ceo_dashboard')
def ceo_dashboard():
    if session.get('role') != 'ceo':
        return redirect(url_for('index'))
    
    # Filtra os registros por funcionário, se especificado
    selected_employee_id = request.args.get('employee_id')
    if selected_employee_id:
        entries = Entry.query.filter_by(employee_id=selected_employee_id).all()
    else:
        entries = Entry.query.all()
    
    employees = Employee.query.all()
    return render_template('ceo_dashboard.html', employees=employees, entries=entries, selected_employee_id=selected_employee_id)

@app.route('/delete_entry/<int:entry_id>', methods=['POST'])
def delete_entry(entry_id):
    if session.get('role') != 'ceo':
        return redirect(url_for('index'))
    
    # Exclui a entrada do banco de dados
    entry = Entry.query.get_or_404(entry_id)
    db.session.delete(entry)
    db.session.commit()
    return redirect(url_for('ceo_dashboard'))

@app.route('/delete_all_entries', methods=['POST'])
def delete_all_entries():
    if session.get('role') != 'ceo':
        return redirect(url_for('index'))
    
    selected_employee_id = request.form.get('employee_id')
    if selected_employee_id:
        Entry.query.filter_by(employee_id=selected_employee_id).delete()
    else:
        Entry.query.delete()
    
    db.session.commit()
    return redirect(url_for('ceo_dashboard'))

@app.route('/export')
def export():
    if session.get('role') != 'ceo':
        return redirect(url_for('index'))
    return export_weekly_reports()

# Inicialização do banco de dados e adição de funcionários
init_db()

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)