// ============================================
// MAZI Chart Components — Animated & Live-Updatable
// ============================================

window.MAZI_CHARTS = window.MAZI_CHARTS || {};

const MAZI_COLORS = {
    text: '#cbd5e1',
    grid: 'rgba(255, 255, 255, 0.05)',
    blue: '#4250A6',
    green: '#47A04A',
    red: '#ef4444',
    orange: '#f59e0b',
    purple: '#7c3aed'
};

if (typeof Chart !== 'undefined') {
    Chart.defaults.color = MAZI_COLORS.text;
    Chart.defaults.font.family = "'Inter', -apple-system, BlinkMacSystemFont, sans-serif";
    Chart.defaults.plugins.tooltip.backgroundColor = 'rgba(20, 10, 40, 0.92)';
    Chart.defaults.plugins.tooltip.titleColor = '#f8fafc';
    Chart.defaults.plugins.tooltip.bodyColor = '#cbd5e1';
    Chart.defaults.plugins.tooltip.borderColor = 'rgba(66, 80, 166, 0.4)';
    Chart.defaults.plugins.tooltip.borderWidth = 1;
    Chart.defaults.plugins.tooltip.padding = 12;
    Chart.defaults.plugins.tooltip.cornerRadius = 8;
}

function getRiskColor(val) {
    if (val > 80) return MAZI_COLORS.red;
    if (val > 50) return MAZI_COLORS.orange;
    return MAZI_COLORS.green;
}

// 1. Animated Risk Gauge
function createRiskGauge(canvasId, value) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return null;
    const ctx = canvas.getContext('2d');
    const safeVal = Math.min(100, Math.max(0, Number(value) || 0));

    if (window.MAZI_CHARTS[canvasId]) {
        window.MAZI_CHARTS[canvasId].destroy();
    }

    const chart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Risk', 'Safe'],
            datasets: [{
                data: [0, 100],
                backgroundColor: [getRiskColor(safeVal), 'rgba(255,255,255,0.05)'],
                borderWidth: 0,
                cutout: '80%'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            rotation: -90,
            circumference: 180,
            plugins: { legend: { display: false }, tooltip: { enabled: false } },
            animation: { animateScale: true, animateRotate: true, duration: 1200, easing: 'easeOutQuart' }
        }
    });

    setTimeout(() => {
        chart.data.datasets[0].data = [safeVal, 100 - safeVal];
        chart.data.datasets[0].backgroundColor[0] = getRiskColor(safeVal);
        chart.update();
    }, 250);

    window.MAZI_CHARTS[canvasId] = chart;
    return chart;
}

// Live updater for Risk Gauge
window.updateRiskGauge = function(canvasId, newValue) {
    const chart = window.MAZI_CHARTS[canvasId];
    const safeVal = Math.min(100, Math.max(0, Number(newValue) || 0));
    const color = getRiskColor(safeVal);

    if (chart) {
        chart.data.datasets[0].data = [safeVal, 100 - safeVal];
        chart.data.datasets[0].backgroundColor[0] = color;
        chart.update();
    }

    const valEl = document.getElementById('network-risk-value');
    const labelEl = document.getElementById('network-risk-label');
    if (valEl) {
        valEl.textContent = safeVal + '%';
        valEl.style.color = color;
    }
    if (labelEl) {
        labelEl.style.color = color;
        if (safeVal > 80) {
            labelEl.textContent = 'Critical Risk Detected';
        } else if (safeVal > 50) {
            labelEl.textContent = 'Elevated Network Threat';
        } else {
            labelEl.textContent = 'Network Traffic Normal';
        }
    }
};

// 2. Animated Line Chart
function createLineChart(canvasId, labels, data, color = MAZI_COLORS.green) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return null;
    const ctx = canvas.getContext('2d');

    if (window.MAZI_CHARTS[canvasId]) {
        window.MAZI_CHARTS[canvasId].destroy();
    }

    const gradient = ctx.createLinearGradient(0, 0, 0, 250);
    gradient.addColorStop(0, color + '33');
    gradient.addColorStop(1, color + '05');

    const chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Avg Risk / Activity',
                data: data,
                borderColor: color,
                backgroundColor: gradient,
                borderWidth: 2.5,
                fill: true,
                tension: 0.4,
                pointRadius: 4,
                pointHoverRadius: 6,
                pointBackgroundColor: color,
                pointBorderColor: '#fff',
                pointBorderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: { intersect: false, mode: 'index' },
            plugins: { legend: { display: false } },
            scales: {
                y: { grid: { color: MAZI_COLORS.grid }, beginAtZero: true },
                x: { grid: { display: false } }
            },
            animation: { duration: 900, easing: 'easeOutQuart' }
        }
    });

    window.MAZI_CHARTS[canvasId] = chart;
    return chart;
}

// 3. Animated Bar Chart
function createBarChart(canvasId, labels, data, colors = [MAZI_COLORS.red, MAZI_COLORS.orange, MAZI_COLORS.blue, MAZI_COLORS.green]) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return null;

    if (window.MAZI_CHARTS[canvasId]) {
        window.MAZI_CHARTS[canvasId].destroy();
    }

    const chart = new Chart(canvas.getContext('2d'), {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Case Volume',
                data: data,
                backgroundColor: colors,
                borderRadius: 6,
                borderSkipped: false
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                y: { grid: { color: MAZI_COLORS.grid }, beginAtZero: true },
                x: { grid: { display: false } }
            },
            animation: { duration: 900, easing: 'easeOutQuart' }
        }
    });

    window.MAZI_CHARTS[canvasId] = chart;
    return chart;
}

// 4. Animated Doughnut Chart
function createDoughnutChart(canvasId, labels, data, colors) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return null;

    if (window.MAZI_CHARTS[canvasId]) {
        window.MAZI_CHARTS[canvasId].destroy();
    }

    const chart = new Chart(canvas.getContext('2d'), {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors || [MAZI_COLORS.red, MAZI_COLORS.orange, MAZI_COLORS.blue, MAZI_COLORS.green],
                borderWidth: 0,
                cutout: '70%',
                hoverOffset: 10
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'right', labels: { padding: 15, usePointStyle: true } }
            },
            animation: { animateScale: true, animateRotate: true, duration: 1000 }
        }
    });

    window.MAZI_CHARTS[canvasId] = chart;
    return chart;
}

// 5. Radar Chart
function createRadarChart(canvasId, labels, data, color = MAZI_COLORS.green) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return null;

    if (window.MAZI_CHARTS[canvasId]) {
        window.MAZI_CHARTS[canvasId].destroy();
    }

    const chart = new Chart(canvas.getContext('2d'), {
        type: 'radar',
        data: {
            labels: labels,
            datasets: [{
                label: 'AI Model',
                data: data,
                borderColor: color,
                backgroundColor: color + '4D',
                pointBackgroundColor: color,
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: color,
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                r: {
                    grid: { color: MAZI_COLORS.grid },
                    pointLabels: { color: MAZI_COLORS.text, font: { size: 11 } },
                    ticks: { display: false, backdropColor: 'transparent' },
                    angleLines: { color: MAZI_COLORS.grid },
                    suggestedMin: 0,
                    suggestedMax: 100
                }
            },
            animation: { duration: 1000 }
        }
    });

    window.MAZI_CHARTS[canvasId] = chart;
    return chart;
}