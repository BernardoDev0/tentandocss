#!/usr/bin/env python3
"""
Script para testar os dados do dashboard
"""

from app import app
from utils.calculations import calculate_weekly_progress, calculate_monthly_progress
from models import Employee

def test_dashboard_data():
    """Testar dados do dashboard"""
    
    with app.app_context():
        print("🧪 TESTANDO DADOS DO DASHBOARD...")
        
        # Testar dados semanais
        print("\n📊 DADOS SEMANAIS (calculate_weekly_progress):")
        weekly_data = calculate_weekly_progress(None, 1)  # Semana 1, todos os funcionários
        print(f"Resultado: {weekly_data}")
        
        # Testar dados mensais
        print("\n📊 DADOS MENSAIS (calculate_monthly_progress):")
        monthly_data = calculate_monthly_progress(None, 7, 2025)  # Julho 2025
        print(f"Resultado: {monthly_data}")
        
        # Verificar funcionários
        print("\n👥 FUNCIONÁRIOS:")
        employees = Employee.query.all()
        for emp in employees:
            print(f"  - {emp.real_name} (ID: {emp.id})")
        
        # Simular o que o dashboard faz
        print("\n🔍 SIMULAÇÃO DO DASHBOARD:")
        employee_totals = {}
        for emp in employees:
            name = emp.real_name
            weekly_points = weekly_data.get(name, 0)
            monthly_points = monthly_data.get(name, 0)
            weekly_goal = emp.weekly_goal or 1
            monthly_goal = emp.monthly_goal or 1
            
            print(f"  {name}:")
            print(f"    Semanal: {weekly_points} / {weekly_goal} pts")
            print(f"    Mensal: {monthly_points} / {monthly_goal} pts")

if __name__ == "__main__":
    test_dashboard_data() 