#!/usr/bin/env python3
"""
Script para aplicar automaticamente as correções de performance
"""

import os
import shutil
import re
from pathlib import Path

def apply_emergency_fixes():
    """Aplicar correções emergenciais de performance"""
    
    print("🚀 APLICANDO CORREÇÕES DE PERFORMANCE...")
    
    # 1. Verificar se os arquivos existem
    files_to_check = [
        'static/css/emergency-patch.css',
        'static/css/background-fix.css',
        'static/js/chart-optimized.js',
        'static/js/performance-diagnostic.js'
    ]
    
    missing_files = []
    for file_path in files_to_check:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Arquivos não encontrados: {missing_files}")
        return False
    
    print("✅ Todos os arquivos de correção encontrados")
    
    # 2. Aplicar patch CSS no template principal
    template_path = 'templates/ceo_dashboard_enhanced.html'
    if os.path.exists(template_path):
        apply_css_patch(template_path)
    else:
        print(f"⚠️ Template não encontrado: {template_path}")
    
    # 3. Aplicar JavaScript otimizado
    js_files = [
        'static/ceo_dashboard.js',
        'static/employee_dashboard.js'
    ]
    
    for js_file in js_files:
        if os.path.exists(js_file):
            apply_js_optimizations(js_file)
    
    # 4. Criar script de teste
    create_test_script()
    
    print("✅ Correções aplicadas com sucesso!")
    print("\n📋 PRÓXIMOS PASSOS:")
    print("1. Reiniciar o servidor Flask")
    print("2. Abrir o dashboard no navegador")
    print("3. Verificar o painel de debug (canto superior direito)")
    print("4. Testar hover nos elementos para verificar FPS")
    print("5. Verificar se o background não fica branco no hover")
    
    return True

def apply_css_patch(template_path):
    """Aplicar patch CSS no template"""
    
    print(f"🔧 Aplicando patch CSS em {template_path}")
    
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Adicionar CSS emergencial no head
    css_links = [
        '<link rel="stylesheet" href="{{ url_for(\'static\', filename=\'css/emergency-patch.css\') }}">',
        '<link rel="stylesheet" href="{{ url_for(\'static\', filename=\'css/background-fix.css\') }}">'
    ]
    
    # Verificar se já foram adicionados
    for css_link in css_links:
        if css_link not in content:
            # Inserir após o último link CSS
            pattern = r'(</head>)'
            replacement = f'    {css_link}\n    \\1'
            content = re.sub(pattern, replacement, content)
            
            # Extrair nome do arquivo para exibição
            filename = css_link.split("filename='")[1].split("'")[0]
            print(f"✅ CSS adicionado ao template: {filename}")
        else:
            filename = css_link.split("filename='")[1].split("'")[0]
            print(f"ℹ️ CSS já está no template: {filename}")
    
    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(content)

def apply_js_optimizations(js_file):
    """Aplicar otimizações no JavaScript"""
    
    print(f"🔧 Otimizando {js_file}")
    
    with open(js_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Substituir criação de charts
    old_pattern = r'new Chart\(([^)]+)\)'
    new_pattern = r'createOptimizedChart(\1)'
    
    if re.search(old_pattern, content):
        content = re.sub(old_pattern, new_pattern, content)
        print("✅ Chart.js otimizado")
    
    # Adicionar imports se necessário
    if 'createOptimizedChart' in content and 'chart-optimized.js' not in content:
        # Adicionar comentário sobre import
        content = f'// IMPORTANTE: Adicionar <script src="static/js/chart-optimized.js"></script> no template\n{content}'
    
    with open(js_file, 'w', encoding='utf-8') as f:
        f.write(content)

def create_test_script():
    """Criar script de teste de performance"""
    
    test_script = '''<!DOCTYPE html>
<html>
<head>
    <title>Performance Test</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            padding: 20px; 
            background: #0f172a;
            color: #f8fafc;
        }
        .test-card { 
            background: rgba(15, 23, 42, 0.95); 
            padding: 20px; 
            margin: 10px; 
            border-radius: 8px;
            border: 1px solid rgba(148, 163, 184, 0.2);
            transition: all 0.3s ease;
        }
        .test-card:hover { 
            transform: translateY(-2px); 
            background: rgba(15, 23, 42, 0.95) !important;
        }
    </style>
</head>
<body>
    <h1>🧪 Teste de Performance</h1>
    
    <div class="test-card">
        <h3>Teste 1: Hover Effects</h3>
        <p>Passe o mouse sobre este card para testar FPS e background</p>
    </div>
    
    <div class="test-card">
        <h3>Teste 2: Chart.js</h3>
        <canvas id="testChart" width="400" height="200"></canvas>
    </div>
    
    <div id="performance-display" style="
        position: fixed;
        top: 10px;
        right: 10px;
        background: rgba(0,0,0,0.8);
        color: white;
        padding: 10px;
        border-radius: 5px;
        font-family: monospace;
    ">
        FPS: <span id="fps">--</span><br>
        Memory: <span id="memory">--</span><br>
        Background OK: <span id="background-status">✅</span>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="static/js/chart-optimized.js"></script>
    <script src="static/js/performance-diagnostic.js"></script>
    
    <script>
        // Teste de FPS
        let frameCount = 0;
        let lastTime = performance.now();
        
        function updateFPS() {
            frameCount++;
            const currentTime = performance.now();
            
            if (currentTime - lastTime >= 1000) {
                const fps = Math.round((frameCount * 1000) / (currentTime - lastTime));
                document.getElementById('fps').textContent = fps;
                
                if (performance.memory) {
                    const memoryMB = Math.round(performance.memory.usedJSHeapSize / 1024 / 1024);
                    document.getElementById('memory').textContent = memoryMB + 'MB';
                }
                
                frameCount = 0;
                lastTime = currentTime;
            }
            
            requestAnimationFrame(updateFPS);
        }
        
        updateFPS();
        
        // Teste de Chart.js
        const ctx = document.getElementById('testChart').getContext('2d');
        const chart = createOptimizedChart('testChart', {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
            datasets: [{
                label: 'Test Data',
                data: [12, 19, 3, 5, 2],
                borderColor: '#3b82f6',
                backgroundColor: 'rgba(59, 130, 246, 0.1)'
            }]
        });
        
        // Teste de background
        function checkBackground() {
            const cards = document.querySelectorAll('.test-card');
            let allGood = true;
            
            cards.forEach(card => {
                const style = window.getComputedStyle(card);
                const bg = style.backgroundColor;
                
                // Verificar se o background não é branco
                if (bg.includes('255, 255, 255') || bg.includes('white') || bg.includes('#fff')) {
                    allGood = false;
                    card.style.outline = '2px solid red';
                } else {
                    card.style.outline = 'none';
                }
            });
            
            document.getElementById('background-status').textContent = allGood ? '✅' : '❌';
            document.getElementById('background-status').style.color = allGood ? 'green' : 'red';
        }
        
        // Verificar background a cada segundo
        setInterval(checkBackground, 1000);
        checkBackground();
    </script>
</body>
</html>'''
    
    with open('performance-test.html', 'w', encoding='utf-8') as f:
        f.write(test_script)
    
    print("✅ Script de teste criado: performance-test.html")

def check_performance_metrics():
    """Verificar métricas de performance atuais"""
    
    print("\n📊 VERIFICANDO MÉTRICAS DE PERFORMANCE...")
    
    # Verificar arquivos CSS problemáticos
    css_files = [
        'static/css/utilities/animations.css',
        'static/css/app.css',
        'static/css/main.css'
    ]
    
    problematic_rules = []
    
    for css_file in css_files:
        if os.path.exists(css_file):
            with open(css_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Procurar regras problemáticas
                if 'transition: all' in content:
                    problematic_rules.append(f"{css_file}: transition: all")
                
                if 'animation:' in content and 'animation: none' not in content:
                    problematic_rules.append(f"{css_file}: animações CSS")
                
                if 'box-shadow:' in content and 'rgba' in content:
                    problematic_rules.append(f"{css_file}: box-shadow complexo")
    
    if problematic_rules:
        print("⚠️ Regras CSS problemáticas encontradas:")
        for rule in problematic_rules:
            print(f"   - {rule}")
    else:
        print("✅ Nenhuma regra CSS problemática encontrada")
    
    return problematic_rules

def main():
    """Função principal"""
    
    print("=" * 50)
    print("🚀 APLICADOR DE CORREÇÕES DE PERFORMANCE")
    print("=" * 50)
    
    # Verificar métricas atuais
    check_performance_metrics()
    
    # Aplicar correções
    success = apply_emergency_fixes()
    
    if success:
        print("\n🎉 CORREÇÕES APLICADAS COM SUCESSO!")
        print("\n📋 PARA TESTAR:")
        print("1. python app.py")
        print("2. Abrir http://localhost:5000")
        print("3. Verificar painel de debug no canto superior direito")
        print("4. Testar hover nos elementos")
        print("5. Verificar se o background não fica branco no hover")
        print("6. Abrir performance-test.html para testes isolados")
    else:
        print("\n❌ ERRO AO APLICAR CORREÇÕES")
        print("Verifique se todos os arquivos necessários estão presentes")

if __name__ == "__main__":
    main() 