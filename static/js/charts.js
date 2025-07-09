// Charts JavaScript for Financial Dashboard

// Chart.js default configuration
Chart.defaults.font.family = "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif";
Chart.defaults.font.size = 12;
Chart.defaults.plugins.legend.position = 'top';
Chart.defaults.plugins.legend.align = 'center';
Chart.defaults.responsive = true;
Chart.defaults.maintainAspectRatio = false;

// Color palette
const colors = {
    primary: '#667eea',
    secondary: '#764ba2',
    success: '#4facfe',
    warning: '#43e97b',
    danger: '#fa709a',
    info: '#38f9d7',
    light: '#f8f9fa',
    dark: '#2c3e50'
};

// Gradient colors
const gradients = {
    primary: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    success: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
    warning: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
    danger: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)'
};

// Chart utilities
function createGradient(ctx, colorStart, colorEnd) {
    const gradient = ctx.createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, colorStart);
    gradient.addColorStop(1, colorEnd);
    return gradient;
}

function getRandomColor() {
    const colorKeys = Object.keys(colors);
    return colors[colorKeys[Math.floor(Math.random() * colorKeys.length)]];
}

// Monthly Income vs Expenses Chart
function createMonthlyChart(ctx, data) {
    const monthlyLabels = Object.keys(data).sort();
    const incomeData = monthlyLabels.map(month => data[month].income || 0);
    const expenseData = monthlyLabels.map(month => data[month].expenses || 0);
    
    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: monthlyLabels,
            datasets: [{
                label: 'Income',
                data: incomeData,
                borderColor: colors.success,
                backgroundColor: createGradient(ctx, colors.success + '20', colors.success + '05'),
                fill: true,
                tension: 0.4,
                pointRadius: 6,
                pointHoverRadius: 8,
                pointBackgroundColor: colors.success,
                pointBorderColor: '#fff',
                pointBorderWidth: 2
            }, {
                label: 'Expenses',
                data: expenseData,
                borderColor: colors.danger,
                backgroundColor: createGradient(ctx, colors.danger + '20', colors.danger + '05'),
                fill: true,
                tension: 0.4,
                pointRadius: 6,
                pointHoverRadius: 8,
                pointBackgroundColor: colors.danger,
                pointBorderColor: '#fff',
                pointBorderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        usePointStyle: true,
                        padding: 20,
                        font: {
                            size: 14,
                            weight: 'bold'
                        }
                    }
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    borderColor: colors.primary,
                    borderWidth: 1,
                    cornerRadius: 8,
                    callbacks: {
                        label: function(context) {
                            return context.dataset.label + ': $' + context.parsed.y.toLocaleString();
                        }
                    }
                }
            },
            scales: {
                x: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Month',
                        font: {
                            size: 14,
                            weight: 'bold'
                        }
                    },
                    grid: {
                        display: false
                    }
                },
                y: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Amount ($)',
                        font: {
                            size: 14,
                            weight: 'bold'
                        }
                    },
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    },
                    ticks: {
                        callback: function(value) {
                            return '$' + value.toLocaleString();
                        }
                    }
                }
            },
            interaction: {
                mode: 'index',
                intersect: false
            }
        }
    });
}

// Category Spending Chart
function createCategoryChart(ctx, data) {
    const categoryLabels = Object.keys(data);
    const categoryAmounts = Object.values(data);
    
    // Generate colors for each category
    const backgroundColors = categoryLabels.map(() => getRandomColor());
    const borderColors = backgroundColors.map(color => color);
    
    return new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: categoryLabels,
            datasets: [{
                data: categoryAmounts,
                backgroundColor: backgroundColors,
                borderColor: borderColors,
                borderWidth: 3,
                hoverBorderWidth: 5,
                hoverOffset: 10
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 20,
                        usePointStyle: true,
                        font: {
                            size: 12
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    borderColor: colors.primary,
                    borderWidth: 1,
                    cornerRadius: 8,
                    callbacks: {
                        label: function(context) {
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((context.parsed / total) * 100).toFixed(1);
                            return context.label + ': $' + context.parsed.toLocaleString() + ' (' + percentage + '%)';
                        }
                    }
                }
            },
            animation: {
                animateRotate: true,
                animateScale: true,
                duration: 1000
            }
        }
    });
}

// Goal Progress Chart
function createGoalProgressChart(ctx, goals) {
    const goalNames = goals.map(goal => goal.name);
    const progressData = goals.map(goal => goal.progress);
    
    return new Chart(ctx, {
        type: 'horizontalBar',
        data: {
            labels: goalNames,
            datasets: [{
                label: 'Progress (%)',
                data: progressData,
                backgroundColor: colors.warning,
                borderColor: colors.warning,
                borderWidth: 2,
                borderRadius: 5,
                borderSkipped: false
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    callbacks: {
                        label: function(context) {
                            return context.parsed.x + '% Complete';
                        }
                    }
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        callback: function(value) {
                            return value + '%';
                        }
                    }
                },
                y: {
                    ticks: {
                        maxTicksLimit: 5
                    }
                }
            }
        }
    });
}

// Debt Payoff Chart
function createDebtChart(ctx, debts) {
    const debtNames = debts.map(debt => debt.name);
    const remainingAmounts = debts.map(debt => debt.remaining);
    const paidAmounts = debts.map(debt => debt.paid);
    
    return new Chart(ctx, {
        type: 'bar',
        data: {
            labels: debtNames,
            datasets: [{
                label: 'Remaining',
                data: remainingAmounts,
                backgroundColor: colors.danger,
                borderColor: colors.danger,
                borderWidth: 2
            }, {
                label: 'Paid',
                data: paidAmounts,
                backgroundColor: colors.success,
                borderColor: colors.success,
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.dataset.label + ': $' + context.parsed.y.toLocaleString();
                        }
                    }
                }
            },
            scales: {
                x: {
                    stacked: true
                },
                y: {
                    stacked: true,
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '$' + value.toLocaleString();
                        }
                    }
                }
            }
        }
    });
}

// Spending Trend Chart
function createSpendingTrendChart(ctx, data) {
    const dates = Object.keys(data).sort();
    const amounts = dates.map(date => data[date]);
    
    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [{
                label: 'Daily Spending',
                data: amounts,
                borderColor: colors.primary,
                backgroundColor: colors.primary + '20',
                fill: true,
                tension: 0.4,
                pointRadius: 4,
                pointHoverRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return '$' + context.parsed.y.toLocaleString();
                        }
                    }
                }
            },
            scales: {
                x: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Date'
                    }
                },
                y: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Amount ($)'
                    },
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '$' + value.toLocaleString();
                        }
                    }
                }
            }
        }
    });
}

// Budget vs Actual Chart
function createBudgetChart(ctx, budgetData, actualData) {
    const categories = Object.keys(budgetData);
    const budgetAmounts = categories.map(cat => budgetData[cat]);
    const actualAmounts = categories.map(cat => actualData[cat] || 0);
    
    return new Chart(ctx, {
        type: 'bar',
        data: {
            labels: categories,
            datasets: [{
                label: 'Budget',
                data: budgetAmounts,
                backgroundColor: colors.info,
                borderColor: colors.info,
                borderWidth: 2
            }, {
                label: 'Actual',
                data: actualAmounts,
                backgroundColor: colors.warning,
                borderColor: colors.warning,
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.dataset.label + ': $' + context.parsed.y.toLocaleString();
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '$' + value.toLocaleString();
                        }
                    }
                }
            }
        }
    });
}

// Initialize charts based on page
function initializeCharts() {
    // Monthly chart
    const monthlyCtx = document.getElementById('monthlyChart');
    if (monthlyCtx && window.monthlyData) {
        createMonthlyChart(monthlyCtx.getContext('2d'), window.monthlyData);
    }
    
    // Category chart
    const categoryCtx = document.getElementById('categoryChart');
    if (categoryCtx && window.categoryData) {
        createCategoryChart(categoryCtx.getContext('2d'), window.categoryData);
    }
    
    // Goal progress chart
    const goalCtx = document.getElementById('goalChart');
    if (goalCtx && window.goalData) {
        createGoalProgressChart(goalCtx.getContext('2d'), window.goalData);
    }
    
    // Debt chart
    const debtCtx = document.getElementById('debtChart');
    if (debtCtx && window.debtData) {
        createDebtChart(debtCtx.getContext('2d'), window.debtData);
    }
    
    // Spending trend chart
    const trendCtx = document.getElementById('trendChart');
    if (trendCtx && window.trendData) {
        createSpendingTrendChart(trendCtx.getContext('2d'), window.trendData);
    }
    
    // Budget chart
    const budgetCtx = document.getElementById('budgetChart');
    if (budgetCtx && window.budgetData && window.actualData) {
        createBudgetChart(budgetCtx.getContext('2d'), window.budgetData, window.actualData);
    }
}

// Chart animation utilities
function animateChart(chart) {
    chart.update('active');
}

function refreshAllCharts() {
    Chart.helpers.each(Chart.instances, function(instance) {
        instance.update();
    });
}

// Export functions
window.ChartUtils = {
    createMonthlyChart,
    createCategoryChart,
    createGoalProgressChart,
    createDebtChart,
    createSpendingTrendChart,
    createBudgetChart,
    initializeCharts,
    animateChart,
    refreshAllCharts,
    colors,
    gradients
};

// Initialize charts when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeCharts();
});
