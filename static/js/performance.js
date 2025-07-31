/* ===================================================================
   PERFORMANCE.JS - Helpers de Performance e Otimizações
   ================================================================= */

// FPS Meter
class FPSMeter {
    constructor() {
        this.frames = [];
        this.lastFrameTime = performance.now();
        this.fps = 0;
    }
    
    tick() {
        const now = performance.now();
        const delta = now - this.lastFrameTime;
        this.lastFrameTime = now;
        
        if (delta > 0) {
            this.frames.push(1000 / delta);
            if (this.frames.length > 60) {
                this.frames.shift();
            }
            this.fps = Math.round(this.frames.reduce((a, b) => a + b, 0) / this.frames.length);
        }
        
        return this.fps;
    }
}

// Throttle Helper
function throttle(fn, delay) {
    let lastCall = 0;
    return (...args) => {
        const now = Date.now();
        if (now - lastCall < delay) return;
        lastCall = now;
        return fn(...args);
    };
}

// Debounce Helper
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

// Performance Monitor
class PerformanceMonitor {
    constructor() {
        this.fpsMeter = new FPSMeter();
        this.layoutThrashingCount = 0;
        this.performanceData = [];
        this.issues = [];
        this.optimizations = [];
        
        this.init();
    }
    
    init() {
        this.detectIssues();
        this.detectOptimizations();
        this.startMonitoring();
        this.setupEventListeners();
    }
    
    detectIssues() {
        // Detectar problemas de CSS
        const styleSheets = Array.from(document.styleSheets);
        let transitionAllCount = 0;
        let boxShadowCount = 0;
        let universalSelectorCount = 0;
        
        styleSheets.forEach(sheet => {
            try {
                const rules = Array.from(sheet.cssRules || []);
                rules.forEach(rule => {
                    if (rule.cssText.includes('transition: all')) {
                        transitionAllCount++;
                    }
                    if (rule.cssText.includes('box-shadow') && rule.cssText.includes('rgba')) {
                        boxShadowCount++;
                    }
                    if (rule.selectorText === '*') {
                        universalSelectorCount++;
                    }
                });
            } catch (e) {
                // Cross-origin stylesheets
            }
        });
        
        if (transitionAllCount > 0) {
            this.issues.push({
                type: 'CSS',
                severity: 'warning',
                title: 'Transições "all" detectadas',
                description: `${transitionAllCount} regras CSS usando "transition: all" podem causar reflows desnecessários.`
            });
        }
        
        if (boxShadowCount > 10) {
            this.issues.push({
                type: 'CSS',
                severity: 'warning',
                title: 'Box-shadows pesados',
                description: `${boxShadowCount} elementos com box-shadow complexos podem impactar performance.`
            });
        }
        
        if (universalSelectorCount > 0) {
            this.issues.push({
                type: 'CSS',
                severity: 'bad',
                title: 'Seletor universal com animações',
                description: `${universalSelectorCount} seletores "*" podem causar layout thrashing.`
            });
        }
    }
    
    detectOptimizations() {
        // Verificar otimizações implementadas
        const optimizations = [
            {
                title: 'CSS Critical Inline',
                description: 'CSS crítico inline para LCP otimizado',
                implemented: document.querySelector('style') !== null
            },
            {
                title: 'Font Display Swap',
                description: 'Fonts com font-display: swap',
                implemented: document.querySelector('@font-face') !== null
            },
            {
                title: 'Preconnect CDNs',
                description: 'Preconnect para CDNs críticos',
                implemented: document.querySelector('link[rel="preconnect"]') !== null
            },
            {
                title: 'Lazy Loading CSS',
                description: 'CSS não-crítico carregado assincronamente',
                implemented: document.querySelector('link[rel="preload"][as="style"]') !== null
            }
        ];
        
        this.optimizations = optimizations;
    }
    
    startMonitoring() {
        const updateMetrics = () => {
            const fps = this.fpsMeter.tick();
            const memory = performance.memory ? Math.round(performance.memory.usedJSHeapSize / 1024 / 1024) : 'N/A';
            
            // Adicionar dados ao histórico
            this.performanceData.push({
                timestamp: Date.now(),
                fps: fps,
                memory: memory,
                layoutThrashing: this.layoutThrashingCount
            });
            
            if (this.performanceData.length > 100) {
                this.performanceData.shift();
            }
        };
        
        setInterval(updateMetrics, 1000);
        requestAnimationFrame(() => updateMetrics());
    }
    
    setupEventListeners() {
        // Detectar layout thrashing
        const observer = new PerformanceObserver((list) => {
            list.getEntries().forEach((entry) => {
                if (entry.entryType === 'layout-shift') {
                    this.layoutThrashingCount++;
                }
            });
        });
        
        try {
            observer.observe({ entryTypes: ['layout-shift'] });
        } catch (e) {
            console.log('PerformanceObserver não suportado');
        }
    }
}

// Chart.js Optimizations
class OptimizedChart {
    constructor(canvasId, data, options = {}) {
        this.canvas = document.getElementById(canvasId);
        this.data = data;
        this.options = this.getOptimizedOptions(options);
        this.chart = null;
        
        this.init();
    }
    
    getOptimizedOptions(customOptions = {}) {
        return {
            // OTIMIZAÇÃO: Desabilitar animações
            animation: {
                duration: 0
            },
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    // OTIMIZAÇÃO: Tooltips simples
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    borderColor: '#3b82f6',
                    borderWidth: 1,
                    cornerRadius: 8,
                    displayColors: false
                }
            },
            elements: {
                point: {
                    radius: 0 // OTIMIZAÇÃO: Remover pontos
                },
                line: {
                    borderWidth: 2
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: '#94a3b8',
                        font: {
                            size: 12
                        }
                    }
                },
                y: {
                    grid: {
                        color: 'rgba(148, 163, 184, 0.1)'
                    },
                    ticks: {
                        color: '#94a3b8',
                        font: {
                            size: 12
                        }
                    }
                }
            },
            ...customOptions
        };
    }
    
    init() {
        if (!this.canvas) {
            console.error(`Canvas ${this.canvasId} não encontrado`);
            return;
        }
        
        // OTIMIZAÇÃO: GPU acceleration para canvas
        this.canvas.style.transform = 'translateZ(0)';
        this.canvas.style.willChange = 'transform';
        
        this.chart = new Chart(this.canvas, {
            type: 'line',
            data: this.data,
            options: this.options
        });
    }
    
    update(newData) {
        if (this.chart) {
            this.chart.data = newData;
            this.chart.update('none'); // OTIMIZAÇÃO: Sem animação
        }
    }
    
    destroy() {
        if (this.chart) {
            this.chart.destroy();
            this.chart = null;
        }
    }
}

// Event Listener Optimizations
class OptimizedEventListeners {
    constructor() {
        this.listeners = new Map();
    }
    
    addThrottledListener(element, event, handler, delay = 16) {
        const throttledHandler = throttle(handler, delay);
        element.addEventListener(event, throttledHandler, { passive: true });
        
        this.listeners.set(`${element.id}-${event}`, {
            element,
            event,
            handler: throttledHandler
        });
    }
    
    addDebouncedListener(element, event, handler, delay = 300) {
        const debouncedHandler = debounce(handler, delay);
        element.addEventListener(event, debouncedHandler, { passive: true });
        
        this.listeners.set(`${element.id}-${event}`, {
            element,
            event,
            handler: debouncedHandler
        });
    }
    
    removeListener(elementId, event) {
        const key = `${elementId}-${event}`;
        const listener = this.listeners.get(key);
        
        if (listener) {
            listener.element.removeEventListener(listener.event, listener.handler);
            this.listeners.delete(key);
        }
    }
    
    removeAllListeners() {
        this.listeners.forEach((listener, key) => {
            listener.element.removeEventListener(listener.event, listener.handler);
        });
        this.listeners.clear();
    }
}

// DOM Optimizations
class DOMOptimizer {
    static batchDOMUpdates(updates) {
        // OTIMIZAÇÃO: Batch DOM updates
        requestAnimationFrame(() => {
            updates.forEach(update => update());
        });
    }
    
    static createElement(tag, attributes = {}, children = []) {
        const element = document.createElement(tag);
        
        // OTIMIZAÇÃO: Set attributes in batch
        Object.entries(attributes).forEach(([key, value]) => {
            if (key === 'className') {
                element.className = value;
            } else if (key === 'style' && typeof value === 'object') {
                Object.assign(element.style, value);
            } else {
                element.setAttribute(key, value);
            }
        });
        
        // OTIMIZAÇÃO: Append children in batch
        if (children.length > 0) {
            const fragment = document.createDocumentFragment();
            children.forEach(child => {
                if (typeof child === 'string') {
                    fragment.appendChild(document.createTextNode(child));
                } else {
                    fragment.appendChild(child);
                }
            });
            element.appendChild(fragment);
        }
        
        return element;
    }
    
    static optimizeScroll(element, handler) {
        // OTIMIZAÇÃO: Passive scroll listener
        element.addEventListener('scroll', throttle(handler, 16), { passive: true });
    }
    
    static optimizeResize(element, handler) {
        // OTIMIZAÇÃO: Debounced resize listener
        element.addEventListener('resize', debounce(handler, 250), { passive: true });
    }
}

// Memory Management
class MemoryManager {
    constructor() {
        this.cache = new Map();
        this.maxCacheSize = 100;
    }
    
    set(key, value, ttl = 300000) { // 5 minutes default
        this.cache.set(key, {
            value,
            timestamp: Date.now(),
            ttl
        });
        
        // OTIMIZAÇÃO: Auto-cleanup
        if (this.cache.size > this.maxCacheSize) {
            this.cleanup();
        }
    }
    
    get(key) {
        const item = this.cache.get(key);
        if (!item) return null;
        
        if (Date.now() - item.timestamp > item.ttl) {
            this.cache.delete(key);
            return null;
        }
        
        return item.value;
    }
    
    cleanup() {
        const now = Date.now();
        for (const [key, item] of this.cache.entries()) {
            if (now - item.timestamp > item.ttl) {
                this.cache.delete(key);
            }
        }
    }
    
    clear() {
        this.cache.clear();
    }
}

// Performance Utilities
const PerformanceUtils = {
    // Measure execution time
    measureTime(fn, label = 'Function') {
        const start = performance.now();
        const result = fn();
        const end = performance.now();
        console.log(`${label} took ${(end - start).toFixed(2)}ms`);
        return result;
    },
    
    // Async version
    async measureTimeAsync(fn, label = 'Async Function') {
        const start = performance.now();
        const result = await fn();
        const end = performance.now();
        console.log(`${label} took ${(end - start).toFixed(2)}ms`);
        return result;
    },
    
    // Check if element is in viewport
    isInViewport(element) {
        const rect = element.getBoundingClientRect();
        return (
            rect.top >= 0 &&
            rect.left >= 0 &&
            rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
            rect.right <= (window.innerWidth || document.documentElement.clientWidth)
        );
    },
    
    // Lazy load images
    lazyLoadImages() {
        const images = document.querySelectorAll('img[data-src]');
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.removeAttribute('data-src');
                    observer.unobserve(img);
                }
            });
        });
        
        images.forEach(img => imageObserver.observe(img));
    },
    
    // Preload critical resources
    preloadResource(href, as = 'style') {
        const link = document.createElement('link');
        link.rel = 'preload';
        link.href = href;
        link.as = as;
        document.head.appendChild(link);
    }
};

// Initialize performance optimizations
document.addEventListener('DOMContentLoaded', () => {
    // Initialize performance monitor
    window.performanceMonitor = new PerformanceMonitor();
    
    // Initialize event listeners optimizer
    window.eventOptimizer = new OptimizedEventListeners();
    
    // Initialize memory manager
    window.memoryManager = new MemoryManager();
    
    // Lazy load images
    PerformanceUtils.lazyLoadImages();
    
    console.log('🚀 Performance optimizations initialized');
});

// Export for use in other modules
window.PerformanceUtils = PerformanceUtils;
window.OptimizedChart = OptimizedChart;
window.DOMOptimizer = DOMOptimizer;
window.throttle = throttle;
window.debounce = debounce; 