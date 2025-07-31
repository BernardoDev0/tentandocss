// ===== FPS OPTIMIZER - DESABILITADO =====

class FPSOptimizer {
  constructor() {
    this.init();
  }

  init() {
    console.log('🔧 FPS Optimizer iniciado (DESABILITADO)');
    // DESABILITADO: Não iniciar otimizações automáticas
    // this.startFPSMonitoring();
  }

  startFPSMonitoring() {
    // DESABILITADO: Monitor de FPS
    console.log('📊 FPS Optimizer: DESABILITADO');
    return;
    
    // Código original comentado
    /*
    this.lastTime = performance.now();
    this.frames = 0;
    this.fpsData = [];
    this.optimizationLevel = 'none';
    
    const measureFPS = () => {
      this.frames++;
      const currentTime = performance.now();
      
      if (currentTime >= this.lastTime + 1000) {
        const fps = Math.round((this.frames * 1000) / (currentTime - this.lastTime));
        this.fpsData.push(fps);
        
        if (this.fpsData.length > 60) {
          this.fpsData.shift();
        }
        
        const avgFPS = Math.round(this.fpsData.reduce((a, b) => a + b, 0) / this.fpsData.length);
        console.log(`FPS Atual: ${fps}`);
        
        // Aplicar otimizações dinâmicas
        this.applyDynamicOptimizations(avgFPS);
        
        this.frames = 0;
        this.lastTime = currentTime;
      }
      
      requestAnimationFrame(measureFPS);
    };
    
    requestAnimationFrame(measureFPS);
    */
  }

  applyDynamicOptimizations(avgFPS) {
    // Se FPS está baixo, aplica otimizações mais agressivas
    if (avgFPS < 30 && this.optimizationLevel < 2) {
      this.optimizationLevel = 2;
      this.applyAggressiveOptimizations();
    } else if (avgFPS < 45 && this.optimizationLevel < 1) {
      this.optimizationLevel = 1;
      this.applyModerateOptimizations();
    } else if (avgFPS > 55 && this.optimizationLevel > 0) {
      this.optimizationLevel = 0;
      this.removeOptimizations();
    }
  }

  applyTabOptimizations() {
    const tabButtons = document.querySelectorAll('.tab-button');
    
    tabButtons.forEach(button => {
      // Remove listeners antigos para evitar duplicação
      button.removeEventListener('mouseenter', this.handleTabHover);
      button.removeEventListener('mouseleave', this.handleTabLeave);
      
      // Adiciona listeners otimizados
      button.addEventListener('mouseenter', this.handleTabHover.bind(this), { passive: true });
      button.addEventListener('mouseleave', this.handleTabLeave.bind(this), { passive: true });
      
      // Aplica otimizações CSS via JavaScript
      button.style.willChange = 'opacity';
      button.style.transform = 'none';
      button.style.transition = 'opacity 0.15s ease-out';
    });
  }

  handleTabHover(event) {
    const button = event.target.closest('.tab-button');
    if (!button) return;
    
    // Usa requestAnimationFrame para otimizar a mudança
    requestAnimationFrame(() => {
      button.style.opacity = '0.9';
      button.style.background = 'rgba(255, 255, 255, 0.05)';
    });
  }

  handleTabLeave(event) {
    const button = event.target.closest('.tab-button');
    if (!button) return;
    
    requestAnimationFrame(() => {
      if (!button.classList.contains('active')) {
        button.style.opacity = '1';
        button.style.background = 'transparent';
      }
    });
  }

  applyModerateOptimizations() {
    console.log('Aplicando otimizações moderadas...');
    
    // Remove animações complexas
    const style = document.createElement('style');
    style.textContent = `
      .tab-button {
        transition: opacity 0.1s ease-out !important;
        transform: none !important;
        box-shadow: none !important;
      }
      .tab-button::before,
      .tab-button::after {
        display: none !important;
      }
    `;
    document.head.appendChild(style);
  }

  applyAggressiveOptimizations() {
    console.log('Aplicando otimizações agressivas...');
    
    // Remove todas as animações
    const style = document.createElement('style');
    style.textContent = `
      .tab-button {
        transition: none !important;
        transform: none !important;
        box-shadow: none !important;
        animation: none !important;
      }
      .tab-button::before,
      .tab-button::after {
        display: none !important;
      }
      .tab-content {
        animation: none !important;
        transition: none !important;
      }
    `;
    document.head.appendChild(style);
  }

  removeOptimizations() {
    console.log('Removendo otimizações...');
    
    // Remove estilos de otimização
    const optimizationStyles = document.querySelectorAll('style');
    optimizationStyles.forEach(style => {
      if (style.textContent.includes('tab-button') && 
          style.textContent.includes('!important')) {
        style.remove();
      }
    });
  }

  addHoverListeners() {
    // Adiciona listener global para detectar hover em tabs
    document.addEventListener('mouseover', (event) => {
      const tabButton = event.target.closest('.tab-button');
      if (tabButton) {
        // Marca que estamos em uma tab para otimizações
        document.body.classList.add('tab-hover-active');
      }
    }, { passive: true });
    
    document.addEventListener('mouseout', (event) => {
      const tabButton = event.target.closest('.tab-button');
      if (tabButton) {
        // Remove marcação quando sair da tab
        setTimeout(() => {
          if (!document.querySelector('.tab-button:hover')) {
            document.body.classList.remove('tab-hover-active');
          }
        }, 100);
      }
    }, { passive: true });
  }

  // Método para forçar otimização manual
  forceOptimization() {
    this.applyAggressiveOptimizations();
    console.log('Otimização forçada aplicada');
  }

  // Método para resetar otimizações
  resetOptimizations() {
    this.optimizationLevel = 0;
    this.removeOptimizations();
    console.log('Otimizações resetadas');
  }
}

// Inicializa o otimizador quando o DOM estiver pronto
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    window.fpsOptimizer = new FPSOptimizer();
  });
} else {
  window.fpsOptimizer = new FPSOptimizer();
}

// Expose para uso no console
window.FPSOptimizer = FPSOptimizer;

// ===== FIM DO OTIMIZADOR DE FPS ===== 