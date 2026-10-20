// ============================================
// MAZI Fraud AI — Live Dashboard Engine
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    initLiveStats();
    initCounters();
    initClock();
    initActivityTicker();
    initToasts();
    initMobileSidebar();
    initShimmerEffects();
});

// 1. LIVE STATS POLLING — Updates every 5 seconds
function initLiveStats() {
    const statElements = {
        'transaction-count': document.querySelector('[data-stat="transaction_count"]'),
        'active-alerts': document.querySelector('[data-stat="active_alerts"]'),
        'fraud-count': document.querySelector('[data-stat="fraud_count"]'),
        'avg-risk': document.querySelector('[data-stat="avg_risk_score"]')
    };

    // Check if we're on the dashboard
    if (!document.getElementById('riskGauge')) return;

    async function fetchStats() {
        try {
            const res = await fetch('/dashboard/api/stats');
            if (!res.ok) return;
            const data = await res.json();
            
            Object.keys(data).forEach(key => {
                const el = document.querySelector(`[data-stat="${key}"]`);
                if (el && el.textContent != data[key]) {
                    animateNumberChange(el, parseFloat(el.textContent) || 0, data[key]);
                }
            });
        } catch (e) {
            console.log('Live stats unavailable');
        }
    }

    // Poll every 5 seconds
    setInterval(fetchStats, 5000);
    fetchStats(); // Initial fetch
}

// 2. ANIMATED COUNTERS — Numbers count up on page load
function initCounters() {
    document.querySelectorAll('[data-counter]').forEach(el => {
        const target = parseFloat(el.getAttribute('data-counter')) || 0;
        const duration = 1500;
        const start = performance.now();
        
        function update(now) {
            const elapsed = now - start;
            const progress = Math.min(elapsed / duration, 1);
            const eased = 1 - Math.pow(1 - progress, 3); // ease-out cubic
            const current = target * eased;
            
            if (el.textContent.includes('%')) {
                el.textContent = current.toFixed(1) + '%';
            } else if (el.textContent.includes('R')) {
                el.textContent = 'R ' + current.toFixed(2);
            } else {
                el.textContent = Math.floor(current).toLocaleString();
            }
            
            if (progress < 1) requestAnimationFrame(update);
        }
        
        requestAnimationFrame(update);
    });
}

// 3. REAL-TIME CLOCK
function initClock() {
    const clockEl = document.getElementById('live-clock');
    if (!clockEl) return;
    
    function tick() {
        const now = new Date();
        clockEl.textContent = now.toLocaleTimeString('en-GB', { 
            hour: '2-digit', minute: '2-digit', second: '2-digit' 
        }) + ' UTC';
    }
    tick();
    setInterval(tick, 1000);
}

// 4. ACTIVITY TICKER — Simulated live feed
function initActivityTicker() {
    const ticker = document.getElementById('activity-ticker');
    if (!ticker) return;
    
    const activities = [
        '🔴 TXN from Johannesburg flagged (Risk: 94)',
        '🟢 Transaction ACC-9921 cleared as Safe',
        '🟡 High velocity detected on ACC-4451',
        '🔴 Account Takeover attempt blocked',
        '🟢 Model accuracy updated to 98.4%',
        '🟡 Location mismatch: Durban → Pretoria'
    ];
    
    let idx = 0;
    setInterval(() => {
        const item = document.createElement('div');
        item.style.cssText = 'padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,0.05); font-size: 12px; animation: slideIn 0.3s ease;';
        item.textContent = activities[idx % activities.length];
        ticker.insertBefore(item, ticker.firstChild);
        if (ticker.children.length > 5) ticker.lastChild.remove();
        idx++;
    }, 4000);
}

// 5. TOAST SYSTEM — Programmatic notifications
window.showToast = function(message, type = 'success') {
    const container = document.getElementById('toast-container') || createToastContainer();
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `${type === 'error' ? '⚠️' : '✓'} ${message}`;
    toast.style.cssText = `
        padding: 14px 20px; border-radius: 10px; color: #fff; font-size: 13px;
        font-weight: 600; box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        animation: slideIn 0.35s ease; cursor: pointer; margin-bottom: 8px;
        background: ${type === 'error' ? 'var(--accent-red)' : type === 'info' ? 'var(--accent-blue)' : 'var(--accent-green)'};
    `;
    toast.onclick = () => toast.remove();
    container.appendChild(toast);
    setTimeout(() => {
        toast.style.animation = 'fadeOut 0.4s ease forwards';
        setTimeout(() => toast.remove(), 400);
    }, 4000);
};

function createToastContainer() {
    const c = document.createElement('div');
    c.id = 'toast-container';
    c.style.cssText = 'position: fixed; top: 24px; right: 24px; z-index: 2000; display: flex; flex-direction: column;';
    document.body.appendChild(c);
    return c;
}

// 6. MOBILE SIDEBAR
function initMobileSidebar() {
    const sidebar = document.querySelector('.sidebar');
    const toggle = document.querySelector('.mobile-toggle');
    if (!toggle || !sidebar) return;
    
    toggle.addEventListener('click', () => {
        sidebar.classList.toggle('open');
    });
    
    // Close on outside click
    document.addEventListener('click', (e) => {
        if (!sidebar.contains(e.target) && !toggle.contains(e.target)) {
            sidebar.classList.remove('open');
        }
    });
}

// 7. SHIMMER LOADING EFFECTS
function initShimmerEffects() {
    document.querySelectorAll('.glass-card').forEach((card, i) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        setTimeout(() => {
            card.style.transition = 'all 0.5s cubic-bezier(0.4, 0, 0.2, 1)';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, i * 100);
    });
}

// 8. NUMBER CHANGE ANIMATION
function animateNumberChange(el, from, to) {
    const duration = 800;
    const start = performance.now();
    const isFloat = String(to).includes('.');
    
    function step(now) {
        const elapsed = now - start;
        const progress = Math.min(elapsed / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3);
        const current = from + (to - from) * eased;
        
        if (el.textContent.includes('%')) {
            el.textContent = current.toFixed(1) + '%';
        } else if (el.textContent.includes('R')) {
            el.textContent = 'R ' + current.toFixed(2);
        } else {
            el.textContent = Math.floor(current).toLocaleString();
        }
        
        if (progress < 1) requestAnimationFrame(step);
    }
    
    el.style.color = to > from ? 'var(--accent-green)' : 'var(--accent-red)';
    setTimeout(() => el.style.color = '', 1000);
    requestAnimationFrame(step);
}

// 9. RANDOM LIVE SPARKLINE (adds movement to KPI cards)
function initSparklines() {
    document.querySelectorAll('.sparkline').forEach(canvas => {
        const ctx = canvas.getContext('2d');
        const data = Array(20).fill(0).map(() => Math.random() * 30 + 10);
        
        function draw() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.beginPath();
            ctx.strokeStyle = canvas.dataset.color || '#47A04A';
            ctx.lineWidth = 2;
            
            data.forEach((val, i) => {
                const x = (i / (data.length - 1)) * canvas.width;
                const y = canvas.height - (val / 50) * canvas.height;
                if (i === 0) ctx.moveTo(x, y);
                else ctx.lineTo(x, y);
            });
            
            ctx.stroke();
            
            // Shift data
            data.shift();
            data.push(Math.random() * 30 + 10);
        }
        
        setInterval(draw, 1000);
        draw();
    });
}

// Initialize sparklines if present
if (document.querySelector('.sparkline')) initSparklines();