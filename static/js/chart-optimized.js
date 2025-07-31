/* ===================================================================
   CHART.JS OPTIMIZED - Configurações Otimizadas para Performance
   ================================================================= */

// Detectar se é desktop (com mouse)
const isDesktop = window.matchMedia('(hover: hover) and (pointer: fine)').matches;

// Configuração base otimizada
const optimizedChartConfig = {
    // ANIMAÇÕES OTIMIZADAS (não completamente desabilitadas)
    animation: {
        duration: isDesktop ? 0 : 300 // Reduzido de 400 para 300
    },
    responsiveAnimationDuration: isDesktop ? 0 : 300,
    
    // OTIMIZAR RESPONSIVIDADE
    responsive: true,
    maintainAspectRatio: false,
    
    // INTERAÇÕES OTIMIZADAS
    interaction: {
        mode: 'nearest', // CORREÇÃO: HABILITAR PARA TODOS
        intersect: true // CORREÇÃO: INTERSECT TRUE PARA PRECISÃO
    },
    
    // CONFIGURAÇÕES DE HOVER OTIMIZADAS
    hover: {
        mode: 'nearest', // HABILITAR HOVER PARA TODOS
        animationDuration: isDesktop ? 0 : 150, // Reduzido de 200 para 150
        intersect: true // CORREÇÃO: INTERSECT TRUE PARA PRECISÃO
    },
    
    // PLUGINS OTIMIZADOS
    plugins: {
        legend: {
            display: true, // MANTENDO LEGENDAS HABILITADAS
            labels: {
                usePointStyle: true
            }
        },
        tooltip: {
            enabled: true, // HABILITAR TOOLTIPS PARA TODOS
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            titleColor: '#fff',
            bodyColor: '#fff',
            borderColor: '#3b82f6',
            borderWidth: 1,
            cornerRadius: 8,
            displayColors: true, // MOSTRAR CORES NOS TOOLTIPS
            animation: false
        },
        decimation: {
            enabled: true,
            algorithm: 'min-max'
        }
    },
    
    // ELEMENTOS OTIMIZADOS
    elements: {
        point: {
            radius: 4, // ✅ PONTOS VISÍVEIS PARA TODOS
            hoverRadius: 6, // ✅ HOVER MAIOR
            hitRadius: 8 // ✅ ÁREA DE CLIQUE MAIOR
        },
        line: {
            borderWidth: 2,
            tension: 0.05 // Reduzido de 0.1 para 0.05
        },
        bar: {
            borderWidth: 0
        }
    },
    
    // ESCALAS OTIMIZADAS
    scales: {
        x: {
            grid: {
                display: false // Remove grid horizontal
            },
            ticks: {
                color: '#94a3b8',
                font: {
                    size: 10 // Reduzido de 11 para 10
                },
                maxRotation: 0,
                minRotation: 0
            }
        },
        y: {
            grid: {
                color: 'rgba(148, 163, 184, 0.1)',
                drawBorder: false
            },
            ticks: {
                color: '#94a3b8',
                font: {
                    size: 10 // Reduzido de 11 para 10
                },
                padding: 4 // Reduzido de 5 para 4
            }
        }
    }
};

// Configuração específica para desktop
const desktopChartConfig = {
    ...optimizedChartConfig,
    plugins: {
        ...optimizedChartConfig.plugins,
        tooltip: {
            enabled: true, // HABILITAR TOOLTIPS PARA DESKTOP TAMBÉM
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            titleColor: '#fff',
            bodyColor: '#fff',
            borderColor: '#3b82f6',
            borderWidth: 1,
            cornerRadius: 8,
            displayColors: true,
            animation: false
        }
    },
    interaction: {
        mode: 'nearest', // ✅ HABILITAR INTERAÇÃO COM PRECISÃO
        intersect: true // ✅ INTERSECT TRUE PARA PRECISÃO
    }
};

// Configuração específica para mobile
const mobileChartConfig = {
    ...optimizedChartConfig,
    plugins: {
        ...optimizedChartConfig.plugins,
        tooltip: {
            enabled: true,
            mode: 'nearest',
            intersect: false
        }
    }
};

// Função para criar chart otimizado
function createOptimizedChart(canvasId, data, customOptions = {}) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) {
        console.error(`Canvas ${canvasId} não encontrado`);
        return null;
    }
    
    // Aplicar otimizações no canvas
    canvas.style.transform = 'translateZ(0)';
    canvas.style.willChange = 'auto';
    canvas.style.contain = 'layout style paint';
    canvas.style.imageRendering = 'optimizeSpeed';
    
    // Escolher configuração baseada no dispositivo
    const baseConfig = isDesktop ? desktopChartConfig : mobileChartConfig;
    
    // Mesclar configurações
    const finalConfig = {
        ...baseConfig,
        ...customOptions
    };
    
    // Criar chart - CORREÇÃO: Usar o tipo das customOptions ou padrão 'line'
    const chartType = customOptions.type || 'line';
    
    const chart = new Chart(canvas, {
        type: chartType,
        data: data,
        options: finalConfig
    });
    
    // Otimizações adicionais apenas em desktop
    if (isDesktop) {
        // DESABILITADO: pointerEvents para permitir interações
        // canvas.style.pointerEvents = 'none';
        
        // Otimizar renderização apenas para gráficos de linha
        if (chartType === 'line') {
            chart.options.elements.line.tension = 0;
            // REMOVIDO: chart.options.elements.point.radius = 0; // ✅ MANTENDO PONTOS VISÍVEIS
        }
        
        // Desabilitar animações completamente
        chart.options.animation.duration = 0;
        chart.options.responsiveAnimationDuration = 0;
        chart.options.hover.animationDuration = 0;
    }
    
    return chart;
}

// Função para atualizar chart com animação otimizada
function updateChartOptimized(chart, newData) {
    if (!chart) return;
    
    chart.data = newData;
    // Usar animação otimizada baseada no dispositivo
    chart.update(isDesktop ? 'none' : 'active');
}

// Função para destruir chart otimizado
function destroyChartOptimized(chart) {
    if (chart) {
        chart.destroy();
    }
}

// Monitor de performance para charts
class ChartPerformanceMonitor {
    constructor() {
        this.charts = new Map();
        this.fpsData = [];
        this.lastFrameTime = performance.now();
    }
    
    addChart(chartId, chart) {
        this.charts.set(chartId, chart);
    }
    
    removeChart(chartId) {
        const chart = this.charts.get(chartId);
        if (chart) {
            destroyChartOptimized(chart);
            this.charts.delete(chartId);
        }
    }
    
    measureFPS() {
        const now = performance.now();
        const delta = now - this.lastFrameTime;
        this.lastFrameTime = now;
        
        if (delta > 0) {
            const fps = 1000 / delta;
            this.fpsData.push(fps);
            
            // Manter apenas últimos 60 frames
            if (this.fpsData.length > 60) {
                this.fpsData.shift();
            }
            
            const avgFPS = this.fpsData.reduce((a, b) => a + b, 0) / this.fpsData.length;
            
            // Se FPS muito baixo, aplicar otimizações emergenciais
            if (avgFPS < 30) {
                this.applyEmergencyOptimizations();
            }
            
            return avgFPS;
        }
        
        return 0;
    }
    
    applyEmergencyOptimizations() {
        console.warn('FPS baixo detectado, aplicando otimizações emergenciais...');
        
        // Desabilitar todas as animações apenas em emergência
        document.body.classList.add('emergency-performance-mode');
        
        // Otimizar todos os charts
        this.charts.forEach((chart, chartId) => {
            if (chart && chart.options) {
                chart.options.animation.duration = 0;
                chart.options.responsiveAnimationDuration = 0;
                chart.options.hover.mode = null;
                chart.update('none');
            }
        });
    }
}

// Inicializar monitor de performance
const chartPerformanceMonitor = new ChartPerformanceMonitor();

// Função para criar chart com monitoramento
function createMonitoredChart(canvasId, data, customOptions = {}) {
    const chart = createOptimizedChart(canvasId, data, customOptions);
    
    if (chart) {
        chartPerformanceMonitor.addChart(canvasId, chart);
        
        // Monitorar FPS
        const monitorFPS = () => {
            const fps = chartPerformanceMonitor.measureFPS();
            if (fps < 30) {
                console.warn(`FPS baixo detectado: ${fps.toFixed(1)}`);
            }
            requestAnimationFrame(monitorFPS);
        };
        
        requestAnimationFrame(monitorFPS);
    }
    
    return chart;
}

// Exportar funções
window.createOptimizedChart = createOptimizedChart;
window.updateChartOptimized = updateChartOptimized;
window.destroyChartOptimized = destroyChartOptimized;
window.createMonitoredChart = createMonitoredChart;
window.chartPerformanceMonitor = chartPerformanceMonitor;
window.isDesktop = isDesktop; 