// IMPORTANTE: Adicionar <script src="static/js/chart-optimized.js"></script> no template
// Variáveis globais para controle de estado
let currentPage = 1;
let currentSelectedWeek = '';

// Função para inicializar os gráficos do dashboard do funcionário
function initEmployeeDashboard(monthlyData, weeklyData) {
    // Gráfico de evolução mensal
    if (document.getElementById('monthlyChart')) {
      var monthlyChart = createOptimizedChart('monthlyChart', {
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
      }, {
        type: 'line',
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
      var weeklyChart = createOptimizedChart('weeklyChart', {
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
      }, {
        type: 'bar',
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
  
  // Função para atualizar gráfico semanal (CORRIGIDA)
  function updateWeeklyChart(weeklyData) {
      if (!weeklyData || !window.employeeId) {
          console.log('Dados semanais ou employeeId não disponíveis');
          return;
      }
      
      // Filtrar apenas os dados do funcionário logado
      const filteredData = {
          labels: weeklyData.labels || [],
          points: weeklyData.points || []
      };
      
      console.log('Dados filtrados para o funcionário:', filteredData);
      
      // Atualizar o gráfico se existir
      if (document.getElementById('weeklyChart')) {
          // Recriar o gráfico com os dados filtrados
          initEmployeeDashboard({}, filteredData);
      }
  }
  
  // Função para buscar histórico com paginação e filtro de semana
  function fetchHistory(page, selectedWeek) {
      // Se selectedWeek não for fornecido, usar o valor atual
      if (selectedWeek !== undefined) {
          currentSelectedWeek = selectedWeek;
      }
      
      let url = `/api/entries?page=${page}&employee_id=${window.employeeId || ''}`;
      if (currentSelectedWeek && currentSelectedWeek !== '') {
          url += `&week=${currentSelectedWeek}`;
      }
      
      fetch(url)
          .then(response => response.json())
          .then(data => {
              console.log('Histórico:', data);
              if (data.entries) {
                  renderHistory(data.entries);
                  currentPage = page;
                  // Atualizar controles de paginação se necessário
                  updatePaginationControls(data.pagination);
              }
          })
          .catch(error => console.error('Erro ao buscar histórico:', error));
  }
  
  // Função para renderizar histórico na tabela
  function renderHistory(entries) {
      const tbody = document.querySelector('#history .glass-table tbody');
      if (!tbody) return;
      
      tbody.innerHTML = '';
      
      if (entries && entries.length > 0) {
          entries.forEach(entry => {
              const tr = document.createElement('tr');
              
              // Formatar data
              const [datePart, timePart] = entry.date.split(' ');
              const [yyyy, mm, dd] = datePart.split('-');
              const brDate = `${dd}/${mm}/${yyyy}`;
              const brTime = timePart ? timePart.substring(0, 5) : '-';
              
              tr.innerHTML = `
                  <td>${brDate}</td>
                  <td>${brTime}</td>
                  <td>${entry.refinery || ''}</td>
                  <td>${entry.points}</td>
                  <td>${entry.observations || ''}</td>
              `;
              
              tbody.appendChild(tr);
          });
      } else {
          tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;padding:1rem">Nenhum registro encontrado.</td></tr>';
      }
  }
  
  // Função para atualizar controles de paginação
  function updatePaginationControls(pagination) {
      // Implementar controles de paginação se necessário
      if (pagination) {
          console.log('Paginação:', pagination);
          // Aqui você pode adicionar botões de navegação
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
    
      // Configurar employeeId global se disponível
      if (typeof employeeId !== 'undefined') {
          window.employeeId = employeeId;
      }
      
      // Configurar listener para mudança de semana
      const weekSelect = document.getElementById('week');
      if (weekSelect) {
          weekSelect.addEventListener('change', function() {
              currentSelectedWeek = this.value;
              // Se estiver na aba de histórico, recarregar dados
              const historyTab = document.querySelector('.tab[data-tab="history"]');
              if (historyTab && historyTab.classList.contains('active')) {
                  fetchHistory(1, currentSelectedWeek);
              }
          });
      }
    
      // Se existir hash na URL (ex.: #history), ativar a tab correspondente
      const hash = window.location.hash.replace('#', '');
      if (hash) {
          const targetTab = document.querySelector('.tab[data-tab="' + hash + '"]');
          if (targetTab) {
              targetTab.click();
          }
      }

      const successMsg = document.querySelector('.success-message');
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