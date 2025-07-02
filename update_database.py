from models import Employee, db
from app import app

with app.app_context():
    # Atualizar todos os registros com role='employee' para 'Funcionário'
    employees_to_update = Employee.query.filter_by(role='employee').all()
    
    for employee in employees_to_update:
        employee.role = 'Funcionário'
        print(f"Atualizando {employee.real_name}: role -> 'Funcionário'")
    
    db.session.commit()
    print(f"Atualizados {len(employees_to_update)} funcionários")