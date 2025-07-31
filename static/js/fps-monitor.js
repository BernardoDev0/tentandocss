// ===== FPS MONITOR - DESABILITADO =====

class FPSMonitor {
  constructor() {
    this.init();
  }

  init() {
    console.log('🔍 FPS Monitor iniciado (DESABILITADO)');
    // DESABILITADO: Não iniciar monitoramento automático
    // this.startMonitoring();
  }

  startMonitoring() {
    // DESABILITADO: Monitor de FPS
    console.log('📊 FPS Monitor: DESABILITADO');
    return;
    
    // Código original comentado
    /*
    this.lastTime = performance.now();
    this.frames = 0;
    this.fpsData = [];
    
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
        const minFPS = Math.min(...this.fpsData);
        const maxFPS = Math.max(...this.fpsData);
        
        console.log(`FPS: ${avgFPS} | Min: ${minFPS} | Max: ${maxFPS}`);
        console.log(`FPS Atual: ${fps}`);
        
        this.frames = 0;
        this.lastTime = currentTime;
      }
      
      requestAnimationFrame(measureFPS);
    };
    
    requestAnimationFrame(measureFPS);
    */
  }

  getAverageFPS() {
    if (this.fpsData.length === 0) return 0;
    return Math.round(this.fpsData.reduce((a, b) => a + b, 0) / this.fpsData.length);
  }

  showStats() {
    if (this.fpsData.length === 0) {
      console.log('📊 Nenhum dado de FPS disponível');
      return;
    }
    
    const avg = this.getAverageFPS();
    const min = Math.min(...this.fpsData);
    const max = Math.max(...this.fpsData);
    
    console.log('📊 Estatísticas de FPS:');
    console.log(`   Média: ${avg}`);
    console.log(`   Mínimo: ${min}`);
    console.log(`   Máximo: ${max}`);
    console.log(`   Amostras: ${this.fpsData.length}`);
  }

  testTabHover() {
    console.log('🧪 Teste de hover nas tabs (DESABILITADO)');
    return;
  }

  startComparison() {
    console.log('📊 Comparação de performance (DESABILITADO)');
    return;
  }
}

// Inicializar monitor (DESABILITADO)
window.fpsMonitor = new FPSMonitor();

// ===== FIM DO FPS MONITOR ===== 