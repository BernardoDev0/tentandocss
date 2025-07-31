// ===== TESTE RÁPIDO DE PERFORMANCE DAS TABS =====

class QuickPerformanceTest {
  constructor() {
    this.testResults = {
      before: null,
      after: null
    };
    
    this.init();
  }

  init() {
    console.log('🚀 Teste Rápido de Performance das Tabs');
    console.log('📋 Comandos disponíveis:');
    console.log('   window.quickTest.runBeforeTest() - Teste ANTES das otimizações');
    console.log('   window.quickTest.runAfterTest() - Teste DEPOIS das otimizações');
    console.log('   window.quickTest.compareResults() - Comparar resultados');
    console.log('   window.quickTest.autoTest() - Teste automático completo');
  }

  async runBeforeTest() {
    console.log('🧪 Executando teste ANTES das otimizações...');
    
    // Remove otimizações temporariamente
    this.removeOptimizations();
    
    // Aguarda um pouco para estabilizar
    await this.delay(1000);
    
    const result = await this.measureTabPerformance();
    this.testResults.before = result;
    
    console.log('📊 Resultados ANTES das otimizações:', result);
    return result;
  }

  async runAfterTest() {
    console.log('🧪 Executando teste DEPOIS das otimizações...');
    
    // Aplica otimizações
    this.applyOptimizations();
    
    // Aguarda um pouco para estabilizar
    await this.delay(1000);
    
    const result = await this.measureTabPerformance();
    this.testResults.after = result;
    
    console.log('📊 Resultados DEPOIS das otimizações:', result);
    return result;
  }

  async measureTabPerformance() {
    const tabButtons = document.querySelectorAll('.tab-button');
    if (tabButtons.length === 0) {
      console.log('❌ Nenhuma tab encontrada');
      return null;
    }

    const fpsHistory = [];
    const startTime = performance.now();
    const testDuration = 2000; // 2 segundos
    const testInterval = 100; // Teste a cada 100ms
    let testCount = 0;
    const maxTests = testDuration / testInterval;

    return new Promise((resolve) => {
      const testHover = () => {
        const currentTab = tabButtons[testCount % tabButtons.length];
        
        // Dispara hover
        currentTab.dispatchEvent(new MouseEvent('mouseenter', {
          bubbles: true,
          cancelable: true
        }));
        
        // Remove hover após 50ms
        setTimeout(() => {
          currentTab.dispatchEvent(new MouseEvent('mouseleave', {
            bubbles: true,
            cancelable: true
          }));
        }, 50);
        
        // Mede FPS
        const currentTime = performance.now();
        const fps = 1000 / (currentTime - (window.lastQuickTestTime || currentTime));
        fpsHistory.push(fps);
        window.lastQuickTestTime = currentTime;
        
        testCount++;
        
        if (testCount < maxTests) {
          setTimeout(testHover, testInterval);
        } else {
          // Finaliza teste
          const avgFPS = fpsHistory.reduce((a, b) => a + b, 0) / fpsHistory.length;
          const minFPS = Math.min(...fpsHistory);
          const maxFPS = Math.max(...fpsHistory);
          
          resolve({
            avgFPS: Math.round(avgFPS),
            minFPS: Math.round(minFPS),
            maxFPS: Math.round(maxFPS),
            testCount: testCount,
            duration: testDuration
          });
        }
      };
      
      testHover();
    });
  }

  applyOptimizations() {
    console.log('🔧 Aplicando otimizações...');
    
    // Aplica patch CSS
    const style = document.createElement('style');
    style.textContent = `
      .tab-button {
        transition: opacity 0.15s ease-out !important;
        will-change: opacity !important;
        transform: none !important;
        box-shadow: none !important;
      }
      .tab-button::before,
      .tab-button::after {
        display: none !important;
      }
      .tab-button:hover {
        opacity: 0.9 !important;
        background: rgba(255, 255, 255, 0.05) !important;
      }
    `;
    document.head.appendChild(style);
    
    // Aplica otimizações via JavaScript
    const tabButtons = document.querySelectorAll('.tab-button');
    tabButtons.forEach(button => {
      button.style.willChange = 'opacity';
      button.style.transition = 'opacity 0.15s ease-out';
    });
  }

  removeOptimizations() {
    console.log('🔄 Removendo otimizações...');
    
    // Remove estilos de otimização
    const optimizationStyles = document.querySelectorAll('style');
    optimizationStyles.forEach(style => {
      if (style.textContent.includes('tab-button') && 
          style.textContent.includes('!important')) {
        style.remove();
      }
    });
    
    // Remove otimizações JavaScript
    const tabButtons = document.querySelectorAll('.tab-button');
    tabButtons.forEach(button => {
      button.style.willChange = '';
      button.style.transition = '';
    });
  }

  compareResults() {
    if (!this.testResults.before || !this.testResults.after) {
      console.log('❌ Execute os testes antes/depois primeiro');
      return;
    }

    const before = this.testResults.before;
    const after = this.testResults.after;
    
    console.log('📊 === COMPARAÇÃO DE RESULTADOS ===');
    console.log(`📈 FPS Médio: ${before.avgFPS} → ${after.avgFPS} (${after.avgFPS - before.avgFPS > 0 ? '+' : ''}${after.avgFPS - before.avgFPS})`);
    console.log(`📉 FPS Mínimo: ${before.minFPS} → ${after.minFPS} (${after.minFPS - before.minFPS > 0 ? '+' : ''}${after.minFPS - before.minFPS})`);
    console.log(`📊 FPS Máximo: ${before.maxFPS} → ${after.maxFPS} (${after.maxFPS - before.maxFPS > 0 ? '+' : ''}${after.maxFPS - before.maxFPS})`);
    
    const improvement = ((after.avgFPS - before.avgFPS) / before.avgFPS * 100);
    
    if (improvement > 0) {
      console.log(`✅ Melhoria: +${Math.round(improvement)}%`);
    } else {
      console.log(`⚠️ Piora: ${Math.round(improvement)}%`);
    }
    
    // Análise de performance
    if (after.avgFPS >= 55) {
      console.log('🎉 Performance EXCELENTE após otimizações!');
    } else if (after.avgFPS >= 45) {
      console.log('✅ Performance BOA após otimizações');
    } else if (after.avgFPS >= 30) {
      console.log('🟡 Performance REGULAR após otimizações');
    } else {
      console.log('🔴 Performance ainda RUIM - mais otimizações necessárias');
    }
    
    console.log('================================');
  }

  async autoTest() {
    console.log('🤖 Iniciando teste automático completo...');
    
    console.log('\n1️⃣ Testando ANTES das otimizações...');
    await this.runBeforeTest();
    
    console.log('\n2️⃣ Aplicando otimizações...');
    this.applyOptimizations();
    
    console.log('\n3️⃣ Testando DEPOIS das otimizações...');
    await this.runAfterTest();
    
    console.log('\n4️⃣ Comparando resultados...');
    this.compareResults();
    
    console.log('\n✅ Teste automático concluído!');
  }

  delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

// Inicializa o teste rápido
window.quickTest = new QuickPerformanceTest();

// ===== FIM DO TESTE RÁPIDO ===== 