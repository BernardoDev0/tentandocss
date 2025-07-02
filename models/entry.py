from . import db
from datetime import datetime
import pytz

class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    refinery = db.Column(db.String(100), nullable=False)
    points = db.Column(db.BigInteger, nullable=False)
    observations = db.Column(db.Text)
    
    @property
    def timestamp(self):
        """Converte a data string para datetime"""
        try:
            timezone = pytz.timezone('America/Sao_Paulo')
            date_obj = datetime.strptime(self.date, '%Y-%m-%d')
            return timezone.localize(date_obj)
        except:
            return datetime.now(pytz.timezone('America/Sao_Paulo'))
    
    def __repr__(self):
        return f'<Entry {self.employee.real_name} - {self.date} - {self.points}>'