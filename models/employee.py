from . import db

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))  # Campo legado
    real_name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    role = db.Column(db.String(50), default='Funcionário')  # Voltando ao nome original
    access_key = db.Column(db.String(50), nullable=False)
    default_refinery = db.Column(db.String(100))
    entries = db.relationship('Entry', backref='employee', lazy=True)
    
    @property
    def weekly_goal(self):
        # Meta semanal específica para o Matheus (E89P)
        if self.username == 'E89P':
            return 2675  # Corrigido de 2625 para 2675
        return 2375  # Meta semanal padrão para os outros
    
    @property
    def daily_goal(self):
        # Meta diária específica para o Matheus (E89P)
        if self.username == 'E89P':
            return 535  # Corrigido de 525 para 535 (2675/5)
        return 475  # Meta diária padrão para os outros (2375/5)
    
    @property
    def monthly_goal(self):
        """Meta mensal baseada na meta semanal"""
        if self.username == 'E89P':
            return 10500  # Corresponde ao valor usado no dashboard
        return 9500  # Corresponde ao valor usado no dashboard
    
    @property
    def display_role(self):
        """Sempre retorna 'Funcionário' independente do valor no banco"""
        return 'Funcionário'
    
    @property
    def employee_role(self):  # Renomeei a propriedade para evitar conflito
        return 'funcionário'
    
    def __repr__(self):
        return f'<Employee {self.real_name}>'
