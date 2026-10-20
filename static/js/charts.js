// ============================================
// MAZI Chart Components — Animated & Reusable
// ============================================

const MAZI_COLORS = {
    text: '#cbd5e1',
    grid: 'rgba(255, 255, 255, 0.05)',
    blue: '#4250A6',
    green: '#47A04A',
    red: '#ef4444',
    orange: '#f59e0b'
};

Chart.defaults.color = MAZI_COLORS.text;
Chart.defaults.font.family = "'Inter', sans-serif";

// Animated Risk Gauge
function createRiskGauge(canvasId, value) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    const chart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Risk', 'Safe'],
            datasets: [{
                data: [0, 100],
                backgroundColor: [MAZI_COLORS.red, 'rgba(255,255,255,0.05)'],
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
            animation: { animateScale: true, animateRotate: true, duration: 2000, easing: 'easeOutQuart' }
        }
    });
    
    // Animate to actual value
    setTimeout(() => {
        chart.data.datasets[0].data = [value, 100 - value];
        chart.update();
    }, 300);
    
    return chart;
}

// Animated Line Chart
function createLineChart(canvasId, labels, data, color = MAZI_COLORS.green) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    
    // Create gradient
    const gradient = ctx.createLinearGradient(0, 0, 0, 250);
    gradient.addColorStop(0, color + '33');
    gradient.addColorStop(1, color + '05');
    
    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Interceptions',
                data: data,
                borderColor: color,
                backgroundColor: gradient,
                borderWidth: 2,
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
            animation: { duration: 1500, easing: 'easeOutQuart' }
        }
    });
}

// Animated Bar Chart
function createBarChart(canvasId, labels, data, colors = [MAZI_COLORS.red, MAZI_COLORS.orange, MAZI_COLORS.blue, MAZI_COLORS.green]) {
    return new Chart(document.getElementById(canvasId).getContext('2d'), {
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
            animation: { duration: 1200, easing: 'easeOutBounce', delay: (ctx) => ctx.dataIndex * 100 }
        }
    });
}

// Animated Doughnut
function createDoughnutChart(canvasId, labels, data, colors) {
    return new Chart(document.getElementById(canvasId).getContext('2d'), {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors,
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
            animation: { animateScale: true, animateRotate: true, duration: 1500 }
        }
    });
}

// Radar Chart
function createRadarChart(canvasId, labels, data, color = MAZI_COLORS.green) {
    return new Chart(document.getElementById(canvasId).getContext('2d'), {
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
            animation: { duration: 1500 }
        }
    });
}