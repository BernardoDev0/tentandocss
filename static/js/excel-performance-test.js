// ===== TESTE DE PERFORMANCE PARA ABA EXCEL =====

class ExcelPerformanceTest {
  constructor() {
    this.testResults = {
      before: null,
      after: null
    };
    
    this.init();
  }

  init() {
    console.log('🚀 Teste de Performance da Aba Excel');
    console.log('📋 Comandos disponíveis:');
    console.log('   window.excelTest.runBeforeTest() - Teste ANTES das otimizações');
    console.log('   window.excelTest.runAfterTest() - Teste DEPOIS das otimizações');
    console.log('   window.excelTest.compareResults() - Comparar resultados');
    console.log('   window.excelTest.autoTest() - Teste automático completo');
    console.log('   window.excelTest.testCardHover() - Testar hover nos cards');
    console.log('   window.excelTest.testChartPerformance() - Testar performance do gráfico');
  }

  async runBeforeTest() {
    console.log('🧪 Executando teste ANTES das otimizações da aba Excel...');
    
    // Remove otimizações temporariamente
    this.removeOptimizations();
    
    // Aguarda um pouco para estabilizar
    await this.delay(1000);
    
    const result = await this.measureExcelPerformance();
    this.testResults.before = result;
    
    console.log('📊 Resultados ANTES das otimizações:', result);
    return result;
  }

  async runAfterTest() {
    console.log('🧪 Executando teste DEPOIS das otimizações da aba Excel...');
    
    // Aplica otimizações
    this.applyOptimizations();
    
    // Aguarda um pouco para estabilizar
    await this.delay(1000);
    
    const result = await this.measureExcelPerformance();
    this.testResults.after = result;
    
    console.log('📊 Resultados DEPOIS das otimizações:', result);
    return result;
  }

  async measureExcelPerformance() {
    const excelCards = document.querySelectorAll('.excel-stat-card');
    const excelButtons = document.querySelectorAll('.excel-chart-container .glass-btn');
    const loadButton = document.getElementById('load-folder-btn');
    
    if (excelCards.length === 0) {
      console.log('❌ Nenhum card da aba Excel encontrado');
      return null;
    }

    const fpsHistory = [];
    const startTime = performance.now();
    const testDuration = 3000; // 3 segundos
    const testInterval = 100; // Teste a cada 100ms
    let testCount = 0;
    const maxTests = testDuration / testInterval;

    return new Promise((resolve) => {
      const testHover = () => {
        // Testa hover em cards alternados
        const currentCard = excelCards[testCount % excelCards.length];
        
        // Dispara hover
        currentCard.dispatchEvent(new MouseEvent('mouseenter', {
          bubbles: true,
          cancelable: true
        }));
        
        // Remove hover após 50ms
        setTimeout(() => {
          currentCard.dispatchEvent(new MouseEvent('mouseleave', {
            bubbles: true,
            cancelable: true
          }));
        }, 50);
        
        // Mede FPS
        const currentTime = performance.now();
        const fps = 1000 / (currentTime - (window.lastExcelTestTime || currentTime));
        fpsHistory.push(fps);
        window.lastExcelTestTime = currentTime;
        
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
            duration: testDuration,
            cardsTested: excelCards.length,
            buttonsTested: excelButtons.length
          });
        }
      };
      
      testHover();
    });
  }

  testCardHover() {
    console.log('🧪 Testando hover nos cards da aba Excel...');
    
    const excelCards = document.querySelectorAll('.excel-stat-card');
    if (excelCards.length === 0) {
      console.log('❌ Nenhum card da aba Excel encontrado');
      return;
    }
    
    console.log(`🎯 Encontrados ${excelCards.length} cards`);
    
    // Testa hover em cada card
    excelCards.forEach((card, index) => {
      setTimeout(() => {
        console.log(`🖱️ Testando card ${index + 1}: ${card.querySelector('.stat-label')?.textContent || 'Card'}`);
        
        // Dispara hover
        card.dispatchEvent(new MouseEvent('mouseenter', {
          bubbles: true,
          cancelable: true
        }));
        
        // Remove hover após 1 segundo
        setTimeout(() => {
          card.dispatchEvent(new MouseEvent('mouseleave', {
            bubbles: true,
            cancelable: true
          }));
        }, 1000);
      }, index * 1500); // Testa um card a cada 1.5 segundos
    });
    
    console.log('✅ Teste de hover nos cards concluído');
  }

  testChartPerformance() {
    console.log('🧪 Testando performance do gráfico da aba Excel...');
    
    const chartCanvas = document.getElementById('excel-chart');
    if (!chartCanvas) {
      console.log('❌ Canvas do gráfico não encontrado');
      return;
    }
    
    // Verifica se o gráfico está carregado
    if (window.ExcelDashboard && window.ExcelDashboard.state.chartInstance) {
      console.log('✅ Gráfico carregado, testando interações...');
      
      // Simula interações com o gráfico
      const chart = window.ExcelDashboard.state.chartInstance;
      
      // Testa hover no gráfico
      const rect = chartCanvas.getBoundingClientRect();
      const centerX = rect.left + rect.width / 2;
      const centerY = rect.top + rect.height / 2;
      
      // Dispara evento de hover no centro do gráfico
      chartCanvas.dispatchEvent(new MouseEvent('mousemove', {
        clientX: centerX,
        clientY: centerY,
        bubbles: true
      }));
      
      console.log('✅ Teste de interação com gráfico concluído');
    } else {
      console.log('⚠️ Gráfico não carregado - carregue dados primeiro');
    }
  }

  applyOptimizations() {
    console.log('🔧 Aplicando otimizações para aba Excel...');
    
    // Aplica patch CSS
    const style = document.createElement('style');
    style.textContent = `
      .excel-stat-card {
        transition: opacity 0.2s ease-out !important;
        will-change: opacity !important;
        transform: none !important;
        box-shadow: none !important;
        contain: layout style paint !important;
      }
      .excel-stat-card:hover {
        opacity: 0.9 !important;
        background: rgba(15, 23, 42, 0.98) !important;
        transform: none !important;
        box-shadow: none !important;
      }
      .excel-chart-container canvas {
        image-rendering: optimizeSpeed !important;
        will-change: auto !important;
        contain: layout style paint !important;
      }
      .excel-chart-container .glass-btn {
        transition: opacity 0.2s ease-out !important;
        will-change: opacity !important;
        transform: none !important;
        box-shadow: none !important;
      }
      .excel-chart-container .glass-btn:hover {
        opacity: 0.9 !important;
        transform: none !important;
        box-shadow: none !important;
      }
    `;
    document.head.appendChild(style);
    
    console.log('✅ Otimizações aplicadas!');
  }

  removeOptimizations() {
    console.log('🔄 Removendo otimizações da aba Excel...');
    
    // Remove estilos de otimização
    const optimizationStyles = document.querySelectorAll('style');
    optimizationStyles.forEach(style => {
      if (style.textContent.includes('excel-stat-card') && 
          style.textContent.includes('!important')) {
        style.remove();
      }
    });
    
    console.log('✅ Otimizações removidas!');
  }

  compareResults() {
    if (!this.testResults.before || !this.testResults.after) {
      console.log('❌ Execute os testes antes/depois primeiro');
      return;
    }

    const before = this.testResults.before;
    const after = this.testResults.after;
    
    console.log('📊 === COMPARAÇÃO DE RESULTADOS ABA EXCEL ===');
    console.log(`📈 FPS Médio: ${before.avgFPS} → ${after.avgFPS} (${after.avgFPS - before.avgFPS > 0 ? '+' : ''}${after.avgFPS - before.avgFPS})`);
    console.log(`📉 FPS Mínimo: ${before.minFPS} → ${after.minFPS} (${after.minFPS - before.minFPS > 0 ? '+' : ''}${after.minFPS - before.minFPS})`);
    console.log(`📊 FPS Máximo: ${before.maxFPS} → ${after.maxFPS} (${after.maxFPS - before.maxFPS > 0 ? '+' : ''}${after.maxFPS - before.maxFPS})`);
    console.log(`🎯 Cards testados: ${before.cardsTested}`);
    console.log(`🔘 Botões testados: ${before.buttonsTested}`);
    
    const improvement = ((after.avgFPS - before.avgFPS) / before.avgFPS * 100);
    
    if (improvement > 0) {
      console.log(`✅ Melhoria: +${Math.round(improvement)}%`);
    } else {
      console.log(`⚠️ Piora: ${Math.round(improvement)}%`);
    }
    
    // Análise de performance
    if (after.avgFPS >= 55) {
      console.log('🎉 Performance EXCELENTE na aba Excel!');
    } else if (after.avgFPS >= 45) {
      console.log('✅ Performance BOA na aba Excel');
    } else if (after.avgFPS >= 30) {
      console.log('🟡 Performance REGULAR na aba Excel');
    } else {
      console.log('🔴 Performance RUIM na aba Excel - mais otimizações necessárias');
    }
    
    console.log('==========================================');
  }

  async autoTest() {
    console.log('🤖 Iniciando teste automático completo da aba Excel...');
    
    console.log('\n1️⃣ Testando ANTES das otimizações...');
    await this.runBeforeTest();
    
    console.log('\n2️⃣ Aplicando otimizações...');
    this.applyOptimizations();
    
    console.log('\n3️⃣ Testando DEPOIS das otimizações...');
    await this.runAfterTest();
    
    console.log('\n4️⃣ Comparando resultados...');
    this.compareResults();
    
    console.log('\n✅ Teste automático da aba Excel concluído!');
  }

  delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

// Inicializa o teste da aba Excel
window.excelTest = new ExcelPerformanceTest();

// ===== FIM DO TESTE DE PERFORMANCE PARA ABA EXCEL ===== 