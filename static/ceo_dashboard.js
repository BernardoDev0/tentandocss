// IMPORTANTE: Adicionar <script src="static/js/chart-optimized.js"></script> no template
// Verificar se a classe já existe antes de declarar
if (typeof window.CEODashboard === 'undefined') {
  window.CEODashboard = class {
    constructor() {
      this.charts = {};
      this.isInitialized = false;
      
      // Aguardar Chart.js estar disponível antes de configurar
      this.waitForChartJS();
    }

    // Aguardar Chart.js estar disponível
    async waitForChartJS() {
        let attempts = 0;
        const maxAttempts = 50; // 5 segundos máximo
        
        const checkChartJS = () => {
            if (typeof Chart !== 'undefined') {
                this.initializeChartJS();
                return;
            }
            
            attempts++;
            if (attempts < maxAttempts) {
                setTimeout(checkChartJS, 100);
            } else {
                console.error('Chart.js não foi carregado após timeout');
            }
        };
        
        checkChartJS();
    }

    // Inicializar configurações do Chart.js
    initializeChartJS() {
        try {
            // Registrar o plugin de anotação para Chart.js 4.x
            if (window['chartjs-plugin-annotation']) {
                Chart.register(window['chartjs-plugin-annotation']);
                console.log('Annotation plugin registered successfully (v4)');
            } else {
                console.warn('Annotation plugin not found - charts will work without annotations');
            }

            // ✅ CORREÇÃO: NÃO CONFIGURAR ANIMAÇÕES GLOBAIS - deixa a aba Gráficos funcionar
            // Configurar apenas o essencial sem afetar outros gráficos
            console.log('Chart.js configurado sem interferir na aba Gráficos');
        } catch (error) {
            console.error('Erro ao configurar Chart.js:', error);
        }
    }

    ensureCanvasDimensions(canvas) {
        canvas.style.width = '100%';
        canvas.style.height = '350px';
        canvas.style.minHeight = '350px';
        canvas.style.display = 'block';
        
        // Forçar reflow
        canvas.offsetHeight;
    }

    async initializeBasicCharts() {
        if (this.isInitialized) {
            console.log('Charts already initialized');
            return;
        }

        console.log('Initializing charts...');
        
        try {
            // Aguardar um pouco para garantir que o DOM está pronto
            await new Promise(resolve => setTimeout(resolve, 100));
            
            // Verificar se os elementos existem
            let weeklyCanvas = document.getElementById('weeklyChart');
            let monthlyCanvas = document.getElementById('monthlyChart');
            let dailyCanvas = document.getElementById('dailyChart');
            
            if (!weeklyCanvas || !monthlyCanvas || !dailyCanvas) {
                console.error('Canvas elements not found');
                return;
            }
            
            // Verificar se os dados existem
            const weeklyDataElement = document.getElementById('weekly-data');
            const monthlyDataElement = document.getElementById('monthly-data');
            const dailyDataElement = document.getElementById('daily-data');
            
            if (!weeklyDataElement || !monthlyDataElement || !dailyDataElement) {
                console.error('Data elements not found');
                return;
            }
            
            // Logar conteúdo dos placeholders de dados antes do parse
            console.log('weekly-data placeholder:', weeklyDataElement.textContent);
            console.log('monthly-data placeholder:', monthlyDataElement.textContent);
            console.log('daily-data placeholder:', dailyDataElement.textContent);
            
            // Obter dados
            let weeklyData, monthlyData, dailyData;
            
            try {
                weeklyData = JSON.parse(weeklyDataElement.textContent);
                monthlyData = JSON.parse(monthlyDataElement.textContent);
                dailyData = JSON.parse(dailyDataElement.textContent);
            
                // PASSO 1: ADICIONAR NO SEU HTML (antes do </body>):
                // <script src="https://cdnjs.cloudflare.com/ajax/libs/chartjs-plugin-annotation/3.0.1/chartjs-plugin-annotation.min.js"></script>
            
                // PASSO 2: REGISTRAR O PLUGIN (adicione no início do seu arquivo JS, após Chart.js)
                if (typeof Chart !== 'undefined') {
                    // Register the annotation plugin
                    if (window.chartjsPluginAnnotation) {
                        Chart.register(window.chartjsPluginAnnotation);
                        console.log('Plugin de annotation registrado');
                    } else {
                        console.error('Annotation plugin not found');
                    }
                }
            
                // PASSO 3: REMOVER AS LINHAS DE META DOS DATASETS
                dailyData.datasets.forEach((dataset, index) => {
                    if (dataset.label !== 'Meta') {
                        dataset.order = index + 1; // Barras ficam atrás
                    }
                });
                
            } catch (e) {
                console.error('Error parsing chart data:', e);
                return;
            }
            
            console.log('Weekly data:', weeklyData);
            console.log('Monthly data:', monthlyData);
            console.log('Daily data:', dailyData);
            
            // Verificar se há dados válidos
            if (!weeklyData.datasets || weeklyData.datasets.length === 0) {
                console.warn('No weekly data available');
                this.showNoDataMessage('weeklyChart', 'Nenhum dado semanal disponível');
                return;
            }
            
            if (!monthlyData.datasets || monthlyData.datasets.length === 0) {
                console.warn('No monthly data available');
                this.showNoDataMessage('monthlyChart', 'Nenhum dado mensal disponível');
                return;
            }
            
            if (!dailyData.datasets || dailyData.datasets.length === 0) {
                console.warn('No daily data available');
                this.showNoDataMessage('dailyChart', 'Nenhum dado diário disponível');
                return;
            }
            
            // PASSO 4: SUBSTITUIR AS OPÇÕES DOS GRÁFICOS
            // Substituir weeklyChartOptions por:
            const weeklyChartOptions = {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                        display: true, // HABILITAR LEGENDAS
                        labels: {
                            color: '#ffffff',
                            usePointStyle: true,
                            padding: 10,
                            font: {
                                size: 12
                            }
                        },
                        onClick: function(e, legendItem, legend) {
                            // TORNAR LEGENDAS CLICÁVEIS - CORREÇÃO
                            const index = legendItem.datasetIndex; // ✅ CORREÇÃO: datasetIndex em vez de index
                            const ci = legend.chart;
                            const meta = ci.getDatasetMeta(index);
                            
                            // ANIMAÇÃO OTIMIZADA PARA LEGENDAS
                            const originalOpacity = meta.hidden ? 0 : 1;
                            const targetOpacity = meta.hidden ? 1 : 0;
                            
                            // Configurar animação suave
                            ci.options.animation = {
                                duration: 300, // 300ms - otimizado
                                easing: 'easeInOutQuart'
                            };
                            
                            // Toggle visibility com animação
                            meta.hidden = !meta.hidden;
                            
                            // Aplicar transição de opacidade
                            if (meta.dataset) {
                                meta.dataset.hidden = meta.hidden;
                            }
                            
                            // Atualizar com animação
                            ci.update('active');
                            
                            // Resetar animação após conclusão
                            setTimeout(() => {
                                ci.options.animation.duration = 0; // Desabilitar para performance
                            }, 350);
                        }
                    },
                    annotation: {
                        annotations: {
                            metaWeekly: {
                                type: 'line',
                                yMin: 2375, // valor da meta semanal
                                yMax: 2375,
                                borderColor: 'rgba(255,99,132,0.8)',
                                borderWidth: 2,
                                borderDash: [6, 6],
                                label: {
                                    content: 'Meta',
                                    enabled: true,
                                    position: 'end',
                                    color: '#fff',
                                    backgroundColor: 'rgba(255,99,132,0.8)'
                                },
                                display: true
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        ticks: {
                            color: '#ffffff'
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        // CONFIGURAÇÕES ESPECÍFICAS PARA BARRAS
                        categoryPercentage: 0.8, // Largura das categorias
                        barPercentage: 0.9 // Largura das barras
                    },
                    y: {
                        ticks: {
                            color: '#ffffff'
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        }
                    }
                },
                // CONFIGURAÇÕES ESPECÍFICAS PARA BARRAS
                elements: {
                    bar: {
                        borderWidth: 2,
                        borderRadius: 4,
                        backgroundColor: [
                            'rgba(147, 51, 234, 0.8)', // Rodrigo - Roxo
                            'rgba(59, 130, 246, 0.8)', // Maurício - Azul
                            'rgba(34, 197, 94, 0.8)',  // Matheus - Verde
                            'rgba(239, 68, 68, 0.8)'   // Wesley - Vermelho
                        ],
                        borderColor: [
                            'rgba(147, 51, 234, 1)',
                            'rgba(59, 130, 246, 1)',
                            'rgba(34, 197, 94, 1)',
                            'rgba(239, 68, 68, 1)'
                        ]
                    }
                },
                animation: {
                    duration: 800,
                    easing: 'easeInOutCubic'
                }
            };
            
            // Substituir monthlyChartOptions por:
            const monthlyChartOptions = {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                        display: true, // HABILITAR LEGENDAS
                        labels: {
                            color: '#ffffff',
                            usePointStyle: true,
                            padding: 10,
                            font: {
                                size: 12
                            }
                        },
                        onClick: function(e, legendItem, legend) {
                            // TORNAR LEGENDAS CLICÁVEIS - CORREÇÃO
                            const index = legendItem.datasetIndex; // ✅ CORREÇÃO: datasetIndex em vez de index
                            const ci = legend.chart;
                            const meta = ci.getDatasetMeta(index);
                            
                            // ANIMAÇÃO OTIMIZADA PARA LEGENDAS
                            const originalOpacity = meta.hidden ? 0 : 1;
                            const targetOpacity = meta.hidden ? 1 : 0;
                            
                            // Configurar animação suave
                            ci.options.animation = {
                                duration: 300, // 300ms - otimizado
                                easing: 'easeInOutQuart'
                            };
                            
                            // Toggle visibility com animação
                            meta.hidden = !meta.hidden;
                            
                            // Aplicar transição de opacidade
                            if (meta.dataset) {
                                meta.dataset.hidden = meta.hidden;
                            }
                            
                            // Atualizar com animação
                            ci.update('active');
                            
                            // Resetar animação após conclusão
                            setTimeout(() => {
                                ci.options.animation.duration = 0; // Desabilitar para performance
                            }, 350);
                        }
                    },
                    annotation: {
                        annotations: {
                            metaMonthly: {
                                type: 'line',
                                yMin: 2375, // valor da meta mensal
                                yMax: 2375,
                                borderColor: 'rgba(54,162,235,0.8)',
                                borderWidth: 2,
                                borderDash: [6, 6],
                                label: {
                                    content: 'Meta',
                                    enabled: true,
                                    position: 'end',
                                    color: '#fff',
                                    backgroundColor: 'rgba(54,162,235,0.8)'
                                },
                                display: true
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        ticks: {
                            color: '#ffffff'
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        }
                    },
                    y: {
                        ticks: {
                            color: '#ffffff'
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        }
                    }
                },
                animation: {
                    duration: 800,
                    easing: 'easeInOutCubic'
                }
            };
            
            // Substituir dailyChartOptions por:
            const dailyChartOptions = {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                        display: true, // HABILITAR LEGENDAS
                        labels: {
                            color: '#ffffff',
                            usePointStyle: true,
                            padding: 10,
                            font: {
                                size: 12
                            }
                        },
                        onClick: function(e, legendItem, legend) {
                            // TORNAR LEGENDAS CLICÁVEIS - CORREÇÃO
                            const index = legendItem.datasetIndex; // ✅ CORREÇÃO: datasetIndex em vez de index
                            const ci = legend.chart;
                            const meta = ci.getDatasetMeta(index);
                            
                            // ANIMAÇÃO OTIMIZADA PARA LEGENDAS
                            const originalOpacity = meta.hidden ? 0 : 1;
                            const targetOpacity = meta.hidden ? 1 : 0;
                            
                            // Configurar animação suave
                            ci.options.animation = {
                                duration: 300, // 300ms - otimizado
                                easing: 'easeInOutQuart'
                            };
                            
                            // Toggle visibility com animação
                            meta.hidden = !meta.hidden;
                            
                            // Aplicar transição de opacidade
                            if (meta.dataset) {
                                meta.dataset.hidden = meta.hidden;
                            }
                            
                            // Atualizar com animação
                            ci.update('active');
                            
                            // Resetar animação após conclusão
                            setTimeout(() => {
                                ci.options.animation.duration = 0; // Desabilitar para performance
                            }, 350);
                        }
                    },
                    annotation: {
                        annotations: {
                            metaDaily: {
                                type: 'line',
                                yMin: 475, // valor da meta diária
                                yMax: 475,
                                borderColor: 'rgba(255,206,86,0.8)',
                                borderWidth: 2,
                                borderDash: [6, 6],
                                label: {
                                    content: 'Meta',
                                    enabled: true,
                                    position: 'end',
                                    color: '#fff',
                                    backgroundColor: 'rgba(255,206,86,0.8)'
                                },
                                display: true
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        ticks: {
                            color: '#ffffff'
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        // CONFIGURAÇÕES ESPECÍFICAS PARA BARRAS
                        categoryPercentage: 0.8, // Largura das categorias
                        barPercentage: 0.9 // Largura das barras
                    },
                    y: {
                        min: 0,
                        max: 1200, // AUMENTADO DE 800 PARA 1200
                        ticks: {
                            color: '#ffffff',
                            stepSize: 100
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        }
                    }
                },
                // CONFIGURAÇÕES ESPECÍFICAS PARA BARRAS
                elements: {
                    bar: {
                        borderWidth: 2,
                        borderRadius: 4,
                        backgroundColor: [
                            'rgba(147, 51, 234, 0.8)', // Rodrigo - Roxo
                            'rgba(59, 130, 246, 0.8)', // Maurício - Azul
                            'rgba(34, 197, 94, 0.8)',  // Matheus - Verde
                            'rgba(239, 68, 68, 0.8)'   // Wesley - Vermelho
                        ],
                        borderColor: [
                            'rgba(147, 51, 234, 1)',
                            'rgba(59, 130, 246, 1)',
                            'rgba(34, 197, 94, 1)',
                            'rgba(239, 68, 68, 1)'
                        ]
                    }
                },
                animation: {
                    duration: 800,
                    easing: 'easeInOutCubic'
                }
            };
            
            // Logar dados e opções antes de criar os gráficos
            console.log('WeeklyData:', weeklyData);
            console.log('WeeklyChartOptions:', weeklyChartOptions);
            console.log('MonthlyData:', monthlyData);
            console.log('MonthlyChartOptions:', monthlyChartOptions);
            console.log('DailyData:', dailyData);
            console.log('DailyChartOptions:', dailyChartOptions);
            
            if (!weeklyCanvas || !monthlyCanvas || !dailyCanvas) {
                console.error('Canvas elements not found');
                return;
            }
            
            // Criar gráficos com try/catch para logar erros
            try {
                this.charts.weekly = createOptimizedChart('weeklyChart', weeklyData, {
                    type: 'bar',
                    ...weeklyChartOptions,
                    plugins: {
                        ...weeklyChartOptions.plugins,
                        tooltip: { enabled: true }
                    }
                });
            } catch (e) {
                console.error('Erro ao criar gráfico semanal:', e);
            }
            let metaWeeklyVisible = true;
            try {
                metaWeeklyVisible = this.charts.weekly.options.plugins.annotation.annotations.metaWeekly.display !== false;
            } catch(e) {}
            this.updateMetaButton('weekly', metaWeeklyVisible);
            if (typeof removeChartLoading === 'function') removeChartLoading('weeklyChart');
            
            try {
                this.charts.monthly = createOptimizedChart('monthlyChart', monthlyData, {
                    type: 'line',
                    ...monthlyChartOptions,
                    plugins: {
                        ...monthlyChartOptions.plugins,
                        tooltip: { enabled: true }
                    }
                });
            } catch (e) {
                console.error('Erro ao criar gráfico mensal:', e);
            }
            let metaMonthlyVisible = true;
            try {
                metaMonthlyVisible = this.charts.monthly.options.plugins.annotation.annotations.metaMonthly.display !== false;
            } catch(e) {}
            this.updateMetaButton('monthly', metaMonthlyVisible);
            if (typeof removeChartLoading === 'function') removeChartLoading('monthlyChart');
            
            try {
                this.charts.daily = createOptimizedChart('dailyChart', dailyData, {
                    type: 'bar',
                    ...dailyChartOptions,
                    plugins: {
                        ...dailyChartOptions.plugins,
                        tooltip: { enabled: true }
                    }
                });
            } catch (e) {
                console.error('Erro ao criar gráfico diário:', e);
            }
            let metaDailyVisible = true;
            try {
                metaDailyVisible = this.charts.daily.options.plugins.annotation.annotations.metaDaily.display !== false;
            } catch(e) {}
            this.updateMetaButton('daily', metaDailyVisible);
            if (typeof removeChartLoading === 'function') removeChartLoading('dailyChart');
            
            this.isInitialized = true;
            console.log('Charts initialized successfully');
            
        } catch (error) {
            console.error('Error initializing charts:', error);
        }
    }

    // PASSO 5: FUNÇÃO PARA ALTERNAR VISIBILIDADE DAS METAS (OPCIONAL)
    toggleGoalLine(chartType) {
        const chartKey = chartType === 'weekly' ? 'weekly' : 
                         chartType === 'monthly' ? 'monthly' : 'daily';
        if (this.charts[chartKey]) {
            const chart = this.charts[chartKey];
            if (chart.options.plugins && chart.options.plugins.annotation && chart.options.plugins.annotation.annotations) {
                const annotationId = `meta${chartType.charAt(0).toUpperCase() + chartType.slice(1)}`;
                const annotation = chart.options.plugins.annotation.annotations[annotationId];
                if (annotation) {
                    // Alternar o estado
                    const novoEstado = !annotation.display;
                    annotation.display = novoEstado;
                    chart.update();
                    this.updateMetaButton(chartKey, novoEstado);
                } else {
                    console.warn(`Annotation '${annotationId}' não encontrada no gráfico '${chartKey}'.`);
                }
            } else {
                console.warn(`Annotation plugin não configurado corretamente no gráfico '${chartKey}'.`);
            }
        }
    }

    destroyChart(chartId) {
        if (this.charts[chartId]) {
            try {
                this.charts[chartId].destroy();
            } catch (e) {
                console.warn(`Erro ao destruir chart ${chartId}:`, e);
            }
            delete this.charts[chartId];
            console.log(`Chart ${chartId} destroyed`);
        }
    }

    showNoDataMessage(canvasId, message) {
        const canvas = document.getElementById(canvasId);
        if (canvas) {
            const ctx = canvas.getContext('2d');
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.fillStyle = '#ffffff';
            ctx.font = '16px Arial';
            ctx.textAlign = 'center';
            ctx.fillText(message, canvas.width / 2, canvas.height / 2);
        }
    }

    // No final do arquivo, alterar:
    debugAnnotations() {
        ['weekly', 'monthly', 'daily'].forEach(chartType => {
            if (this.charts[chartType]) {
                const chart = this.charts[chartType];
                const annotations = chart.options.plugins.annotation?.annotations;
                console.log(`${chartType} annotations:`, annotations);
            }
        });
    }

    updateMetaButton(chartKey, visible) {
        const button = document.getElementById(`toggle-${chartKey}-meta`);
        if (button) {
            button.innerHTML = visible
                ? '<i class="fas fa-eye"></i> Meta'
                : '<i class="fas fa-eye-slash"></i> Meta';
            button.classList.toggle('meta-hidden', !visible);
        }
    }
  };
}

// Adicionar função de debounce
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Função para adicionar event listeners dos botões de meta
function addMetaButtonListeners() {
    console.log('Tentando adicionar listeners dos botões de meta...');
    
    if (!window.dashboardInstance) {
        console.error('dashboardInstance não encontrado');
        return;
    }
    
    const weeklyBtn = document.getElementById('toggle-weekly-meta');
    const monthlyBtn = document.getElementById('toggle-monthly-meta');
    const dailyBtn = document.getElementById('toggle-daily-meta');
    
    console.log('Botões encontrados:', {
        weekly: !!weeklyBtn,
        monthly: !!monthlyBtn,
        daily: !!dailyBtn
    });
    
    if (weeklyBtn) {
        // Remover listeners existentes para evitar duplicação
        weeklyBtn.removeEventListener('click', weeklyBtn._metaClickHandler);
        weeklyBtn._metaClickHandler = function() {
            console.log('Botão weekly clicado');
            window.dashboardInstance.toggleGoalLine('weekly');
        };
        weeklyBtn.addEventListener('click', weeklyBtn._metaClickHandler);
        console.log('Listener adicionado ao botão weekly');
    }
    
    if (monthlyBtn) {
        // Remover listeners existentes para evitar duplicação
        monthlyBtn.removeEventListener('click', monthlyBtn._metaClickHandler);
        monthlyBtn._metaClickHandler = function() {
            console.log('Botão monthly clicado');
            window.dashboardInstance.toggleGoalLine('monthly');
        };
        monthlyBtn.addEventListener('click', monthlyBtn._metaClickHandler);
        console.log('Listener adicionado ao botão monthly');
    }
    
    if (dailyBtn) {
        // Remover listeners existentes para evitar duplicação
        dailyBtn.removeEventListener('click', dailyBtn._metaClickHandler);
        dailyBtn._metaClickHandler = function() {
            console.log('Botão daily clicado');
            window.dashboardInstance.toggleGoalLine('daily');
        };
        dailyBtn.addEventListener('click', dailyBtn._metaClickHandler);
        console.log('Listener adicionado ao botão daily');
    }
}

// Criar dashboard instance e adicionar listeners
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM carregado, criando dashboard instance...');
    
    setTimeout(function() {
        window.dashboardInstance = new CEODashboard();
        console.log('window.dashboardInstance criado:', window.dashboardInstance);
        
        // Adicionar listeners após um delay para garantir que tudo esteja pronto
        setTimeout(addMetaButtonListeners, 200);
    }, 100);
});
