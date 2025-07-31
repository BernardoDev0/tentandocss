#!/usr/bin/env python3
"""
Script para limpar arquivos de performance desnecessários
"""

import os
import glob

def cleanup_performance_files():
    """Limpar arquivos de performance desnecessários"""
    
    print("🧹 LIMPANDO ARQUIVOS DE PERFORMANCE...")
    
    # Lista de arquivos para remover
    files_to_remove = [
        # Relatórios de performance
        'performance_report_*.json',
        'optimization_report_*.json',
        
        # Arquivos de auditoria
        'performance-audit.html',
        'performance-test.html',
        
        # Relatórios markdown
        'PERFORMANCE_AUDIT_REPORT.md',
        'PERFORMANCE_MIGRATION_PLAN.md',
        'SOLUCAO_PERFORMANCE_FINAL.md',
        'RELATORIO_BACKGROUND_FIX.md',
        'RESUMO_OTIMIZACOES.md',
        
        # Scripts de performance
        'apply_optimizations.py',
        'performance_monitor.py',
        'analyze_db.py',
        'profile_app.py',
        
        # Arquivos de cache
        '__pycache__/*',
        '*.pyc',
        '*.pyo'
    ]
    
    removed_count = 0
    
    for pattern in files_to_remove:
        files = glob.glob(pattern)
        for file_path in files:
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    print(f"✅ Removido: {file_path}")
                    removed_count += 1
                elif os.path.isdir(file_path):
                    import shutil
                    shutil.rmtree(file_path)
                    print(f"✅ Removido diretório: {file_path}")
                    removed_count += 1
            except Exception as e:
                print(f"❌ Erro ao remover {file_path}: {e}")
    
    print(f"\n🎉 LIMPEZA CONCLUÍDA!")
    print(f"📊 Total de arquivos removidos: {removed_count}")
    
    # Manter apenas os arquivos essenciais
    essential_files = [
        'static/css/emergency-patch.css',
        'static/css/background-fix.css',
        'static/js/chart-optimized.js',
        'static/js/performance-diagnostic.js',
        'apply-performance-fixes.py'
    ]
    
    print(f"\n📋 ARQUIVOS ESSENCIAIS MANTIDOS:")
    for file_path in essential_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"⚠️ {file_path} (não encontrado)")

def main():
    """Função principal"""
    
    print("=" * 50)
    print("🧹 LIMPADOR DE ARQUIVOS DE PERFORMANCE")
    print("=" * 50)
    
    # Confirmar antes de limpar
    response = input("\n⚠️ ATENÇÃO: Isso vai remover vários arquivos de performance.\nDeseja continuar? (s/N): ")
    
    if response.lower() in ['s', 'sim', 'y', 'yes']:
        cleanup_performance_files()
        print("\n✅ Limpeza concluída com sucesso!")
    else:
        print("\n❌ Operação cancelada pelo usuário")

if __name__ == "__main__":
    main() 