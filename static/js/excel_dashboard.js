/**
 * JavaScript otimizado para a aba Excel Dashboard
 * Consistente com o sistema e otimizado para performance
 */

// Namespace para evitar conflitos
window.ExcelDashboard = {
    // Estado da aplicação
    state: {
        isLoaded: false,
        isLoading: false,
        data: null,
        chart: null,
        animationFrame: null,
        chartInstance: null
    },

    // Inicialização
    init() {
        console.log('Excel Dashboard: Inicializando...');
        
        // ✅ CORREÇÃO: Garantir que o loading está desabilitado na inicialização
        this.setStateLoading(false);
        
        // ✅ CORREÇÃO: Verificar e corrigir estado inicial do loading
        this.fixInitialLoadingState();
        
        // ✅ REMOVIDO: Não forçar dados falsos na inicialização
        // this.forceShowCardsOnInit();
        
        this.bindEvents();
        this.checkStatus();
    },

    // Vincular eventos
    bindEvents() {
        const loadBtn = document.getElementById('load-folder-btn');
        if (loadBtn) {
            loadBtn.addEventListener('click', () => this.loadFolder());
        }

        // ✅ REMOVIDO: Event listeners para cards de estatísticas - não faz sentido clicar
        // this.bindStatCardEvents();
    },

    // Verificar status da aba
    async checkStatus() {
        try {
            const response = await fetch('/api/excel/status');
            const data = await response.json();
            
            if (data.status === 'success') {
                console.log('Excel Dashboard: Status OK');
                this.state.isLoaded = true;
            }
        } catch (error) {
            console.error('Excel Dashboard: Erro ao verificar status:', error);
        }
    },

    // Debug da função loadFolder
    debugLoadFolder() {
        console.log('🔍 === DEBUG: LOAD FOLDER ===');
        
        // Simular chamada para loadFolder
        this.loadFolder().then(() => {
            console.log('✅ LoadFolder concluído');
            this.debugDataStructure();
        }).catch((error) => {
            console.error('❌ Erro no loadFolder:', error);
        });
    },

    // Carregar pasta de arquivos Excel
    async loadFolder() {
        if (this.state.isLoading) return;

        console.log('🔍 === DEBUG: INICIANDO LOAD FOLDER ===');
        this.setStateLoading(true);
        this.showMessage('Carregando arquivos Excel...', 'info');

        try {
            console.log('🔍 Fazendo requisição para /api/excel/load_folder');
            
            const response = await fetch('/api/excel/load_folder', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    folder_path: 'registros monitorar'
                })
            });

            console.log('📡 Resposta recebida:', response.status);

            const data = await response.json();
            console.log('📊 Dados recebidos:', data);

            if (data.status === 'success') {
                // Garantir que os dados são válidos
                this.state.data = data.data || {};
                console.log('✅ Dados aplicados ao state:', this.state.data);
                
                // Garantir que as estatísticas são válidas
                const statistics = data.statistics || {};
                console.log('📊 Estatísticas recebidas:', statistics);
                
                // ✅ FORÇAR EXIBIÇÃO DOS CARDS com dados reais
                if (statistics && Object.keys(statistics).length > 0) {
                    console.log('✅ Dados reais encontrados, forçando exibição dos cards');
                    this.updateStatistics(statistics);
                } else {
                    console.log('⚠️ Nenhum dado real encontrado');
                    this.showMessage('Nenhum arquivo Excel encontrado na pasta', 'warning');
                }
                
                this.showMessage('Arquivos carregados com sucesso!', 'success');
                this.initializeChart();
            } else {
                throw new Error(data.message || 'Erro ao carregar arquivos');
            }

        } catch (error) {
            console.error('Excel Dashboard: Erro ao carregar pasta:', error);
            this.showMessage(`Erro: ${error.message}`, 'error');
        } finally {
            this.setStateLoading(false);
        }
    },

    // Definir estado de loading
    setStateLoading(loading) {
        this.state.isLoading = loading;
        const loadBtn = document.getElementById('load-folder-btn');
        const loadingIndicator = document.getElementById('loading-indicator');

        if (loadBtn) {
            loadBtn.disabled = loading;
            loadBtn.classList.toggle('loading', loading);
        }

        if (loadingIndicator) {
            // ✅ CORREÇÃO: Garantir que o loading indicator está oculto por padrão
            if (loading) {
                loadingIndicator.style.display = 'flex';
                loadingIndicator.style.opacity = '1';
            } else {
                loadingIndicator.style.opacity = '0';
                // Ocultar após a transição
                setTimeout(() => {
                    if (loadingIndicator && !this.state.isLoading) {
                        loadingIndicator.style.display = 'none';
                    }
                }, 200);
            }
        }
    },

    // Verificar e corrigir estado inicial do loading
    fixInitialLoadingState() {
        console.log('🔧 === CORRIGINDO ESTADO INICIAL DO LOADING ===');
        
        const loadingIndicator = document.getElementById('loading-indicator');
        const loadBtn = document.getElementById('load-folder-btn');
        
        if (loadingIndicator) {
            // Garantir que está oculto por padrão
            loadingIndicator.style.display = 'none';
            loadingIndicator.style.opacity = '0';
            console.log('✅ Loading indicator oculto');
        }
        
        if (loadBtn) {
            // Garantir que o botão está habilitado
            loadBtn.disabled = false;
            loadBtn.classList.remove('loading');
            console.log('✅ Botão de carregar habilitado');
        }
        
        // Resetar estado interno
        this.state.isLoading = false;
        console.log('✅ Estado de loading resetado');
    },

    // Atualizar estatísticas
    updateStatistics(stats) {
        console.log('🔍 === DEBUG: ATUALIZANDO ESTATÍSTICAS ===');
        console.log('📊 Stats recebidos:', stats);
        
        // ✅ VERIFICAÇÃO: Só atualizar se stats for válido
        if (!stats || typeof stats !== 'object') {
            console.log('❌ Stats inválidos, não atualizando');
            return;
        }
        
        // ✅ CORREÇÃO: Usar as chaves corretas do backend (com underscore)
        const totalPoints = stats.total_points || stats.totalPoints || 0;
        const profitValue = this.calculateProfit(totalPoints);
        
        const elements = {
            'total-files': stats.total_files || stats.totalFiles || 0,
            'total-records': stats.total_records || stats.totalRecords || 0,
            'total-points': totalPoints,
            'total-profit': profitValue
        };

        console.log('📊 Elementos para atualizar:', elements);

        // Animar valores com otimização
        Object.entries(elements).forEach(([id, value]) => {
            const element = document.getElementById(id);
            console.log(`🔍 Elemento ${id}:`, element ? '✅ Encontrado' : '❌ Não encontrado');
            if (element) {
                console.log(`📝 Atualizando ${id} para:`, value);
                this.animateValueOptimized(element, 0, value, 800);
            } else {
                console.error(`❌ Elemento ${id} não encontrado no DOM`);
            }
        });

        // Atualizar detalhes dos cards
        this.updateCardDetails(stats);

        // ✅ FORÇAR EXIBIÇÃO DO GRID quando há dados reais
        const statsGrid = document.getElementById('excel-stats-grid');
        if (statsGrid) {
            statsGrid.style.display = 'grid';
            console.log('✅ Grid de estatísticas exibido com dados reais');
        } else {
            console.error('❌ Grid de estatísticas não encontrado');
        }
    },

    // Calcular lucro total (pontos x R$ 3,25)
    calculateProfit(totalPoints) {
        const profit = totalPoints * 3.25;
        return `R$ ${profit.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
    },

    // Animação otimizada de valores
    animateValueOptimized(element, start, end, duration) {
        // Se o valor final é uma string (como "R$ 1.234,56"), não animar
        if (typeof end === 'string' && end.includes('R$')) {
            if (element && typeof element.textContent !== 'undefined') {
                element.textContent = end;
            }
            return;
        }

        // Garantir que os valores são números válidos
        start = Number(start) || 0;
        end = Number(end) || 0;
        duration = Number(duration) || 800;

        const startTime = performance.now();

        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            // Easing suave
            const easeOut = 1 - Math.pow(2, -10 * progress);
            const current = Math.round(start + (end - start) * easeOut);
            
            // Garantir que o elemento existe e é válido
            if (element && typeof element.textContent !== 'undefined') {
                element.textContent = current.toLocaleString('pt-BR');
            }

            if (progress < 1) {
                this.state.animationFrame = requestAnimationFrame(animate);
            }
        };

        this.state.animationFrame = requestAnimationFrame(animate);
    },

    // Atualizar detalhes dos cards
    updateCardDetails(stats) {
        console.log('🔍 === DEBUG: ATUALIZANDO DETALHES DOS CARDS ===');
        console.log('📊 Stats para detalhes:', stats);
        
        // Garantir que stats é um objeto válido
        stats = stats || {};
        
        const totalFiles = stats.total_files || stats.totalFiles || 0;
        const totalRecords = stats.total_records || stats.totalRecords || 0;
        const totalPoints = stats.total_points || stats.totalPoints || 0;
        const totalProfit = (totalPoints * 3.25).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
        
        const details = {
            'files-detail': `${totalFiles} arquivos processados`,
            'records-detail': `${totalRecords.toLocaleString('pt-BR')} registros totais`,
            'points-detail': `${totalPoints.toLocaleString('pt-BR')} pontos totais`,
            'profit-detail': `R$ ${totalProfit} (pontos x R$ 3,25)`
        };

        console.log('📊 Detalhes para atualizar:', details);

        Object.entries(details).forEach(([id, text]) => {
            const element = document.getElementById(id);
            console.log(`🔍 Elemento ${id}:`, element ? '✅ Encontrado' : '❌ Não encontrado');
            if (element) {
                console.log(`📝 Atualizando ${id} para:`, text);
                element.textContent = text;
            } else {
                console.error(`❌ Elemento ${id} não encontrado no DOM`);
            }
        });
    },

    // Inicializar gráfico
    initializeChart() {
        if (!this.state.data) return;

        this.loadChartJS().then(() => {
            this.createChart();
        });
    },

    // Carregar Chart.js se necessário
    async loadChartJS() {
        // Verificar se Chart.js já está carregado
        if (typeof Chart !== 'undefined') {
            console.log('Chart.js já está carregado');
            
            // Destruir instâncias antigas para evitar conflitos
            if (this.state.chartInstance) {
                try {
                    this.state.chartInstance.destroy();
                    this.state.chartInstance = null;
                } catch (e) {
                    console.log('Erro ao destruir chart anterior:', e);
                }
            }
            
            return Promise.resolve();
        }

        return new Promise((resolve, reject) => {
            // Carregar Chart.js de forma isolada
            const script = document.createElement('script');
            script.src = 'https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js';
            script.type = 'text/javascript';
            
            script.onload = () => {
                console.log('Chart.js carregado com sucesso para Excel Dashboard');
                
                // ✅ CORREÇÃO: NÃO CONFIGURAR GLOBALMENTE - só para este gráfico
                if (typeof Chart !== 'undefined') {
                    console.log('Chart.js disponível para Excel Dashboard');
                }
                
                resolve();
            };
            
            script.onerror = () => {
                console.error('Erro ao carregar Chart.js');
                reject(new Error('Falha ao carregar Chart.js'));
            };
            
            document.head.appendChild(script);
        });
    },

    // Criar gráfico otimizado
    createChart() {
        const canvas = document.getElementById('excel-chart');
        if (!canvas) {
            console.error('Canvas não encontrado');
            return;
        }

        // Destruir gráfico anterior se existir
        if (this.state.chartInstance) {
            try {
                this.state.chartInstance.destroy();
            } catch (e) {
                console.log('Erro ao destruir chart anterior:', e);
            }
        }

        const chartData = this.prepareChartData();
        console.log('📊 Dados para o gráfico:', chartData);

        // Configuração para gráfico de barras
        try {
            this.state.chartInstance = new Chart(canvas, {
                type: 'bar', // ✅ MUDADO PARA BARRAS
            data: chartData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                    animation: false,
                plugins: {
                    legend: {
                            display: true,
                        position: 'top',
                        labels: {
                            color: '#ffffff',
                            font: {
                                size: 12,
                                    weight: '600'
                            },
                            usePointStyle: true,
                                padding: 20
                        },
                        onClick: (event, legendItem, legend) => {
                                console.log('🔍 Legend clicada:', legendItem);
                            const chart = legend.chart;
                                const index = legendItem.datasetIndex; // ✅ CORREÇÃO: usar datasetIndex em vez de index
                            const meta = chart.getDatasetMeta(index);
                            
                            // ✅ ANIMAÇÃO OTIMIZADA PARA LEGENDAS
                            const originalOpacity = meta.hidden ? 0 : 1;
                            const targetOpacity = meta.hidden ? 1 : 0;
                            
                            // Configurar animação suave com easing personalizado
                            chart.options.animation = {
                                duration: 400, // 400ms para transição mais suave
                                easing: 'easeInOutCubic', // Easing mais suave
                                onProgress: (animation) => {
                                    // Aplicar transição de opacidade progressiva
                                    if (meta.dataset) {
                                        const progress = animation.currentStep / animation.numSteps;
                                        const opacity = meta.hidden ? 
                                            (1 - progress) : // Fade out
                                            progress;        // Fade in
                                        
                                        // Aplicar opacidade às barras
                                        if (meta.dataset.data) {
                                            meta.dataset.data.forEach((bar, barIndex) => {
                                                if (bar) {
                                                    bar.opacity = opacity;
                                                }
                                            });
                                        }
                                    }
                                }
                            };
                            
                            // Toggle visibility com animação
                            meta.hidden = !meta.hidden;
                            
                            // Aplicar transição de opacidade
                            if (meta.dataset) {
                                meta.dataset.hidden = meta.hidden;
                            }
                            
                            // Atualizar com animação
                            chart.update('active');
                            
                            // Resetar animação após conclusão
                            setTimeout(() => {
                                chart.options.animation.duration = 0; // Desabilitar para performance
                                chart.options.animation.onProgress = null; // Limpar callback
                            }, 450);
                            
                            // Mostrar mensagem - CORREÇÃO: verificar se o dataset existe
                            if (chart.data.datasets && chart.data.datasets[index]) {
                                const datasetName = chart.data.datasets[index].label;
                            const action = meta.hidden ? 'ocultado' : 'exibido';
                                this.showMessage(`${datasetName} ${action}`, 'info');
                            } else {
                                console.log('Dataset não encontrado para índice:', index);
                            }
                        }
                    },
                    tooltip: {
                        enabled: true,
                        backgroundColor: 'rgba(15, 23, 42, 0.95)',
                        titleColor: '#ffffff',
                            bodyColor: '#e2e8f0',
                        borderColor: 'rgba(148, 163, 184, 0.2)',
                        borderWidth: 1,
                        cornerRadius: 8,
                        displayColors: true,
                        callbacks: {
                            title: (tooltipItems) => {
                                return `Mês: ${tooltipItems[0].label}`;
                            },
                            label: (tooltipItems) => {
                                    const dataset = tooltipItems.dataset;
                                    const value = tooltipItems.parsed.y;
                                    return `${dataset.label}: ${value.toLocaleString('pt-BR')} pontos`;
                                }
                        }
                    }
                },
                scales: {
                    x: {
                            display: true,
                        title: {
                            display: true,
                            text: 'Meses',
                            color: '#ffffff',
                            font: {
                                    size: 14,
                                    weight: '600'
                                }
                            },
                        ticks: {
                                color: '#94a3b8',
                            font: {
                                    size: 12
                            }
                        },
                        grid: {
                                color: 'rgba(148, 163, 184, 0.1)'
                            }
                        },
                        y: {
                            display: true,
                        title: {
                            display: true,
                            text: 'Pontos',
                            color: '#ffffff',
                            font: {
                                    size: 14,
                                    weight: '600'
                                }
                            },
                            ticks: {
                                color: '#94a3b8',
                                font: {
                                    size: 12
                                }
                            },
                            grid: {
                                color: 'rgba(148, 163, 184, 0.1)'
                        }
                    }
                },
                interaction: {
                    intersect: false,
                    mode: 'index'
                },
                    elements: {
                        bar: {
                            borderWidth: 2,
                            borderRadius: 4
                    }
                }
            }
        });

            console.log('✅ Gráfico de barras criado com sucesso');
            
            // Mostrar container do gráfico
            const chartContainer = document.getElementById('excel-chart-container');
            if (chartContainer) {
                chartContainer.style.display = 'block';
            }
            
        } catch (error) {
            console.error('❌ Erro ao criar gráfico:', error);
            this.showMessage('Erro ao criar gráfico: ' + error.message, 'error');
        }
    },

    // Preparar dados do gráfico
    prepareChartData() {
        console.log('🔍 === DEBUG: PREPARANDO DADOS DO GRÁFICO ===');
        console.log('State data:', this.state.data);
        
        if (!this.state.data || !this.state.data.employees) {
            console.log('❌ Dados ou employees não encontrados');
            return { labels: [], datasets: [] };
        }

        const employees = Object.keys(this.state.data.employees);
        console.log('👥 Funcionários encontrados:', employees);
        
        // Obter meses únicos dos dados do Excel
        const months = this.getMonthsFromExcelData();
        console.log('📅 Meses extraídos:', months);
        
        // Preparar datasets para cada funcionário (igual ao da aba Gráficos)
        const datasets = [];
        
        employees.forEach((employeeName, index) => {
            console.log(`\n🔍 Processando funcionário: ${employeeName}`);
            const empData = this.state.data.employees[employeeName] || {};
            console.log('Dados do funcionário:', empData);
            
            // Processar registros individuais para criar dados por mês
            const monthlyData = this.processEmployeeRecords(empData, months);
            console.log(`📊 Dados mensais para ${employeeName}:`, monthlyData);
            
            // Cores baseadas no nome do funcionário (igual ao da aba Gráficos)
            const colors = this.getEmployeeColors(employeeName);
            
            datasets.push({
                label: employeeName,
                data: monthlyData,
                borderColor: colors.borderColor,
                backgroundColor: colors.backgroundColor,
            borderWidth: 2,
                tension: 0.4,
                fill: false
            });
        });

        const result = {
            labels: months,
            datasets: datasets
        };
        
        console.log('✅ Dados finais do gráfico:', result);
        return result;
    },

    // Processar registros de um funcionário para criar dados por mês
    processEmployeeRecords(empData, months) {
        console.log('🔍 Processando registros do funcionário:', empData);
        
        // Inicializar dados por mês
        const monthlyPoints = {};
        months.forEach(month => {
            monthlyPoints[month] = 0;
        });
        
        // Se temos registros individuais, processar eles
        if (empData.records && Array.isArray(empData.records)) {
            console.log(`📋 Processando ${empData.records.length} registros...`);
            
            empData.records.forEach((record, index) => {
                console.log(`  📋 Registro ${index + 1}:`, record);
                
                if (record.date && record.points) {
                    const month = this.getMonthFromDate(record.date);
                    if (month) {
                        // Converter para formato limpo
                        const cleanMonth = this.convertToCleanMonth(month);
                        if (monthlyPoints.hasOwnProperty(cleanMonth)) {
                            monthlyPoints[cleanMonth] += record.points;
                            console.log(`    📅 Adicionado ${record.points} pontos para ${cleanMonth}`);
                        } else {
                            console.log(`    ❌ Mês não encontrado: ${cleanMonth}`);
                        }
                    } else {
                        console.log(`    ❌ Mês inválido para data: ${record.date}`);
                    }
                }
            });
        } else if (empData.months) {
            // Se já temos dados por mês, usar eles
            console.log('📅 Usando dados por mês existentes');
            Object.entries(empData.months).forEach(([month, data]) => {
                // Converter para formato limpo
                const cleanMonth = this.convertToCleanMonth(month);
                if (monthlyPoints.hasOwnProperty(cleanMonth)) {
                    monthlyPoints[cleanMonth] = data.points || 0;
                    console.log(`  📅 ${cleanMonth}: ${data.points || 0} pontos`);
                }
            });
        } else {
            // Distribuir pontos totais pelos meses
            console.log('📊 Distribuindo pontos totais pelos meses');
            // ✅ CORREÇÃO: Usar as chaves corretas do backend (com underscore)
            const totalPoints = empData.total_points || empData.totalPoints || 0;
            const pointsPerMonth = Math.round(totalPoints / months.length);
            
            months.forEach(month => {
                monthlyPoints[month] = pointsPerMonth;
            });
        }
        
        // Converter para array na ordem dos meses
        const result = months.map(month => monthlyPoints[month] || 0);
        console.log('📊 Resultado final:', result);
        
        return result;
    },

    // Converter mês para formato limpo
    convertToCleanMonth(month) {
        const monthMap = {
            '01': 'Janeiro',
            '02': 'Fevereiro', 
            '03': 'Março',
            '04': 'Abril',
            '05': 'Maio',
            '06': 'Junho',
            '07': 'Julho',
            '08': 'Agosto',
            '09': 'Setembro',
            '10': 'Outubro',
            '11': 'Novembro',
            '12': 'Dezembro'
        };
        
        // Se é formato "MM/YYYY", converter para nome do mês
        if (month.includes('/')) {
            const [monthNum, year] = month.split('/');
            const monthName = monthMap[monthNum] || month;
            return `${monthName} ${year}`;
        }
        
        // Se já é nome do mês, verificar se tem ano
        if (month.includes(' ')) {
            return month; // Já está no formato correto
        }
        
        // Se é só nome do mês sem ano, adicionar ano atual
        const currentYear = new Date().getFullYear();
        return `${month} ${currentYear}`;
    },

    // Obter meses únicos dos dados do Excel
    getMonthsFromExcelData() {
        console.log('🔍 === DEBUG: EXTRAINDO MESES DOS DADOS ===');
        
        const months = new Set();
        
        if (this.state.data && this.state.data.employees) {
            console.log('📊 Processando dados dos funcionários...');
            
            Object.values(this.state.data.employees).forEach((empData, index) => {
                console.log(`\n👤 Funcionário ${index + 1}:`, empData);
                
                // Verificar se há dados de registros individuais
                if (empData.records && Array.isArray(empData.records)) {
                    console.log(`  📋 ${empData.records.length} registros individuais encontrados`);
                    this.extractMonthsFromRecords(empData.records, months);
                } else {
                    console.log('  ❌ Nenhum registro individual encontrado ou não é array');
                }
                
                // Verificar se há dados por mês
                if (empData.months) {
                    console.log('  📅 Meses encontrados:', Object.keys(empData.months));
                    Object.keys(empData.months).forEach(month => {
                        months.add(month);
                    });
                } else {
                    console.log('  ❌ Nenhum dado de meses encontrado');
                }
            });
        }
        
        console.log('📅 Meses únicos encontrados:', Array.from(months));
        
        // Se não encontrou meses específicos, tentar extrair dos registros
        if (months.size === 0) {
            console.log('🔍 Tentando extrair meses dos registros...');
            this.extractMonthsFromAllRecords(months);
        }
        
        // Converter meses para formato mais limpo
        const cleanMonths = this.cleanMonthNames(Array.from(months));
        console.log('📅 Meses limpos:', cleanMonths);
        
        return cleanMonths;
    },

    // Limpar nomes dos meses para formato mais legível
    cleanMonthNames(months) {
        const monthMap = {
            '01': 'Janeiro',
            '02': 'Fevereiro', 
            '03': 'Março',
            '04': 'Abril',
            '05': 'Maio',
            '06': 'Junho',
            '07': 'Julho',
            '08': 'Agosto',
            '09': 'Setembro',
            '10': 'Outubro',
            '11': 'Novembro',
            '12': 'Dezembro'
        };
        
        // Converter meses para formato limpo e remover duplicatas
        const cleanMonths = new Set();
        
        months.forEach(month => {
            let cleanMonth;
            
            // Se é formato "MM/YYYY", converter para nome do mês
            if (month.includes('/')) {
                const [monthNum, year] = month.split('/');
                const monthName = monthMap[monthNum] || month;
                cleanMonth = `${monthName} ${year}`;
            } else {
                // Se já é nome do mês, verificar se tem ano
                if (month.includes(' ')) {
                    cleanMonth = month; // Já está no formato correto
                } else {
                    // Se é só nome do mês sem ano, adicionar ano atual
                    const currentYear = new Date().getFullYear();
                    cleanMonth = `${month} ${currentYear}`;
                }
            }
            
            cleanMonths.add(cleanMonth);
        });
        
        // Ordenar meses cronologicamente
        const monthOrder = [
            'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
            'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
        ];
        
        const sortedMonths = Array.from(cleanMonths).sort((a, b) => {
            const aParts = a.split(' ');
            const bParts = b.split(' ');
            
            const aMonth = aParts[0];
            const bMonth = bParts[0];
            const aYear = parseInt(aParts[1]) || 0;
            const bYear = parseInt(bParts[1]) || 0;
            
            // Primeiro ordenar por ano
            if (aYear !== bYear) {
                return aYear - bYear;
            }
            
            // Depois por mês
            return monthOrder.indexOf(aMonth) - monthOrder.indexOf(bMonth);
        });
        
        console.log('📅 Meses limpos e ordenados:', sortedMonths);
        return sortedMonths;
    },

    // Extrair meses dos registros individuais
    extractMonthsFromRecords(records, monthsSet) {
        console.log('🔍 Extraindo meses dos registros:', records);
        
        // Verificar se records é um array ou um número
        if (typeof records === 'number') {
            console.log('❌ Records é um número, não um array. Tentando buscar registros individuais...');
            return;
        }
        
        if (!Array.isArray(records)) {
            console.log('❌ Records não é um array:', typeof records);
            return;
        }
        
        console.log(`📋 Processando ${records.length} registros individuais`);
        
        records.forEach((record, index) => {
            console.log(`  📋 Registro ${index + 1}:`, record);
            
            if (record.date) {
                const month = this.getMonthFromDate(record.date);
                if (month) {
                    monthsSet.add(month);
                    console.log(`    📅 Mês extraído: ${month}`);
                }
            }
        });
    },

    // Extrair meses de todos os registros
    extractMonthsFromAllRecords(monthsSet) {
        console.log('🔍 Extraindo meses de todos os registros...');
        
        if (this.state.data && this.state.data.employees) {
            Object.values(this.state.data.employees).forEach(empData => {
                if (empData.records) {
                    this.extractMonthsFromRecords(empData.records, monthsSet);
                }
            });
        }
    },

    // Obter mês a partir de uma data (considerando mês do dia 26 ao 25)
    getMonthFromDate(dateString) {
        console.log('🔍 Processando data:', dateString);
        
        try {
            let date;
            
            // Se é uma string, tentar parsear
            if (typeof dateString === 'string') {
                date = new Date(dateString);
            } else if (dateString instanceof Date) {
                date = dateString;
            } else {
                console.log('  ❌ Formato de data inválido:', typeof dateString);
                return null;
            }
            
            console.log('  📅 Data parseada:', date);
            
            if (isNaN(date.getTime())) {
                console.log('  ❌ Data inválida');
                return null;
            }
            
            // Lógica: mês vai do dia 26 ao dia 25
            const day = date.getDate();
            let month = date.getMonth();
            let year = date.getFullYear();
            
            // Se o dia é 26 ou maior, o mês é o próximo
            if (day >= 26) {
                month++;
                if (month > 11) {
                    month = 0;
                    year++;
                }
            }
            
            const monthNames = [
                'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
            ];
            
            const monthName = monthNames[month];
            console.log(`  📅 Mês calculado: ${monthName} (dia ${day})`);
            
            return monthName;
        } catch (error) {
            console.error('❌ Erro ao processar data:', error);
            return null;
        }
    },

    // Obter cores para cada funcionário (igual ao da aba Gráficos)
    getEmployeeColors(employeeName) {
        const colorMap = {
            'Matheus': {
                borderColor: 'rgba(34, 197, 94, 1)',    // Verde
                backgroundColor: 'rgba(34, 197, 94, 0.1)'
            },
            'Maurício': {
                borderColor: 'rgba(59, 130, 246, 1)',   // Azul
                backgroundColor: 'rgba(59, 130, 246, 0.1)'
            },
            'Rodrigo': {
                borderColor: 'rgba(147, 51, 234, 1)',   // Roxo
                backgroundColor: 'rgba(147, 51, 234, 0.1)'
            },
            'Wesley': {
                borderColor: 'rgba(239, 68, 68, 1)',    // Vermelho
                backgroundColor: 'rgba(239, 68, 68, 0.1)'
            }
        };
        
        return colorMap[employeeName] || {
            borderColor: 'rgba(156, 163, 175, 1)',      // Cinza padrão
            backgroundColor: 'rgba(156, 163, 175, 0.1)'
        };
    },

    // Gerar cor baseada no índice
    getColor(index) {
        const colors = [
            'rgba(59, 130, 246, 0.8)',
            'rgba(16, 185, 129, 0.8)',
            'rgba(245, 158, 11, 0.8)',
            'rgba(239, 68, 68, 0.8)',
            'rgba(139, 92, 246, 0.8)'
        ];
        return colors[index % colors.length];
    },

    // ✅ REMOVIDO: Funções de clique dos cards - não fazem sentido
    // bindStatCardEvents() { ... }
    // filterByStat(card) { ... }
    // applyStatFilter(statType) { ... }
    // filterByRecords() { ... }
    // filterByPoints() { ... }
    // filterByMonths() { ... }

    // Mostrar detalhes do funcionário
    showEmployeeDetails(employee, month) {
        if (!this.state.data || !this.state.data.employees[employee]) {
            return;
        }

        const empData = this.state.data.employees[employee];
        const monthData = empData.months[month];
        
        if (!monthData) {
            this.showMessage(`Sem dados para ${employee} em ${month}`, 'info');
            return;
        }

        const details = `
            Funcionário: ${employee}
            Mês: ${month}
            Registros: ${monthData.records}
            Pontos: ${monthData.points}
            Média: ${(monthData.points / monthData.records).toFixed(2)} pontos/registro
        `;

        alert(details); // Substituir por modal mais elegante se necessário
    },

    // Mostrar mensagem
    showMessage(message, type = 'info') {
        // Remover mensagem anterior
        const existingMessage = document.querySelector('.excel-message');
        if (existingMessage) {
            existingMessage.remove();
        }

        // Criar nova mensagem
        const messageDiv = document.createElement('div');
        messageDiv.className = `excel-message excel-${type}`;
        messageDiv.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-triangle' : 'info-circle'}"></i>
            ${message}
        `;

        // Inserir no container
        const container = document.querySelector('.excel-dashboard-container');
        if (container) {
            container.insertBefore(messageDiv, container.firstChild);
        }
            
        // Remover após 5 segundos
            setTimeout(() => {
                if (messageDiv.parentNode) {
                    messageDiv.remove();
                }
        }, 5000);
    },

    // Debug massivo para analisar dados
    debugDataStructure() {
        console.log('🔍 === DEBUG MASSIVO: ESTRUTURA DOS DADOS ===');
        console.log('State completo:', this.state);
        
        if (this.state.data) {
            console.log('📊 Dados encontrados:', this.state.data);
            
            if (this.state.data.employees) {
                console.log('👥 Estrutura dos funcionários:');
                Object.entries(this.state.data.employees).forEach(([name, data]) => {
                    console.log(`\n👤 ${name}:`, data);
                    
                    if (data.records) {
                        console.log(`  📋 ${data.records.length} registros encontrados`);
                        if (Array.isArray(data.records)) {
                            data.records.slice(0, 3).forEach((record, index) => {
                                console.log(`    Registro ${index + 1}:`, record);
                            });
                        } else {
                            console.log(`    ❌ Records não é array: ${typeof data.records}`);
                        }
                    }
                    
                    if (data.months) {
                        console.log(`  📅 Meses:`, Object.keys(data.months));
                        Object.entries(data.months).forEach(([month, monthData]) => {
                            console.log(`    ${month}:`, monthData);
                        });
                    }
                });
            } else {
                console.log('❌ Nenhum funcionário encontrado');
            }
        } else {
            console.log('❌ Nenhum dado encontrado');
        }
    },

    // Limpar dados
    clearData() {
        this.state.data = null;
        this.state.chartInstance = null;
        
        // Esconder elementos
        const statsGrid = document.getElementById('excel-stats-grid');
        const chartContainer = document.getElementById('excel-chart-container');
        
        if (statsGrid) statsGrid.style.display = 'none';
        if (chartContainer) chartContainer.style.display = 'none';
        
        // Limpar canvas
        const canvas = document.getElementById('excel-chart');
        if (canvas) {
            const ctx = canvas.getContext('2d');
            ctx.clearRect(0, 0, canvas.width, canvas.height);
        }
    },

    // Limpar e recriar Chart.js completamente
    async resetChartJS() {
        console.log('🔄 Resetando Chart.js completamente...');
        
        // Destruir instância atual
        if (this.state.chartInstance) {
            try {
                this.state.chartInstance.destroy();
                this.state.chartInstance = null;
            } catch (e) {
                console.log('Erro ao destruir chart:', e);
            }
        }
        
        // Limpar canvas
        const canvas = document.getElementById('excel-chart');
        if (canvas) {
            const ctx = canvas.getContext('2d');
            ctx.clearRect(0, 0, canvas.width, canvas.height);
        }
        
        // Remover Chart.js global se existir
        if (typeof window.Chart !== 'undefined') {
            delete window.Chart;
            console.log('Chart.js global removido');
        }
        
        // Aguardar um pouco
        await new Promise(resolve => setTimeout(resolve, 100));
        
        // Recarregar Chart.js
        await this.loadChartJS();
        
        console.log('✅ Chart.js resetado com sucesso');
    },

    // Testar legendas clicáveis
    testLegendClick() {
        console.log('🧪 === TESTE LEGENDAS CLICÁVEIS ===');
        
        if (!this.state.chartInstance) {
            console.log('❌ Nenhum gráfico encontrado. Carregue dados reais primeiro.');
            return;
        }
        
        const chart = this.state.chartInstance;
        console.log('📊 Gráfico encontrado:', chart);
        console.log('📊 Datasets:', chart.data.datasets);
        console.log('📊 Legendas:', chart.options.plugins.legend);
        
        // Simular clique na primeira legenda
        const legendItems = chart.legend.legendItems;
        if (legendItems && legendItems.length > 0) {
            console.log('🔍 Legend items:', legendItems);
            console.log('🔍 Primeira legenda:', legendItems[0]);
            
            // Simular clique
            const firstLegendItem = legendItems[0];
            if (firstLegendItem) {
                console.log('🖱️ Simulando clique na legenda:', firstLegendItem.text);
                
                // Chamar onClick manualmente
                const onClick = chart.options.plugins.legend.onClick;
                if (onClick) {
                    onClick(null, firstLegendItem, chart.legend);
                    console.log('✅ Clique simulado com sucesso!');
                } else {
                    console.log('❌ onClick não encontrado');
                }
            }
        } else {
            console.log('❌ Nenhuma legenda encontrada');
        }
    },

    // Testar animação das legendas
    testLegendAnimation() {
        console.log('🎬 === TESTE ANIMAÇÃO DAS LEGENDAS ===');
        
        if (!this.state.chartInstance) {
            console.log('❌ Nenhum gráfico encontrado. Carregue dados reais primeiro.');
            return;
        }
        
        const chart = this.state.chartInstance;
        console.log('📊 Testando animação no gráfico:', chart);
        
        // Simular clique em todas as legendas para testar animação
        const legendItems = chart.legend.legendItems;
        if (legendItems && legendItems.length > 0) {
            console.log('🎬 Testando animação em', legendItems.length, 'legendas...');
            
            legendItems.forEach((legendItem, index) => {
                setTimeout(() => {
                    console.log(`🎬 Animando legenda ${index + 1}:`, legendItem.text);
                    
                    // Chamar onClick manualmente
                    const onClick = chart.options.plugins.legend.onClick;
                    if (onClick) {
                        onClick(null, legendItem, chart.legend);
                    }
                }, index * 500); // Delay de 500ms entre cada teste
            });
            
            console.log('✅ Teste de animação iniciado! Observe as transições suaves.');
        } else {
            console.log('❌ Nenhuma legenda encontrada para testar');
        }
    },

    // Testar animação com efeitos visuais
    testVisualAnimation() {
        console.log('🎨 === TESTE ANIMAÇÃO VISUAL ===');
        
        if (!this.state.chartInstance) {
            console.log('❌ Nenhum gráfico encontrado. Carregue dados reais primeiro.');
            return;
        }
        
        const chart = this.state.chartInstance;
        console.log('🎨 Testando animação visual no gráfico:', chart);
        
        // Simular sequência de animações
        const legendItems = chart.legend.legendItems;
        if (legendItems && legendItems.length > 0) {
            console.log('🎨 Iniciando sequência de animações visuais...');
            
            // Sequência: ocultar todos, depois mostrar um por um
            let currentIndex = 0;
            
            const animateSequence = () => {
                if (currentIndex < legendItems.length) {
                    const legendItem = legendItems[currentIndex];
                    console.log(`🎨 Animando legenda ${currentIndex + 1}:`, legendItem.text);
                    
                    // Chamar onClick manualmente
                    const onClick = chart.options.plugins.legend.onClick;
                    if (onClick) {
                        onClick(null, legendItem, chart.legend);
                    }
                    
                    currentIndex++;
                    setTimeout(animateSequence, 800); // Delay maior para observar
                } else {
                    console.log('✅ Sequência de animação visual concluída!');
                }
            };
            
            // Iniciar sequência após um delay
            setTimeout(animateSequence, 500);
            
        } else {
            console.log('❌ Nenhuma legenda encontrada para testar');
        }
    },

    // Corrigir meses duplicados e organizar cronologicamente
    fixDuplicateMonths() {
        console.log('🔧 === CORRIGINDO MESES DUPLICADOS ===');
        
        if (!this.state.data || !this.state.data.employees) {
            console.log('❌ Nenhum dado encontrado');
            return;
        }
        
        // Coletar todos os meses únicos
        const allMonths = new Set();
        
        Object.values(this.state.data.employees).forEach(empData => {
            // Extrair meses dos registros
            if (empData.records && Array.isArray(empData.records)) {
                empData.records.forEach(record => {
                    if (record.date) {
                        const month = this.getMonthFromDate(record.date);
                        if (month) {
                            allMonths.add(month);
                        }
                    }
                });
            }
            
            // Extrair meses dos dados por mês
            if (empData.months) {
                Object.keys(empData.months).forEach(month => {
                    allMonths.add(month);
                });
            }
        });
        
        console.log('📅 Meses encontrados (antes da correção):', Array.from(allMonths));
        
        // Limpar e ordenar meses
        const cleanMonths = this.cleanMonthNames(Array.from(allMonths));
        
        console.log('📅 Meses limpos e ordenados:', cleanMonths);
        
        // Atualizar dados com meses corrigidos
        Object.values(this.state.data.employees).forEach(empData => {
            // Processar registros com meses corrigidos
            if (empData.records && Array.isArray(empData.records)) {
                empData.records.forEach(record => {
                    if (record.date) {
                        const month = this.getMonthFromDate(record.date);
                        if (month) {
                            record.month = this.convertToCleanMonth(month);
                        }
                    }
                });
            }
            
            // Processar dados por mês com meses corrigidos
            if (empData.months) {
                const correctedMonths = {};
                Object.entries(empData.months).forEach(([month, data]) => {
                    const cleanMonth = this.convertToCleanMonth(month);
                    correctedMonths[cleanMonth] = data;
                });
                empData.months = correctedMonths;
            }
        });
        
        console.log('✅ Meses corrigidos com sucesso!');
        return cleanMonths;
    },

    // Testar se a aba Gráficos está funcionando
    testChartsTab() {
        console.log('📊 === TESTE ABA GRÁFICOS ===');
        
        // Verificar se os elementos da aba Gráficos existem
        const chartsTab = document.getElementById('charts-tab');
        const weeklyChart = document.getElementById('weeklyChart');
        const monthlyChart = document.getElementById('monthlyChart');
        const dailyChart = document.getElementById('dailyChart');
        
        console.log('📊 Aba Gráficos:', chartsTab ? '✅ Encontrada' : '❌ Não encontrada');
        console.log('📊 Weekly Chart:', weeklyChart ? '✅ Encontrado' : '❌ Não encontrado');
        console.log('📊 Monthly Chart:', monthlyChart ? '✅ Encontrado' : '❌ Não encontrado');
        console.log('📊 Daily Chart:', dailyChart ? '✅ Encontrado' : '❌ Não encontrado');
        
        // Verificar se o dashboard instance está funcionando
        if (window.dashboardInstance) {
            console.log('📊 Dashboard Instance:', '✅ Encontrado');
            console.log('📊 Charts:', Object.keys(window.dashboardInstance.charts || {}));
        } else {
            console.log('📊 Dashboard Instance:', '❌ Não encontrado');
        }
        
        // Verificar se Chart.js está funcionando
        if (typeof Chart !== 'undefined') {
            console.log('📊 Chart.js:', '✅ Disponível');
            console.log('📊 Chart.defaults:', Chart.defaults ? '✅ Configurado' : '❌ Não configurado');
        } else {
            console.log('📊 Chart.js:', '❌ Não disponível');
        }
        
        console.log('📊 Teste concluído! Verifique se os gráficos estão funcionando.');
    },

    // Forçar exibição dos cards para debug
    forceShowCards() {
        console.log('🔍 === DEBUG: FORÇANDO EXIBIÇÃO DOS CARDS ===');
        
        // Verificar se os elementos existem
        const elements = [
            'total-files', 'total-records', 'total-points', 'total-profit',
            'files-detail', 'records-detail', 'points-detail', 'profit-detail',
            'excel-stats-grid'
        ];
        
        elements.forEach(id => {
            const element = document.getElementById(id);
            console.log(`🔍 ${id}:`, element ? '✅ Encontrado' : '❌ Não encontrado');
            if (element) {
                console.log(`  📝 Conteúdo atual: "${element.textContent}"`);
            }
        });
        
        // Forçar exibição do grid
        const statsGrid = document.getElementById('excel-stats-grid');
        if (statsGrid) {
            statsGrid.style.display = 'grid';
            console.log('✅ Grid forçado para exibição');
        }
        
        // ✅ REMOVIDO: Não aplicar dados falsos
        console.log('ℹ️ Cards exibidos - carregue dados reais com loadFolder()');
    }
};

// Inicializar quando o DOM estiver pronto
if (document.readyState === 'loading') {
document.addEventListener('DOMContentLoaded', () => {
        window.ExcelDashboard.init();
    });
} else {
    window.ExcelDashboard.init();
}

// Comandos de debug para o console
console.log('🔧 === EXCEL DASHBOARD DEBUG ===');
console.log('Comandos disponíveis:');
console.log('  window.ExcelDashboard.debugDataStructure() - Analisar estrutura dos dados');
console.log('  window.ExcelDashboard.clearData() - Limpar dados');
console.log('  window.ExcelDashboard.loadFolder() - Carregar pasta Excel (DADOS REAIS)');
console.log('  window.ExcelDashboard.debugLoadFolder() - Debugar a função loadFolder');
console.log('  window.ExcelDashboard.resetChartJS() - Resetar Chart.js completamente');
console.log('  window.ExcelDashboard.testLegendClick() - Testar legendas clicáveis');
console.log('  window.ExcelDashboard.testLegendAnimation() - Testar animação das legendas');
console.log('  window.ExcelDashboard.testVisualAnimation() - Testar animação visual das legendas');
console.log('  window.ExcelDashboard.fixDuplicateMonths() - Corrigir meses duplicados');
console.log('  window.ExcelDashboard.fixInitialLoadingState() - Corrigir estado inicial do loading');
console.log('  window.ExcelDashboard.testChartsTab() - Testar se a aba Gráficos está funcionando');
console.log('  window.ExcelDashboard.forceShowCards() - Forçar exibição dos cards (SEM DADOS FALSOS)');

// ===== FIM DO JAVASCRIPT OTIMIZADO PARA ABA EXCEL ===== 