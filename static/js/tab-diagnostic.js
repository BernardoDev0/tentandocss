// ===== DIAGNÓSTICO ESPECÍFICO DAS TABS =====

class TabDiagnostic {
  constructor() {
    this.tabElements = [];
    this.hoverEvents = [];
    this.performanceIssues = [];
    
    this.init();
  }

  init() {
    console.log('🔍 Iniciando diagnóstico das Tabs...');
    this.analyzeTabs();
    this.detectPerformanceIssues();
    this.suggestOptimizations();
  }

  analyzeTabs() {
    // Encontra todas as tabs
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');
    
    console.log(`📊 Encontradas ${tabButtons.length} tab buttons e ${tabContents.length} tab contents`);
    
    this.tabElements = Array.from(tabButtons).map((button, index) => {
      const computedStyle = getComputedStyle(button);
      
      return {
        element: button,
        index: index,
        text: button.textContent.trim(),
        hasIcon: button.querySelector('i') !== null,
        transition: computedStyle.transition,
        transform: computedStyle.transform,
        boxShadow: computedStyle.boxShadow,
        hasPseudoElements: this.hasPseudoElements(button),
        cssClasses: Array.from(button.classList)
      };
    });
    
    console.log('📋 Análise das Tabs:', this.tabElements);
  }

  hasPseudoElements(element) {
    const before = getComputedStyle(element, '::before');
    const after = getComputedStyle(element, '::after');
    
    return {
      before: before.content !== 'none' && before.content !== '',
      after: after.content !== 'none' && after.content !== ''
    };
  }

  detectPerformanceIssues() {
    console.log('🔍 Detectando problemas de performance...');
    
    this.tabElements.forEach((tab, index) => {
      const issues = [];
      
      // Verifica transições problemáticas
      if (tab.transition.includes('all')) {
        issues.push('❌ Transição "all" detectada - causa recálculo de layout');
      }
      
      if (tab.transition.includes('transform')) {
        issues.push('⚠️ Transição "transform" pode causar problemas se mal otimizada');
      }
      
      if (tab.transition.includes('box-shadow')) {
        issues.push('⚠️ Transição "box-shadow" pode ser pesada');
      }
      
      // Verifica pseudo-elementos
      if (tab.hasPseudoElements.before || tab.hasPseudoElements.after) {
        issues.push('⚠️ Pseudo-elementos detectados - podem causar overhead');
      }
      
      // Verifica classes problemáticas
      if (tab.cssClasses.some(cls => cls.includes('backdrop'))) {
        issues.push('⚠️ Backdrop-filter detectado - pode ser pesado');
      }
      
      if (issues.length > 0) {
        this.performanceIssues.push({
          tabIndex: index,
          tabText: tab.text,
          issues: issues
        });
      }
    });
    
    if (this.performanceIssues.length > 0) {
      console.log('🚨 Problemas de performance detectados:', this.performanceIssues);
    } else {
      console.log('✅ Nenhum problema crítico detectado');
    }
  }

  suggestOptimizations() {
    console.log('💡 Sugestões de otimização:');
    
    if (this.performanceIssues.length > 0) {
      console.log('🔧 Otimizações recomendadas:');
      
      this.performanceIssues.forEach(issue => {
        console.log(`\n📌 Tab "${issue.tabText}":`);
        issue.issues.forEach(problem => {
          console.log(`   ${problem}`);
        });
      });
      
      console.log('\n🎯 Soluções rápidas:');
      console.log('   1. Substituir "transition: all" por "transition: opacity"');
      console.log('   2. Remover pseudo-elementos animados');
      console.log('   3. Usar "will-change: opacity" para otimização GPU');
      console.log('   4. Aplicar "contain: layout style paint"');
    }
    
    // Sugestões gerais
    console.log('\n📚 Melhores práticas:');
    console.log('   • Use apenas "opacity" e "transform" para animações');
    console.log('   • Evite animar "width", "height", "margin", "padding"');
    console.log('   • Use "requestAnimationFrame" para mudanças de estilo');
    console.log('   • Aplique "will-change" apenas quando necessário');
  }

  // Método para testar performance das tabs
  testTabPerformance() {
    console.log('🧪 Testando performance das tabs...');
    
    const testDuration = 3000; // 3 segundos
    const testInterval = 100; // Teste a cada 100ms
    let testCount = 0;
    const maxTests = testDuration / testInterval;
    
    const startTime = performance.now();
    const fpsHistory = [];
    
    const testHover = () => {
      const tabButtons = document.querySelectorAll('.tab-button');
      if (tabButtons.length === 0) {
        console.log('❌ Nenhuma tab encontrada para teste');
        return;
      }
      
      // Simula hover em tabs alternadas
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
      const fps = 1000 / (currentTime - (window.lastTestTime || currentTime));
      fpsHistory.push(fps);
      window.lastTestTime = currentTime;
      
      testCount++;
      
      if (testCount < maxTests) {
        setTimeout(testHover, testInterval);
      } else {
        // Finaliza teste
        const avgFPS = fpsHistory.reduce((a, b) => a + b, 0) / fpsHistory.length;
        const minFPS = Math.min(...fpsHistory);
        const maxFPS = Math.max(...fpsHistory);
        
        console.log('📊 Resultados do teste de performance:');
        console.log(`   FPS Médio: ${Math.round(avgFPS)}`);
        console.log(`   FPS Mínimo: ${Math.round(minFPS)}`);
        console.log(`   FPS Máximo: ${Math.round(maxFPS)}`);
        console.log(`   Testes realizados: ${testCount}`);
        
        if (avgFPS < 45) {
          console.log('⚠️ Performance abaixo do ideal - otimizações necessárias');
        } else {
          console.log('✅ Performance adequada');
        }
      }
    };
    
    testHover();
  }

  // Método para aplicar otimizações automáticas
  applyAutoOptimizations() {
    console.log('🔧 Aplicando otimizações automáticas...');
    
    const tabButtons = document.querySelectorAll('.tab-button');
    
    tabButtons.forEach(button => {
      // Aplica otimizações via JavaScript
      button.style.willChange = 'opacity';
      button.style.transition = 'opacity 0.15s ease-out';
      
      // Remove transformações problemáticas
      if (button.style.transform) {
        button.style.transform = 'none';
      }
      
      // Remove box-shadow animado
      if (button.style.boxShadow) {
        button.style.boxShadow = 'none';
      }
    });
    
    console.log('✅ Otimizações aplicadas!');
  }

  // Método para gerar relatório completo
  generateReport() {
    console.log('📋 === RELATÓRIO DE DIAGNÓSTICO DAS TABS ===');
    
    console.log(`📊 Total de Tabs: ${this.tabElements.length}`);
    console.log(`🚨 Problemas detectados: ${this.performanceIssues.length}`);
    
    if (this.performanceIssues.length > 0) {
      console.log('\n🔍 Detalhes dos problemas:');
      this.performanceIssues.forEach(issue => {
        console.log(`\n   Tab "${issue.tabText}":`);
        issue.issues.forEach(problem => {
          console.log(`     ${problem}`);
        });
      });
    }
    
    console.log('\n💡 Recomendações:');
    console.log('   1. Aplique o patch CSS emergencial');
    console.log('   2. Use o otimizador de FPS automático');
    console.log('   3. Monitore FPS em tempo real');
    console.log('   4. Teste performance após otimizações');
    
    console.log('\n🎯 Comandos úteis:');
    console.log('   window.tabDiagnostic.testTabPerformance()');
    console.log('   window.tabDiagnostic.applyAutoOptimizations()');
    console.log('   window.fpsMonitor.showStats()');
    
    console.log('=====================================');
  }
}

// Inicializa o diagnóstico
window.tabDiagnostic = new TabDiagnostic();

// Comandos úteis para o console
console.log('🔍 Comandos de diagnóstico disponíveis:');
console.log('  window.tabDiagnostic.testTabPerformance() - Testar performance');
console.log('  window.tabDiagnostic.applyAutoOptimizations() - Aplicar otimizações');
console.log('  window.tabDiagnostic.generateReport() - Gerar relatório completo');

// ===== FIM DO DIAGNÓSTICO DAS TABS ===== 