from app import app, db, Entry, Employee
from datetime import datetime

with app.app_context():
    # Busca o ID do Maurício de forma segura
    mauricio = Employee.query.filter_by(name='Maurício').first()
    
    if not mauricio:
        print("❌ Maurício não encontrado no banco de dados!")
    else:
        registros = [
            ('2025-03-26 19:00:00', 'REVAP', 0, 'Greve da Petrobrás'),
            ('2025-03-27 19:00:00', 'REVAP', 575, 'U-280'),
            ('2025-03-28 19:00:00', 'REVAP', 584, 'U-280'),
            ('2025-03-31 19:00:00', 'REVAP', 265, 'TERMINOU U-280'),
            ('2025-04-01 19:00:00', 'REVAP', 511, 'U-276'),
            ('2025-04-02 19:00:00', 'REVAP', 606, 'U-276'),
            ('2025-04-03 19:00:00', 'REVAP', 505, 'U-276'),
            ('2025-04-04 19:00:00', 'REVAP', 650, 'U-276'),
            ('2025-04-07 19:00:00', 'REVAP', 695, 'U-276')
        ]

        for date, refinery, points, obs in registros:
            new_entry = Entry(
                employee_id=mauricio.id,
                date=date,
                refinery=refinery,
                points=points,
                observations=obs
            )
            db.session.add(new_entry)
        
        db.session.commit()
        print(f"✅ {len(registros)} registros do Maurício inseridos com sucesso!")