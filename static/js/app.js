// ============================================
// MAZI Fraud AI — Live Dashboard Engine
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    initLiveStats();
    initCounters();
    initClock();
    initToasts();
    initMobileSidebar();
    initShimmerEffects();
    if (document.querySelector('.sparkline')) {
        initSparklines();
    }
});

function initToasts() {
    document.querySelectorAll('.toast').forEach(toast => {
        toast.onclick = () => toast.remove();
        setTimeout(() => {
            toast.style.animation = 'fadeOut 0.4s ease forwards';
            setTimeout(() => toast.remove(), 400);
        }, 4500);
    });
}

// 1. LIVE STATS & LIVE CHARTS POLLING — Updates every 4 seconds from SQLite
function initLiveStats() {
    if (!document.getElementById('riskGauge')) return;

    let lastSeenCaseId = null;

    async function fetchStats() {
        try {
            const res = await fetch('/dashboard/api/stats', {
                headers: { 'Cache-Control': 'no-cache' }
            });
            if (!res.ok) return;
            const data = await res.json();

            // A. Update all [data-stat] KPI numbers
            ['transaction_count', 'active_alerts', 'fraud_count', 'avg_risk_score'].forEach(key => {
                if (data[key] !== undefined) {
                    document.querySelectorAll(`[data-stat="${key}"]`).forEach(el => {
                        const currentNum = parseFloat(el.textContent.replace(/[^0-9.-]+/g, '')) || 0;
                        const nextNum = parseFloat(data[key]) || 0;
                        if (currentNum !== nextNum) {
                            animateNumberChange(el, currentNum, nextNum);
                        }
                    });
                }
            });

            // B. Update Live Charts & Risk Gauge
            if (data.chart_data && window.MAZI_CHARTS) {
                const cd = data.chart_data;

                // 1) Update Network Risk Gauge & Percentage Text
                if (typeof window.updateRiskGauge === 'function') {
                    window.updateRiskGauge('riskGauge', cd.network_risk);
                }

                // 2) Update 7-Day Fraud Trends Line Chart
                const trendChart = window.MAZI_CHARTS['fraudTrendChart'];
                if (trendChart && Array.isArray(cd.weekly_trends)) {
                    trendChart.data.datasets[0].data = cd.weekly_trends;
                    trendChart.update();
                }

                // 3) Update Attack Vectors Doughnut Chart
                const vectorChart = window.MAZI_CHARTS['fraudTypeChart'];
                if (vectorChart && Array.isArray(cd.attack_vectors)) {
                    vectorChart.data.datasets[0].data = cd.attack_vectors;
                    vectorChart.update();
                }

                // 4) Update Alert Severity Bar Chart
                const sevChart = window.MAZI_CHARTS['riskDistributionChart'];
                if (sevChart && Array.isArray(cd.alert_severity)) {
                    sevChart.data.datasets[0].data = cd.alert_severity;
                    sevChart.update();

                    const critLabel = document.getElementById('critical-interceptions-count');
                    if (critLabel) {
                        critLabel.textContent = `${cd.alert_severity[0]} Critical Interceptions`;
                    }
                }
            }

            // C. Update Live Activity Feed with real recorded database cases
            const ticker = document.getElementById('activity-ticker');
            if (ticker && Array.isArray(data.fraud_cases) && data.fraud_cases.length > 0) {
                const newestCase = data.fraud_cases[0];
                if (lastSeenCaseId !== newestCase.id) {
                    lastSeenCaseId = newestCase.id;
                    ticker.innerHTML = data.fraud_cases.slice(0, 4).map(c => {
                        const borderColor = c.risk_score > 80 ? 'var(--accent-red)' : 'var(--accent-orange)';
                        return `
                            <div style="padding: 8px; background: rgba(0,0,0,0.2); border-left: 3px solid ${borderColor}; font-size: 12px; color: var(--text-secondary); border-radius: 0 4px 4px 0; animation: slideIn 0.3s ease;">
                                <strong style="color: var(--text-primary);">${c.type}</strong> (${c.account_number})<br>
                                <span style="color: var(--accent-blue);">ID: #${c.id}</span> | Risk: <strong>${c.risk_score}%</strong> | R ${c.loss}
                            </div>
                        `;
                    }).join('');
                }
            }

        } catch (e) {
            console.log('Live stats sync waiting for server...');
        }
    }

    setInterval(fetchStats, 4000);
    fetchStats();
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
            const eased = 1 - Math.pow(1 - progress, 3);
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
        clockEl.textContent = now.toUTCString();
    }
    tick();
    setInterval(tick, 1000);
}

// 4. TOAST SYSTEM — Programmatic notifications
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

// 5. MOBILE SIDEBAR
function initMobileSidebar() {
    const sidebar = document.querySelector('.sidebar');
    const toggle = document.querySelector('.mobile-toggle');
    if (!toggle || !sidebar) return;

    toggle.addEventListener('click', () => {
        sidebar.classList.toggle('open');
    });

    document.addEventListener('click', (e) => {
        if (!sidebar.contains(e.target) && !toggle.contains(e.target)) {
            sidebar.classList.remove('open');
        }
    });
}

// 6. SHIMMER LOADING EFFECTS
function initShimmerEffects() {
    document.querySelectorAll('.glass-card').forEach((card, i) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        setTimeout(() => {
            card.style.transition = 'all 0.5s cubic-bezier(0.4, 0, 0.2, 1)';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, i * 80);
    });
}

// 7. NUMBER CHANGE ANIMATION
function animateNumberChange(el, from, to) {
    const duration = 700;
    const start = performance.now();

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
    setTimeout(() => el.style.color = '', 900);
    requestAnimationFrame(step);
}

// 8. LIVE SPARKLINE
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
            data.shift();
            data.push(Math.random() * 30 + 10);
        }

        setInterval(draw, 1000);
        draw();
    });
}