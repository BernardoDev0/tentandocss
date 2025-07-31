#!/usr/bin/env python3
"""
Script para testar o processamento de dados
"""

from app import app
from utils.data_processing import get_weekly_progress_data, get_monthly_evolution_data, get_daily_data

def test_data_processing():
    """Testar processamento de dados"""
    
    with app.app_context():
        print("🧪 TESTANDO PROCESSAMENTO DE DADOS...")
        
        # Testar dados semanais
        print("\n📊 DADOS SEMANAIS:")
        weekly_data = get_weekly_progress_data()
        print(f"Labels: {weekly_data.get('labels', [])}")
        print(f"Datasets: {len(weekly_data.get('datasets', []))}")
        
        for dataset in weekly_data.get('datasets', []):
            print(f"  {dataset['label']}: {dataset['data']}")
        
        # Testar dados mensais
        print("\n📊 DADOS MENSAIS:")
        monthly_data = get_monthly_evolution_data()
        print(f"Labels: {monthly_data.get('labels', [])}")
        print(f"Datasets: {len(monthly_data.get('datasets', []))}")
        
        for dataset in monthly_data.get('datasets', []):
            print(f"  {dataset['label']}: {dataset['data']}")
        
        # Testar dados diários
        print("\n📊 DADOS DIÁRIOS:")
        daily_data = get_daily_data()
        print(f"Labels: {daily_data.get('labels', [])}")
        print(f"Datasets: {len(daily_data.get('datasets', []))}")
        
        for dataset in daily_data.get('datasets', []):
            print(f"  {dataset['label']}: {dataset['data']}")

if __name__ == "__main__":
    test_data_processing() 