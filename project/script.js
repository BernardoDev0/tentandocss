// Modern Dashboard JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Lucide icons
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }

    // Sidebar functionality
    initSidebar();
    
    // Tab navigation
    initTabNavigation();
    
    // Progress animations
    initProgressAnimations();
    
    // Form interactions
    initFormInteractions();
    
    // Table interactions
    initTableInteractions();
    
    // Mobile responsiveness
    initMobileFeatures();
    
    // Initialize tooltips and other UI enhancements
    initUIEnhancements();
});

// Sidebar Management
function initSidebar() {
    const sidebar = document.getElementById('sidebar');
    const sidebarToggle = document.getElementById('sidebarToggle');
    const mobileMenuToggle = document.getElementById('mobileMenuToggle');
    const navLinks = document.querySelectorAll('.nav-link');

    // Desktop sidebar toggle
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('collapsed');
            
            // Save state to localStorage
            localStorage.setItem('sidebarCollapsed', sidebar.classList.contains('collapsed'));
        });
    }

    // Mobile sidebar toggle
    if (mobileMenuToggle) {
        mobileMenuToggle.addEventListener('click', function() {
            sidebar.classList.toggle('open');
        });
    }

    // Restore sidebar state
    const isCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';
    if (isCollapsed && window.innerWidth > 768) {
        sidebar.classList.add('collapsed');
    }

    // Navigation link clicks
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Remove active class from all links
            navLinks.forEach(l => l.classList.remove('active'));
            
            // Add active class to clicked link
            this.classList.add('active');
            
            // Get target tab
            const targetTab = this.getAttribute('data-tab');
            
            // Switch tabs
            switchTab(targetTab);
            
            // Update breadcrumb
            updateBreadcrumb(this.querySelector('.nav-text').textContent);
            
            // Close mobile sidebar
            if (window.innerWidth <= 768) {
                sidebar.classList.remove('open');
            }
        });
    });

    // Close sidebar on outside click (mobile)
    document.addEventListener('click', function(e) {
        if (window.innerWidth <= 768) {
            if (!sidebar.contains(e.target) && !mobileMenuToggle.contains(e.target)) {
                sidebar.classList.remove('open');
            }
        }
    });
}

// Tab Navigation
function initTabNavigation() {
    // Set initial active tab
    switchTab('dashboard');
}

function switchTab(tabName) {
    // Hide all tab contents
    const tabContents = document.querySelectorAll('.tab-content');
    tabContents.forEach(content => {
        content.classList.remove('active');
    });
    
    // Show target tab
    const targetTab = document.getElementById(tabName);
    if (targetTab) {
        targetTab.classList.add('active');
        
        // Trigger any tab-specific initialization
        initTabSpecificFeatures(tabName);
    }
}

function initTabSpecificFeatures(tabName) {
    switch(tabName) {
        case 'dashboard':
            animateStatCards();
            break;
        case 'graficos':
            initCharts();
            break;
        case 'registros':
            initTableFeatures();
            break;
        case 'excel':
            initExportFeatures();
            break;
    }
}

// Progress Animations
function initProgressAnimations() {
    const progressFills = document.querySelectorAll('.progress-fill');
    const miniProgressFills = document.querySelectorAll('.mini-progress-fill');
    
    // Animate main progress bars
    progressFills.forEach(fill => {
        const progress = fill.getAttribute('data-progress') || 100;
        setTimeout(() => {
            fill.style.width = Math.min(progress, 100) + '%';
        }, 500);
    });
    
    // Animate mini progress bars
    miniProgressFills.forEach(fill => {
        const currentWidth = fill.style.width;
        fill.style.width = '0%';
        setTimeout(() => {
            fill.style.width = currentWidth;
        }, 1000);
    });
}

// Animate stat cards on dashboard load
function animateStatCards() {
    const statCards = document.querySelectorAll('.stat-card');
    statCards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            card.style.transition = 'all 0.5s ease-out';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });
}

// Form Interactions
function initFormInteractions() {
    const selects = document.querySelectorAll('.form-select');
    const inputs = document.querySelectorAll('.form-input');
    
    // Week selector change
    const weekSelect = document.getElementById('week-select');
    if (weekSelect) {
        weekSelect.addEventListener('change', function() {
            updateEmployeeData(this.value);
        });
    }
    
    // Filter functionality
    const semanaFilter = document.getElementById('semana-filter');
    const funcionarioFilter = document.getElementById('funcionario-filter');
    const searchInput = document.getElementById('search-input');
    
    if (semanaFilter) {
        semanaFilter.addEventListener('change', applyFilters);
    }
    
    if (funcionarioFilter) {
        funcionarioFilter.addEventListener('change', applyFilters);
    }
    
    if (searchInput) {
        searchInput.addEventListener('input', debounce(applyFilters, 300));
    }
}

// Table Interactions
function initTableInteractions() {
    const actionBtns = document.querySelectorAll('.action-btn');
    
    actionBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.stopPropagation();
            
            if (this.classList.contains('edit')) {
                editRecord(this.closest('tr'));
            } else if (this.classList.contains('delete')) {
                deleteRecord(this.closest('tr'));
            }
        });
    });
}

// Mobile Features
function initMobileFeatures() {
    // Handle window resize
    window.addEventListener('resize', function() {
        const sidebar = document.getElementById('sidebar');
        
        if (window.innerWidth > 768) {
            sidebar.classList.remove('open');
        }
    });
    
    // Touch gestures for mobile
    let touchStartX = 0;
    let touchEndX = 0;
    
    document.addEventListener('touchstart', function(e) {
        touchStartX = e.changedTouches[0].screenX;
    });
    
    document.addEventListener('touchend', function(e) {
        touchEndX = e.changedTouches[0].screenX;
        handleSwipe();
    });
    
    function handleSwipe() {
        const sidebar = document.getElementById('sidebar');
        const swipeThreshold = 100;
        
        if (window.innerWidth <= 768) {
            if (touchEndX < touchStartX - swipeThreshold) {
                // Swipe left - close sidebar
                sidebar.classList.remove('open');
            }
            
            if (touchEndX > touchStartX + swipeThreshold && touchStartX < 50) {
                // Swipe right from edge - open sidebar
                sidebar.classList.add('open');
            }
        }
    }
}

// UI Enhancements
function initUIEnhancements() {
    // Add loading states to buttons
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(btn => {
        btn.addEventListener('click', function() {
            if (!this.classList.contains('loading')) {
                this.classList.add('loading');
                
                // Remove loading state after 2 seconds (simulate API call)
                setTimeout(() => {
                    this.classList.remove('loading');
                }, 2000);
            }
        });
    });
    
    // Smooth scroll for internal links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// Chart Initialization (placeholder)
function initCharts() {
    const chartCards = document.querySelectorAll('.chart-card');
    
    chartCards.forEach(card => {
        const placeholder = card.querySelector('.chart-placeholder');
        if (placeholder) {
            // Simulate chart loading
            setTimeout(() => {
                placeholder.innerHTML = `
                    <div style="text-align: center; color: var(--text-muted);">
                        <i data-lucide="bar-chart" style="font-size: 48px; margin-bottom: 16px; opacity: 0.5;"></i>
                        <p>Gráfico carregado com sucesso!</p>
                        <p style="font-size: 12px;">Integração com biblioteca de gráficos necessária</p>
                    </div>
                `;
                
                // Re-initialize icons
                if (typeof lucide !== 'undefined') {
                    lucide.createIcons();
                }
            }, 2000);
        }
    });
}

// Table Features
function initTableFeatures() {
    // Add row hover effects
    const tableRows = document.querySelectorAll('.data-table tbody tr');
    tableRows.forEach(row => {
        row.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.01)';
        });
        
        row.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
        });
    });
}

// Export Features
function initExportFeatures() {
    const exportBtns = document.querySelectorAll('.export-card .btn');
    
    exportBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const cardTitle = this.closest('.export-card').querySelector('h3').textContent;
            showNotification(`Gerando ${cardTitle}...`, 'info');
            
            // Simulate export process
            setTimeout(() => {
                showNotification(`${cardTitle} gerado com sucesso!`, 'success');
            }, 2000);
        });
    });
}

// Utility Functions
function updateBreadcrumb(text) {
    const breadcrumbItem = document.querySelector('.breadcrumb-item');
    if (breadcrumbItem) {
        breadcrumbItem.textContent = text;
    }
}

function updateEmployeeData(week) {
    console.log(`Updating employee data for week ${week}`);
    // This would typically make an API call to update employee data
    showNotification(`Dados atualizados para Semana ${week}`, 'info');
}

function applyFilters() {
    const semana = document.getElementById('semana-filter')?.value || '';
    const funcionario = document.getElementById('funcionario-filter')?.value || '';
    const search = document.getElementById('search-input')?.value || '';
    
    console.log('Applying filters:', { semana, funcionario, search });
    
    // Filter table rows
    const tableRows = document.querySelectorAll('.data-table tbody tr');
    tableRows.forEach(row => {
        let show = true;
        
        // Apply filters logic here
        if (funcionario && !row.textContent.toLowerCase().includes(funcionario.toLowerCase())) {
            show = false;
        }
        
        if (search && !row.textContent.toLowerCase().includes(search.toLowerCase())) {
            show = false;
        }
        
        row.style.display = show ? '' : 'none';
    });
}

function editRecord(row) {
    showNotification('Funcionalidade de edição será implementada', 'info');
    console.log('Editing record:', row);
}

function deleteRecord(row) {
    if (confirm('Tem certeza que deseja excluir este registro?')) {
        row.style.transition = 'all 0.3s ease-out';
        row.style.opacity = '0';
        row.style.transform = 'translateX(-100%)';
        
        setTimeout(() => {
            row.remove();
            showNotification('Registro excluído com sucesso', 'success');
        }, 300);
    }
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i data-lucide="${getNotificationIcon(type)}"></i>
            <span>${message}</span>
        </div>
    `;
    
    // Add styles
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: var(--radius-lg);
        padding: var(--spacing-md) var(--spacing-lg);
        box-shadow: var(--shadow-xl);
        z-index: 9999;
        transform: translateX(100%);
        transition: transform 0.3s ease-out;
    `;
    
    // Add to DOM
    document.body.appendChild(notification);
    
    // Initialize icons
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
    
    // Animate in
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 3000);
}

function getNotificationIcon(type) {
    switch(type) {
        case 'success': return 'check-circle';
        case 'warning': return 'alert-triangle';
        case 'error': return 'x-circle';
        default: return 'info';
    }
}

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

// API Integration Functions (for Python backend)
async function fetchDashboardData() {
    try {
        // This would connect to your Python backend
        const response = await fetch('/api/dashboard');
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching dashboard data:', error);
        showNotification('Erro ao carregar dados', 'error');
    }
}

async function exportToExcel(reportType) {
    try {
        const response = await fetch(`/api/export/${reportType}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `relatorio_${reportType}_${new Date().toISOString().split('T')[0]}.xlsx`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        }
    } catch (error) {
        console.error('Error exporting to Excel:', error);
        showNotification('Erro ao exportar relatório', 'error');
    }
}

// Performance monitoring
function initPerformanceMonitoring() {
    // Monitor page load time
    window.addEventListener('load', function() {
        const loadTime = performance.now();
        console.log(`Page loaded in ${loadTime.toFixed(2)}ms`);
    });
    
    // Monitor memory usage (if available)
    if ('memory' in performance) {
        setInterval(() => {
            const memory = performance.memory;
            console.log(`Memory usage: ${(memory.usedJSHeapSize / 1048576).toFixed(2)} MB`);
        }, 30000); // Log every 30 seconds
    }
}