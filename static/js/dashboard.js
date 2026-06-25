/**
 * Chart.js configurations for AI Interview Coach Dashboard
 */

document.addEventListener('DOMContentLoaded', () => {
    // Check if DASHBOARD_DATA exists on window
    const data = window.DASHBOARD_DATA;
    if (!data) return;

    const trendData = data.scoreTrends || [];
    const catAverages = data.categoryAverages || {};

    // Custom dark mode theme defaults for Chart.js
    Chart.defaults.color = '#9ca3af'; // var(--text-secondary)
    Chart.defaults.font.family = "'Plus Jakarta Sans', -apple-system, sans-serif";

    // 1. Score Progression Line Chart
    const trendCtx = document.getElementById('scoreTrendChart');
    if (trendCtx) {
        const labels = trendData.map(item => item.date);
        const scores = trendData.map(item => item.score);
        const roles = trendData.map(item => item.job_role);

        // Gradient for line fill
        const ctx = trendCtx.getContext('2d');
        const gradient = ctx.createLinearGradient(0, 0, 0, 200);
        gradient.addColorStop(0, 'rgba(0, 242, 254, 0.25)'); // Secondary glow
        gradient.addColorStop(1, 'rgba(0, 242, 254, 0)');

        new Chart(trendCtx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Overall Rating (%)',
                    data: scores,
                    borderColor: '#00f2fe', // var(--secondary)
                    borderWidth: 3,
                    pointBackgroundColor: '#00f2fe',
                    pointBorderColor: '#0c0e17',
                    pointBorderWidth: 2,
                    pointRadius: 5,
                    pointHoverRadius: 7,
                    tension: 0.35, // Smooth curves
                    fill: true,
                    backgroundColor: gradient
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: '#141725',
                        borderColor: 'rgba(255,255,255,0.08)',
                        borderWidth: 1,
                        padding: 10,
                        titleColor: '#fff',
                        bodyColor: '#e5e7eb',
                        callbacks: {
                            label: function(context) {
                                const index = context.dataIndex;
                                return ` Score: ${context.parsed.y}% (${roles[index]})`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: { display: false }
                    },
                    y: {
                        min: 0,
                        max: 100,
                        ticks: { stepSize: 20 },
                        grid: { color: 'rgba(255,255,255,0.04)' }
                    }
                }
            }
        });
    }

    // 2. Categorical Performance Horizontal Bar Chart
    const categoryCtx = document.getElementById('categoryChart');
    if (categoryCtx) {
        const commScore = catAverages.communication || 0;
        const techScore = catAverages.technical_accuracy || 0;
        const probScore = catAverages.problem_solving || 0;

        new Chart(categoryCtx, {
            type: 'bar',
            data: {
                labels: ['Communication', 'Technical depth', 'Problem solving'],
                datasets: [{
                    data: [commScore, techScore, probScore],
                    backgroundColor: [
                        '#00f2fe', // var(--secondary)
                        '#6366f1', // var(--primary)
                        '#ec4899'  // var(--accent)
                    ],
                    borderRadius: 6,
                    borderSkipped: false,
                    barThickness: 18
                }]
            },
            options: {
                indexAxis: 'y', // Makes it horizontal
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: '#141725',
                        borderColor: 'rgba(255,255,255,0.08)',
                        borderWidth: 1,
                        padding: 10,
                        titleColor: '#fff',
                        bodyColor: '#e5e7eb',
                        callbacks: {
                            label: function(context) {
                                return ` Average: ${context.parsed.x}%`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        min: 0,
                        max: 100,
                        ticks: { stepSize: 25 },
                        grid: { color: 'rgba(255,255,255,0.04)' }
                    },
                    y: {
                        grid: { display: false }
                    }
                }
            }
        });
    }
});