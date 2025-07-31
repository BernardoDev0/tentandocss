// ===== FORÇAR CORREÇÕES ABA EXCEL =====

class ExcelForceFix {
  constructor() {
    this.init();
  }

  init() {
    console.log('🔧 Forçando correções da aba Excel...');
    this.applyAllFixes();
  }

  applyAllFixes() {
    // 1. Forçar inicialização do ExcelDashboard
    this.forceExcelDashboardInit();
    
    // 2. Corrigir Chart.js
    this.fixChartJS();
    
    // 3. Corrigir dados da API
    this.fixAPIData();
    
    // 4. Corrigir elementos
    this.fixElements();
    
    // 5. Remover botão "Mostrar Todos"
    this.removeResetButton();
    
    console.log('✅ Correções estruturais aplicadas!');
  }

  forceExcelDashboardInit() {
    console.log('🔄 Forçando inicialização do ExcelDashboard...');
    
    // Se ExcelDashboard não existe, criar uma versão básica
    if (!window.ExcelDashboard) {
      window.ExcelDashboard = {
        state: {
          isLoaded: false,
          isLoading: false,
          data: null,
          chartInstance: null
        },
        init() {
          console.log('ExcelDashboard: Inicializando...');
          this.bindEvents();
        },
        bindEvents() {
          const loadBtn = document.getElementById('load-folder-btn');
          if (loadBtn) {
            loadBtn.addEventListener('click', () => this.loadFolder());
          }
        },
        async loadFolder() {
          console.log('📁 Carregando pasta de arquivos Excel...');
          this.showMessage('Carregando arquivos Excel...', 'info');
          
          try {
            const response = await fetch('/api/excel/load_folder', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json'
              },
              body: JSON.stringify({
                folder_path: 'registros monitorar'
              })
            });

            const data = await response.json();

            if (data.status === 'success') {
              this.state.data = data.data || {};
              const statistics = data.statistics || {};
              this.updateStatistics(statistics);
              this.showMessage('Arquivos carregados com sucesso!', 'success');
              this.initializeChart();
            } else {
              throw new Error(data.message || 'Erro ao carregar arquivos');
            }

          } catch (error) {
            console.error('Erro ao carregar pasta:', error);
            this.showMessage(`Erro: ${error.message}`, 'error');
          }
        },
        // Atualizar estatísticas
        updateStatistics(stats) {
            console.log('🔧 === FORCE FIX: ATUALIZANDO ESTATÍSTICAS ===');
            
            // ✅ CORREÇÃO: Usar as chaves corretas do backend (com underscore)
            const totalPoints = stats.total_points || stats.totalPoints || 0;
            
            const elements = {
                'total-files': stats.total_files || stats.totalFiles || 0,
                'total-records': stats.total_records || stats.totalRecords || 0,
                'total-points': totalPoints,
                'total-profit': this.calculateProfit(totalPoints)
            };

            console.log('📊 Elementos para atualizar:', elements);

            Object.entries(elements).forEach(([id, value]) => {
                const element = document.getElementById(id);
                if (element) {
                    console.log(`🔧 ${id} atualizado para: ${value}`);
                    element.textContent = value;
                }
            });

            // Atualizar detalhes dos cards
            this.updateCardDetails(stats);

            // Forçar exibição do grid
            const statsGrid = document.getElementById('excel-stats-grid');
            if (statsGrid) {
                statsGrid.style.display = 'grid';
            }
        },

        // Calcular lucro total
        calculateProfit(totalPoints) {
            const profit = totalPoints * 3.25;
            return `R$ ${profit.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
        },

        // Atualizar detalhes dos cards
        updateCardDetails(stats) {
            console.log('🔧 === FORCE FIX: ATUALIZANDO DETALHES DOS CARDS ===');
            
            // ✅ CORREÇÃO: Usar as chaves corretas do backend (com underscore)
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

            Object.entries(details).forEach(([id, text]) => {
                const element = document.getElementById(id);
                if (element) {
                    element.textContent = text;
                }
            });
        },
        initializeChart() {
          console.log('📊 Inicializando gráfico...');
          const chartContainer = document.getElementById('excel-chart-container');
          if (chartContainer) {
            chartContainer.style.display = 'block';
          }
        },
        showMessage(message, type = 'info') {
          const messageDiv = document.createElement('div');
          messageDiv.className = `excel-message excel-${type}`;
          messageDiv.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-triangle' : 'info-circle'}"></i>
            ${message}
          `;

          const container = document.querySelector('.excel-dashboard-container');
          if (container) {
            container.insertBefore(messageDiv, container.firstChild);
          }

          setTimeout(() => {
            if (messageDiv.parentNode) {
              messageDiv.remove();
            }
          }, 5000);
        }
      };
      
      window.ExcelDashboard.init();
      console.log('✅ ExcelDashboard criado e inicializado');
    }
  }

  fixChartJS() {
    console.log('🔧 Corrigindo problemas do Chart.js...');
    
    // 1. Verificar se Chart.js está carregado
    if (typeof Chart === 'undefined') {
      console.log('⚠️ Chart.js não encontrado, tentando carregar...');
      this.loadChartJS();
      return;
    }
    
    // 2. Verificar configurações globais
    // ✅ CORREÇÃO: NÃO CONFIGURAR GLOBALMENTE - só para o gráfico do Excel
    console.log('✅ Verificando Chart.js sem configurar globalmente');
    
    // 3. Verificar canvas
    const canvas = document.getElementById('excel-chart');
    if (canvas) {
      // Garantir que o canvas tem dimensões corretas
      canvas.width = canvas.offsetWidth;
      canvas.height = canvas.offsetHeight;
      console.log('✅ Canvas dimensionado corretamente');
    }
    
    // 4. Destruir gráfico anterior se existir
    if (window.ExcelDashboard && window.ExcelDashboard.state.chartInstance) {
      try {
        window.ExcelDashboard.state.chartInstance.destroy();
        window.ExcelDashboard.state.chartInstance = null;
        console.log('✅ Gráfico anterior destruído');
      } catch (error) {
        console.warn('⚠️ Erro ao destruir gráfico anterior:', error);
      }
    }
    
    console.log('✅ Problemas do Chart.js corrigidos');
  }

  // Carregar Chart.js se necessário
  loadChartJS() {
    return new Promise((resolve, reject) => {
      const script = document.createElement('script');
      script.src = 'https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js';
      script.onload = () => {
        console.log('✅ Chart.js carregado com sucesso');
        this.fixChartJS(); // Aplicar correções após carregar
        resolve();
      };
      script.onerror = () => {
        console.error('❌ Erro ao carregar Chart.js');
        reject(new Error('Falha ao carregar Chart.js'));
      };
      document.head.appendChild(script);
    });
  }

  fixAPIData() {
    console.log('🔧 Corrigindo dados da API...');
    const statElements = [
      'total-files', 'total-records', 'total-points', 'total-profit'
    ];

    statElements.forEach(id => {
      const element = document.getElementById(id);
      if (element && (element.textContent === 'undefined' || element.textContent === '')) {
        element.textContent = '0';
      }
    });

    const detailElements = [
      'files-detail', 'records-detail', 'points-detail', 'profit-detail'
    ];

    detailElements.forEach(id => {
      const element = document.getElementById(id);
      if (element && (element.textContent === 'undefined' || element.textContent === '')) {
        element.textContent = 'Dados não disponíveis';
      }
    });
    console.log('✅ Dados da API corrigidos');
  }

  fixElements() {
    console.log('🔧 Corrigindo elementos...');
    
    // Corrigir valores undefined nos cards
    const statElements = [
      'total-files', 'total-records', 'total-points', 'total-profit'
    ];
    
    statElements.forEach(id => {
      const element = document.getElementById(id);
      if (element && (element.textContent === 'undefined' || element.textContent === '')) {
        element.textContent = '0';
      }
    });
    
    // Corrigir detalhes dos cards
    const detailElements = [
      'files-detail', 'records-detail', 'points-detail', 'profit-detail'
    ];
    
    detailElements.forEach(id => {
      const element = document.getElementById(id);
      if (element && (element.textContent === 'undefined' || element.textContent === '')) {
        element.textContent = 'Dados não disponíveis';
      }
    });
  }

  removeResetButton() {
    console.log('🗑️ Removendo botão "Mostrar Todos"...');
    
    const resetBtn = document.getElementById('reset-filters');
    if (resetBtn) {
      resetBtn.remove();
      console.log('✅ Botão removido');
    }
    
    const chartControls = document.querySelector('.excel-chart-container .chart-controls');
    if (chartControls) {
      chartControls.remove();
      console.log('✅ Controles removidos');
    }
  }
}

// Executar automaticamente
window.excelForceFix = new ExcelForceFix();

// Comando manual
console.log('🔧 Comando disponível: window.excelForceFix.applyAllFixes()');

// ===== FIM DO FORÇAR CORREÇÕES ABA EXCEL ===== 