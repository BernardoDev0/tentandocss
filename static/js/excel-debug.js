// ===== DEBUG PARA ABA EXCEL =====

class ExcelDebug {
  constructor() {
    this.init();
  }

  init() {
    console.log('🔍 Debug da Aba Excel iniciado');
    console.log('📋 Comandos disponíveis:');
    console.log('   window.excelDebug.diagnose() - Diagnóstico detalhado');
    console.log('   window.excelDebug.checkElements() - Verificar elementos');
    console.log('   window.excelDebug.checkData() - Verificar dados');
    console.log('   window.excelDebug.testAPI() - Testar API');
    console.log('   window.excelDebug.fixErrors() - Corrigir erros comuns');
    console.log('   window.excelDebug.diagnoseAPI() - DEBUG MASSIVO DA API');
    console.log('   window.excelDebug.testAPIData() - Teste completo da API');
    console.log('   window.excelDebug.quickTest() - Teste rápido completo');
    console.log('   window.excelDebug.debugMassivo() - DEBUG MASSIVO COMPLETO');
  }

  checkElements() {
    console.log('🔍 Verificando elementos da aba Excel...');
    
    const elements = {
      'load-folder-btn': document.getElementById('load-folder-btn'),
      'excel-stats-grid': document.getElementById('excel-stats-grid'),
      'excel-chart-container': document.getElementById('excel-chart-container'),
      'excel-chart': document.getElementById('excel-chart'),
      'total-files': document.getElementById('total-files'),
      'total-employees': document.getElementById('total-employees'),
      'total-records': document.getElementById('total-records'),
      'total-points': document.getElementById('total-points'),
      'avg-points': document.getElementById('avg-points')
    };

    console.log('📊 Status dos elementos:');
    Object.entries(elements).forEach(([id, element]) => {
      const status = element ? '✅ Encontrado' : '❌ Não encontrado';
      console.log(`   ${id}: ${status}`);
    });

    // Verificar cards de estatísticas
    const statCards = document.querySelectorAll('.excel-stat-card');
    console.log(`📋 Cards de estatísticas: ${statCards.length} encontrados`);

    // Verificar se o ExcelDashboard está carregado
    if (window.ExcelDashboard) {
      console.log('✅ ExcelDashboard carregado');
      console.log('📊 Estado atual:', window.ExcelDashboard.state);
    } else {
      console.log('❌ ExcelDashboard não encontrado');
    }
  }

  checkData() {
    console.log('🔍 Verificando dados da aba Excel...');
    
    if (window.ExcelDashboard && window.ExcelDashboard.state.data) {
      const data = window.ExcelDashboard.state.data;
      console.log('📊 Dados carregados:', data);
      
      if (data.employees) {
        console.log(`👥 Funcionários: ${Object.keys(data.employees).length}`);
        Object.entries(data.employees).forEach(([name, empData]) => {
          // ✅ CORREÇÃO: Usar as chaves corretas do backend (com underscore)
          console.log(`   ${name}: ${empData.total_points || empData.totalPoints || 0} pontos, ${empData.total_records || empData.totalRecords || 0} registros`);
        });
      }
    } else {
      console.log('❌ Nenhum dado carregado');
    }
  }

  async testAPI() {
    console.log('🧪 Testando API da aba Excel...');
    
    try {
      // Testar endpoint de status
      const statusResponse = await fetch('/api/excel/status');
      const statusData = await statusResponse.json();
      console.log('📊 Status da API:', statusData);
      
      // Testar endpoint de carregar pasta
      const loadResponse = await fetch('/api/excel/load_folder', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          folder_path: 'registros monitorar'
        })
      });
      
      const loadData = await loadResponse.json();
      console.log('📊 Resposta do carregamento:', loadData);
      
    } catch (error) {
      console.error('❌ Erro ao testar API:', error);
    }
  }

  fixErrors() {
    console.log('🔧 Corrigindo erros comuns da aba Excel...');
    
    // Corrigir valores undefined nos cards
    const statElements = [
      'total-files',
      'total-employees', 
      'total-records',
      'total-points',
      'avg-points'
    ];
    
    statElements.forEach(id => {
      const element = document.getElementById(id);
      if (element && (element.textContent === 'undefined' || element.textContent === '')) {
        element.textContent = '0';
        console.log(`✅ Corrigido elemento ${id}`);
      }
    });
    
    // Corrigir detalhes dos cards
    const detailElements = [
      'files-detail',
      'employees-detail',
      'records-detail', 
      'points-detail',
      'avg-detail'
    ];
    
    detailElements.forEach(id => {
      const element = document.getElementById(id);
      if (element && (element.textContent === 'undefined' || element.textContent === '')) {
        element.textContent = 'Dados não disponíveis';
        console.log(`✅ Corrigido detalhe ${id}`);
      }
    });
    
    // Verificar se o ExcelDashboard está inicializado
    if (!window.ExcelDashboard) {
      console.log('⚠️ ExcelDashboard não encontrado, tentando inicializar...');
      // Tentar inicializar manualmente
      if (typeof window.ExcelDashboard !== 'undefined') {
        window.ExcelDashboard.init();
        console.log('✅ ExcelDashboard inicializado manualmente');
      }
    }
    
    console.log('✅ Correções aplicadas!');
  }

  // Método para diagnóstico detalhado
  diagnose() {
    console.log('🔍 === DIAGNÓSTICO DETALHADO ABA EXCEL ===');
    
    // 1. Verificar se estamos na aba Excel
    const excelTab = document.getElementById('excel-tab');
    const isExcelActive = excelTab && excelTab.classList.contains('active');
    console.log(`📍 Aba Excel ativa: ${isExcelActive ? '✅ Sim' : '❌ Não'}`);
    
    // 2. Verificar elementos críticos
    const criticalElements = {
      'excel-tab': document.getElementById('excel-tab'),
      'load-folder-btn': document.getElementById('load-folder-btn'),
      'excel-stats-grid': document.getElementById('excel-stats-grid'),
      'excel-chart-container': document.getElementById('excel-chart-container'),
      'excel-chart': document.getElementById('excel-chart')
    };
    
    console.log('📋 Elementos críticos:');
    Object.entries(criticalElements).forEach(([id, element]) => {
      const status = element ? '✅ Encontrado' : '❌ Não encontrado';
      console.log(`   ${id}: ${status}`);
    });
    
    // 3. Verificar ExcelDashboard
    if (window.ExcelDashboard) {
      console.log('✅ ExcelDashboard carregado');
      console.log('📊 Estado:', window.ExcelDashboard.state);
    } else {
      console.log('❌ ExcelDashboard NÃO encontrado');
    }
    
    // 4. Verificar Chart.js
    this.diagnoseChartJS();
    
    // 5. Verificar API
    this.diagnoseAPI();
    
    // 6. Verificar se os scripts estão carregados
    const scripts = [
      'excel_dashboard.js',
      'excel-debug.js',
      'excel-performance-test.js'
    ];
    
    console.log('📜 Scripts carregados:');
    scripts.forEach(script => {
      const found = Array.from(document.scripts).some(s => s.src.includes(script));
      console.log(`   ${script}: ${found ? '✅ Sim' : '❌ Não'}`);
    });
    
    // 7. Forçar inicialização se necessário
    if (!window.ExcelDashboard) {
      console.log('🔄 Tentando inicializar ExcelDashboard...');
      // Recarregar o script se necessário
      const script = document.createElement('script');
      script.src = '/static/js/excel_dashboard.js';
      script.onload = () => {
        console.log('✅ ExcelDashboard recarregado');
        if (window.ExcelDashboard) {
          window.ExcelDashboard.init();
        }
      };
      document.head.appendChild(script);
    }
    
    console.log('==========================================');
  }

  // Diagnóstico específico do Chart.js
  diagnoseChartJS() {
    console.log('📊 === DIAGNÓSTICO CHART.JS ===');
    
    // Verificar se Chart.js está carregado
    if (typeof Chart !== 'undefined') {
      console.log('✅ Chart.js carregado');
      console.log('📊 Versão:', Chart.version);
      console.log('📊 Configurações globais:', {
        animation: Chart.defaults?.animation,
        responsiveAnimationDuration: Chart.defaults?.responsiveAnimationDuration
      });
    } else {
      console.log('❌ Chart.js NÃO encontrado');
    }
    
    // Verificar plugins
    if (window.chartjsPluginAnnotation) {
      console.log('✅ Plugin de annotation encontrado');
    } else {
      console.log('❌ Plugin de annotation NÃO encontrado');
    }
    
    // Verificar se há múltiplas instâncias
    const chartScripts = Array.from(document.scripts).filter(s => 
      s.src && s.src.includes('chart.js')
    );
    console.log(`📊 Scripts Chart.js encontrados: ${chartScripts.length}`);
    chartScripts.forEach((script, index) => {
      console.log(`   ${index + 1}: ${script.src}`);
    });
    
    // Verificar canvas
    const canvas = document.getElementById('excel-chart');
    if (canvas) {
      console.log('✅ Canvas encontrado');
      console.log('📊 Dimensões:', canvas.width, 'x', canvas.height);
      console.log('📊 Contexto:', canvas.getContext('2d') ? '✅ Disponível' : '❌ Indisponível');
    } else {
      console.log('❌ Canvas não encontrado');
    }
    
    console.log('================================');
  }

  // Método para teste rápido completo
  async quickTest() {
    console.log('🚀 Iniciando teste rápido da aba Excel...');
    
    // 1. Verificar elementos
    console.log('\n1️⃣ Verificando elementos...');
    this.checkElements();
    
    // 2. Corrigir erros
    console.log('\n2️⃣ Corrigindo erros...');
    this.fixErrors();
    
    // 3. Testar Chart.js
    console.log('\n3️⃣ Testando Chart.js...');
    this.testChartJS();
    
    // 4. Testar API
    console.log('\n4️⃣ Testando API...');
    await this.testAPIData();
    
    // 5. Verificar dados
    console.log('\n5️⃣ Verificando dados...');
    setTimeout(() => {
      this.checkData();
      console.log('\n✅ Teste rápido concluído!');
    }, 1000);
  }

  // Teste específico do Chart.js
  testChartJS() {
    console.log('🧪 Testando Chart.js...');
    
    // 1. Verificar se Chart.js está disponível
    if (typeof Chart === 'undefined') {
      console.log('❌ Chart.js não está disponível');
      return;
    }
    
    // 2. Testar criação de um gráfico simples
    try {
      const testCanvas = document.createElement('canvas');
      testCanvas.width = 100;
      testCanvas.height = 100;
      document.body.appendChild(testCanvas);
      
      const testChart = new Chart(testCanvas, {
        type: 'line',
        data: {
          labels: ['Teste'],
          datasets: [{
            label: 'Teste',
            data: [1],
            borderColor: '#3b82f6'
          }]
        },
        options: {
          animation: { duration: 0 },
          responsive: false,
          maintainAspectRatio: false
        }
      });
      
      // Verificar se o gráfico foi criado sem erros
      if (testChart && testChart.data) {
        console.log('✅ Chart.js funcionando corretamente');
        testChart.destroy();
        document.body.removeChild(testCanvas);
      } else {
        console.log('❌ Chart.js não criou gráfico corretamente');
      }
      
    } catch (error) {
      console.error('❌ Erro ao testar Chart.js:', error);
      console.error('❌ Stack trace:', error.stack);
    }
  }

  // Diagnóstico específico dos dados da API
  async diagnoseAPI() {
    console.log('🔍 === DIAGNÓSTICO MASSIVO DA API ===');
    
    try {
      // 1. Testar endpoint de registros com DEBUG MASSIVO
      console.log('📊 Testando endpoint /api/entries...');
      const entriesResponse = await fetch('/api/entries');
      console.log('📊 Status da resposta:', entriesResponse.status);
      console.log('📊 Headers da resposta:', entriesResponse.headers);
      
      const entriesData = await entriesResponse.json();
      console.log('📊 Dados brutos da API:', entriesData);
      
      if (entriesData.entries && entriesData.entries.length > 0) {
        console.log(`📊 Total de registros: ${entriesData.entries.length}`);
        
        // DEBUG MASSIVO: Verificar cada registro individualmente
        entriesData.entries.forEach((entry, index) => {
          console.log(`\n🔍 REGISTRO ${index + 1}:`);
          console.log('   ID:', entry.id);
          console.log('   Employee Name:', entry.employee_name);
          console.log('   Employee Name Type:', typeof entry.employee_name);
          console.log('   Employee Name === undefined:', entry.employee_name === undefined);
          console.log('   Employee Name === null:', entry.employee_name === null);
          console.log('   Employee Name === "":', entry.employee_name === "");
          console.log('   Date:', entry.date);
          console.log('   Refinery:', entry.refinery);
          console.log('   Points:', entry.points);
          console.log('   Observations:', entry.observations);
          
          // Verificar se é undefined
          if (entry.employee_name === undefined) {
            console.log('❌ PROBLEMA: employee_name é undefined!');
          } else if (entry.employee_name === null) {
            console.log('❌ PROBLEMA: employee_name é null!');
          } else if (entry.employee_name === "") {
            console.log('❌ PROBLEMA: employee_name é string vazia!');
          } else {
            console.log('✅ employee_name parece válido');
          }
        });
        
        // Verificar se employee_name está undefined
        const undefinedEmployees = entriesData.entries.filter(entry => 
          entry.employee_name === undefined || entry.employee_name === null
        );
        
        console.log(`\n📊 RESUMO: Registros com employee undefined: ${undefinedEmployees.length}/${entriesData.entries.length}`);
        
        if (undefinedEmployees.length > 0) {
          console.log('❌ PROBLEMA ENCONTRADO: employee_name está undefined');
          console.log('📊 Exemplo de registro problemático:', undefinedEmployees[0]);
        } else {
          console.log('✅ Todos os registros têm employee_name válido');
        }
      } else {
        console.log('⚠️ Nenhum registro encontrado na API');
      }
      
      // 2. Testar endpoint de funcionários com DEBUG MASSIVO
      console.log('\n👥 Testando endpoint /api/employees...');
      const employeesResponse = await fetch('/api/employees');
      console.log('👥 Status da resposta employees:', employeesResponse.status);
      
      const employeesData = await employeesResponse.json();
      console.log('👥 Dados brutos dos funcionários:', employeesData);
      
      // 3. Verificar se há funcionários válidos
      if (employeesData.employees && employeesData.employees.length > 0) {
        console.log('✅ Funcionários encontrados:', employeesData.employees.length);
        employeesData.employees.forEach((emp, index) => {
          console.log(`\n👤 FUNCIONÁRIO ${index + 1}:`);
          console.log('   ID:', emp.id);
          console.log('   Name:', emp.name);
          console.log('   Real Name:', emp.real_name);
          console.log('   Username:', emp.username);
          console.log('   Role:', emp.role);
          console.log('   Weekly Points:', emp.weekly_points);
          console.log('   Weekly Goal:', emp.weekly_goal);
        });
      } else {
        console.log('❌ Nenhum funcionário encontrado');
      }
      
      // 4. DEBUG MASSIVO: Testar relação Entry-Employee
      console.log('\n🔍 TESTANDO RELAÇÃO ENTRY-EMPLOYEE...');
      await this.testEntryEmployeeRelation();
      
    } catch (error) {
      console.error('❌ Erro ao diagnosticar API:', error);
      console.error('❌ Stack trace:', error.stack);
    }
    
    console.log('================================');
  }

  // Teste específico da relação Entry-Employee
  async testEntryEmployeeRelation() {
    console.log('🧪 Testando relação Entry-Employee...');
    
    try {
      // Testar diferentes queries
      const queries = [
        '/api/entries?per_page=1',
        '/api/entries?per_page=5',
        '/api/entries?per_page=10'
      ];
      
      for (const query of queries) {
        console.log(`\n📊 Testando query: ${query}`);
        
        const response = await fetch(query);
        const data = await response.json();
        
        if (data.entries && data.entries.length > 0) {
          console.log(`📊 Query ${query} retornou ${data.entries.length} registros`);
          
          data.entries.forEach((entry, index) => {
            console.log(`   Registro ${index + 1}:`);
            console.log(`     ID: ${entry.id}`);
            console.log(`     Employee Name: "${entry.employee_name}"`);
            console.log(`     Employee Name Type: ${typeof entry.employee_name}`);
            console.log(`     Employee Name Length: ${entry.employee_name ? entry.employee_name.length : 'N/A'}`);
          });
        } else {
          console.log(`⚠️ Query ${query} não retornou registros`);
        }
      }
      
    } catch (error) {
      console.error('❌ Erro ao testar relação Entry-Employee:', error);
    }
  }

  // Teste específico para verificar dados da API
  async testAPIData() {
    console.log('🧪 Testando dados da API...');
    
    try {
      // Testar diferentes endpoints
      const endpoints = [
        '/api/entries',
        '/api/employees',
        '/api/weekly_data',
        '/api/monthly_data',
        '/api/daily_data'
      ];
      
      for (const endpoint of endpoints) {
        console.log(`\n📊 Testando ${endpoint}...`);
        
        try {
          const response = await fetch(endpoint);
          const data = await response.json();
          
          if (response.ok) {
            console.log(`✅ ${endpoint} - OK`);
            console.log(`📊 Dados:`, data);
          } else {
            console.log(`❌ ${endpoint} - Erro: ${response.status}`);
          }
        } catch (error) {
          console.log(`❌ ${endpoint} - Erro: ${error.message}`);
        }
      }
      
    } catch (error) {
      console.error('❌ Erro ao testar API:', error);
    }
  }

  // DEBUG MASSIVO COMPLETO
  async debugMassivo() {
    console.log('🚀 === DEBUG MASSIVO COMPLETO ===');
    console.log('🔍 Iniciando análise completa do sistema...');
    
    // 1. Verificar elementos
    console.log('\n1️⃣ Verificando elementos...');
    this.checkElements();
    
    // 2. Verificar Chart.js
    console.log('\n2️⃣ Verificando Chart.js...');
    this.diagnoseChartJS();
    
    // 3. DEBUG MASSIVO DA API
    console.log('\n3️⃣ DEBUG MASSIVO DA API...');
    await this.diagnoseAPI();
    
    // 4. Teste completo da API
    console.log('\n4️⃣ Teste completo da API...');
    await this.testAPIData();
    
    // 5. Verificar dados
    console.log('\n5️⃣ Verificando dados...');
    this.checkData();
    
    // 6. Corrigir erros
    console.log('\n6️⃣ Corrigindo erros...');
    this.fixErrors();
    
    console.log('\n✅ DEBUG MASSIVO COMPLETO FINALIZADO!');
    console.log('📊 Verifique os logs acima para identificar problemas');
  }
}

// Inicializar debug
window.excelDebug = new ExcelDebug();

// ===== FIM DO DEBUG PARA ABA EXCEL ===== 