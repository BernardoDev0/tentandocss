#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de teste para verificar se a correção da Semana 5 funcionou
Testa se os 523 pontos do Maurício agora aparecem na Semana 5
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import db, Employee, Entry
from utils.calculations import calculate_weekly_progress, get_week_dates
from app import app  # Importar app diretamente
from datetime import datetime

def test_week5_fix():
    """Testa se a correção da Semana 5 funcionou"""
    
    with app.app_context():  # Usar app diretamente
        print("=== TESTE DA CORREÇÃO DA SEMANA 5 ===")
        print()
        
        # 1. Buscar o Maurício
        mauricio = Employee.query.filter_by(name='Maurício').first()
        if not mauricio:
            print("❌ ERRO: Maurício não encontrado no banco de dados")
            return False
            
        print(f"✅ Maurício encontrado - ID: {mauricio.id}")
        
        # 2. Verificar registro de 25/08/2025
        entry_25_08 = Entry.query.filter(
            Entry.employee_id == mauricio.id,
            Entry.date.like('2025-08-25%')
        ).first()
        
        if not entry_25_08:
            print("❌ ERRO: Registro de 25/08/2025 não encontrado")
            return False
            
        print(f"✅ Registro de 25/08 encontrado - Pontos: {entry_25_08.points}")
        print(f"   Data completa: {entry_25_08.date}")
        
        # 3. Obter datas da Semana 5
        start_date, end_date = get_week_dates('5')
        
        print(f"✅ Semana 5: {start_date} até {end_date}")
        
        # 4. Testar a função calculate_weekly_progress CORRIGIDA
        print("\n=== TESTANDO FUNÇÃO CORRIGIDA ===")
        
        weekly_data = calculate_weekly_progress('5', mauricio.id)
        
        print(f"Resultado da função calculate_weekly_progress:")
        print(f"  - Pontos da Semana 5: {weekly_data}")
        
        # 5. Verificar se os 523 pontos estão incluídos
        expected_points = entry_25_08.points
        
        # A função retorna um dicionário com nome do funcionário
        mauricio_points = weekly_data.get(mauricio.real_name, 0)
        
        print("\n=== RESULTADO DO TESTE ===")
        
        if mauricio_points >= expected_points:
            print(f"✅ SUCESSO! Os {expected_points} pontos estão sendo contabilizados na Semana 5")
            print(f"   Pontos esperados: {expected_points}")
            print(f"   Pontos calculados: {mauricio_points}")
            return True
        else:
            print(f"❌ FALHA! Os pontos não estão sendo contabilizados corretamente")
            print(f"   Esperado pelo menos: {expected_points}")
            print(f"   Calculado: {mauricio_points}")
            return False

def test_date_comparison():
    """Testa especificamente a comparação de datas"""
    
    print("\n=== TESTE DE COMPARAÇÃO DE DATAS ===")
    
    # Simular o problema anterior
    date_with_time = "2025-08-25 11:59:50"
    date_only = "2025-08-25"
    
    print(f"Data com hora: '{date_with_time}'")
    print(f"Data apenas: '{date_only}'")
    print(f"Comparação string: '{date_with_time}' <= '{date_only}' = {date_with_time <= date_only}")
    
    # Mostrar como a correção resolve
    from datetime import datetime
    date_obj = datetime.strptime(date_with_time, "%Y-%m-%d %H:%M:%S").date()
    date_only_obj = datetime.strptime(date_only, "%Y-%m-%d").date()
    
    print(f"Comparação com .date(): {date_obj} <= {date_only_obj} = {date_obj <= date_only_obj}")
    
if __name__ == "__main__":
    print("🧪 Iniciando teste da correção da Semana 5...\n")
    
    # Teste de comparação de datas
    test_date_comparison()
    
    # Teste principal
    success = test_week5_fix()
    
    print("\n" + "="*50)
    if success:
        print("🎉 TESTE PASSOU! A correção funcionou corretamente.")
        print("   Os 523 pontos do Maurício agora aparecem na Semana 5.")
    else:
        print("💥 TESTE FALHOU! A correção precisa ser revisada.")
    print("="*50)