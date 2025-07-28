// Função para inicializar os gráficos do dashboard do funcionário
function initEmployeeDashboard(monthlyData, weeklyData) {
    // Gráfico de evolução mensal
    if (document.getElementById('monthlyChart')) {
      var monthlyCtx = document.getElementById('monthlyChart').getContext('2d');
      var monthlyChart = new Chart(monthlyCtx, {
        type: 'line',
        data: {
          labels: monthlyData.labels,
          datasets: [{
            label: 'Pontos',
            data: monthlyData.points,
            borderColor: '#3a6ff7',
            backgroundColor: 'rgba(58, 111, 247, 0.1)',
            borderWidth: 2,
            tension: 0.3,
            fill: true
          }, {
            label: 'Meta',
            data: monthlyData.goals,
            borderColor: 'rgba(233, 185, 73, 0.7)',
            borderWidth: 2,
            borderDash: [5, 5],
            fill: false,
            pointRadius: 0
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'top',
              labels: {
                color: '#e2e8f0'
              }
            },
            tooltip: {
              mode: 'index',
              intersect: false
            }
          },
          scales: {
            x: {
              grid: {
                color: 'rgba(255, 255, 255, 0.1)'
              },
              ticks: {
                color: '#a0aec0'
              }
            },
            y: {
              beginAtZero: true,
              grid: {
                color: 'rgba(255, 255, 255, 0.1)'
              },
              ticks: {
                color: '#a0aec0'
              }
            }
          }
        }
      });
    }
  
    // Gráfico de desempenho semanal
    if (document.getElementById('weeklyChart')) {
      var weeklyCtx = document.getElementById('weeklyChart').getContext('2d');
      var weeklyChart = new Chart(weeklyCtx, {
        type: 'bar',
        data: {
          labels: weeklyData.labels,
          datasets: [{
            label: 'Pontos',
            data: weeklyData.points,
            backgroundColor: [
              'rgba(58, 111, 247, 0.7)',
              'rgba(56, 161, 105, 0.7)',
              'rgba(233, 185, 73, 0.7)',
              'rgba(229, 62, 62, 0.7)',
              'rgba(128, 90, 213, 0.7)'
            ],
            borderColor: [
              'rgba(58, 111, 247, 1)',
              'rgba(56, 161, 105, 1)',
              'rgba(233, 185, 73, 1)',
              'rgba(229, 62, 62, 1)',
              'rgba(128, 90, 213, 1)'
            ],
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              display: false
            }
          },
          scales: {
            x: {
              grid: {
                color: 'rgba(255, 255, 255, 0.1)'
              },
              ticks: {
                color: '#a0aec0'
              }
            },
            y: {
              beginAtZero: true,
              grid: {
                color: 'rgba(255, 255, 255, 0.1)'
              },
              ticks: {
                color: '#a0aec0'
              }
            }
          }
        }
      });
    }
  }
  
  // Configuração das tabs
  function setupTabs() {
    document.querySelectorAll('.tab').forEach(function(tab) {
      tab.addEventListener('click', function() {
        // Remover classe active de todas as tabs
        document.querySelectorAll('.tab').forEach(function(t) {
          t.classList.remove('active');
        });
        document.querySelectorAll('.tab-content').forEach(function(c) {
          c.classList.remove('active');
        });
        
        // Adicionar classe active na tab clicada
        tab.classList.add('active');
        document.getElementById(tab.dataset.tab).classList.add('active');

        // Atualizar hash na URL para permitir retorno à mesma aba após recarregar
        window.location.hash = tab.dataset.tab;
      });
    });
  }
  
  // Inicializar quando o documento estiver pronto
  document.addEventListener('DOMContentLoaded', function() {
    setupTabs();

    // Se existir hash na URL (ex.: #history), ativar a tab correspondente
    const hash = window.location.hash.replace('#', '');
    if (hash) {
      const targetTab = document.querySelector('.tab[data-tab="' + hash + '"]');
      if (targetTab) {
        targetTab.click();
      }
    }

    if(successMsg){
        // Add classe toast para centralizar
        successMsg.classList.add('toast');

        // Criar botão fechar
        const closeBtn = document.createElement('button');
        closeBtn.textContent = 'Fechar';
        closeBtn.className = 'toast-close';
        closeBtn.addEventListener('click', function(){
            successMsg.remove();
        });
        successMsg.appendChild(closeBtn);
    }
  });