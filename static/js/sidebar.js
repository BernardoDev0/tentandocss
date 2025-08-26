// Sincroniza abas e controla a sidebar (mobile + desktop)
(function () {
  const sidebar = document.getElementById('app-sidebar');
  const mobileBtn = document.getElementById('mobile-menu-toggle');
  const collapseBtn = document.getElementById('sidebar-toggle');

  function setActiveTab(tabId) {
    // Conteúdos
    document.querySelectorAll('.tab-content').forEach(el => {
      el.classList.toggle('active', el.id === tabId);
    });
    // Botões do topo
    document.querySelectorAll('.tab-button').forEach(btn => {
      const id = btn.getAttribute('data-tab');
      btn.classList.toggle('active', id === tabId);
    });
    // Links da sidebar
    document.querySelectorAll('.nav-link[data-tab-target]').forEach(link => {
      const id = link.getAttribute('data-tab-target');
      link.classList.toggle('active', id === tabId);
    });
  }

  // Sidebar links -> trocam a aba
  document.querySelectorAll('.nav-link[data-tab-target]').forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      const target = link.getAttribute('data-tab-target');
      setActiveTab(target);
      // Em mobile, fechar ao navegar
      if (window.matchMedia('(max-width: 768px)').matches && sidebar) {
        sidebar.classList.remove('open');
      }
    });
  });

  // Botões de aba do topo -> mantêm a sidebar sincronizada
  document.querySelectorAll('.tab-button[data-tab]').forEach(btn => {
    btn.addEventListener('click', () => {
      const id = btn.getAttribute('data-tab');
      setActiveTab(id);
    });
  });

  // Mobile: abrir/fechar via hambúrguer
  if (mobileBtn && sidebar) {
    mobileBtn.addEventListener('click', () => {
      sidebar.classList.toggle('open');
    });
  }

  // Desktop: colapsar/expandir largura
  if (collapseBtn && sidebar) {
    collapseBtn.addEventListener('click', () => {
      sidebar.classList.toggle('collapsed');
    });
  }
})();