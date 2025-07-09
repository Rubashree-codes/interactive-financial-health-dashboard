// Dashboard JavaScript for Financial Dashboard

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeDashboard();
});

function initializeDashboard() {
    // Initialize tooltips
    initializeTooltips();
    
    // Initialize form validation
    initializeFormValidation();
    
    // Initialize animations
    initializeAnimations();
    
    // Initialize charts refresh
    initializeChartRefresh();
    
    // Initialize auto-save features
    initializeAutoSave();
}

// Tooltip initialization
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Form validation
function initializeFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    
    Array.prototype.slice.call(forms).forEach(function (form) {
        form.addEventListener('submit', function (event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
}

// Animation initialization
function initializeAnimations() {
    // Animate cards on scroll
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.animation = 'slideInUp 0.6s ease forwards';
            }
        });
    });
    
    document.querySelectorAll('.card').forEach(card => {
        observer.observe(card);
    });
    
    // Animate numbers
    animateNumbers();
}

// Number animation
function animateNumbers() {
    const numbers = document.querySelectorAll('.stat-number, .display-4');
    
    numbers.forEach(number => {
        const text = number.textContent;
        const match = text.match(/[\d,]+\.?\d*/);
        
        if (match) {
            const finalValue = parseFloat(match[0].replace(/,/g, ''));
            if (!isNaN(finalValue)) {
                animateNumber(number, finalValue, text);
            }
        }
    });
}

function animateNumber(element, finalValue, originalText) {
    const duration = 2000;
    const startTime = performance.now();
    
    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        const currentValue = finalValue * progress;
        const formattedValue = originalText.replace(/[\d,]+\.?\d*/, formatNumber(currentValue));
        
        element.textContent = formattedValue;
        
        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }
    
    requestAnimationFrame(update);
}

function formatNumber(num) {
    return num.toLocaleString('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
}

// Chart refresh functionality
function initializeChartRefresh() {
    const refreshButtons = document.querySelectorAll('.refresh-chart');
    
    refreshButtons.forEach(button => {
        button.addEventListener('click', function() {
            const chartId = this.dataset.chartId;
            refreshChart(chartId);
        });
    });
}

function refreshChart(chartId) {
    const chartElement = document.getElementById(chartId);
    if (chartElement) {
        chartElement.style.opacity = '0.5';
        
        // Simulate chart refresh
        setTimeout(() => {
            chartElement.style.opacity = '1';
            showNotification('Chart refreshed successfully!', 'success');
        }, 1000);
    }
}

// Auto-save functionality
function initializeAutoSave() {
    const forms = document.querySelectorAll('form[data-autosave]');
    
    forms.forEach(form => {
        const inputs = form.querySelectorAll('input, select, textarea');
        
        inputs.forEach(input => {
            input.addEventListener('change', function() {
                autoSaveForm(form);
            });
        });
    });
}

function autoSaveForm(form) {
    const formData = new FormData(form);
    const data = Object.fromEntries(formData);
    
    // Save to localStorage
    localStorage.setItem(`autosave_${form.id}`, JSON.stringify(data));
    
    showNotification('Data saved automatically', 'info', 2000);
}

// Notification system
function showNotification(message, type = 'info', duration = 5000) {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show notification`;
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Add to page
    const container = document.querySelector('.container') || document.body;
    container.insertBefore(notification, container.firstChild);
    
    // Auto-hide
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, duration);
}

// Utility functions
function confirmDelete(message = 'Are you sure you want to delete this item?') {
    return confirm(message);
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

function formatDate(date) {
    return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    }).format(new Date(date));
}

// Goal progress animation
function animateProgressBars() {
    const progressBars = document.querySelectorAll('.progress-bar');
    
    progressBars.forEach(bar => {
        const width = bar.style.width;
        bar.style.width = '0';
        
        setTimeout(() => {
            bar.style.width = width;
        }, 500);
    });
}

// File upload handling
function handleFileUpload() {
    const fileInput = document.getElementById('file');
    const uploadButton = document.querySelector('button[type="submit"]');
    
    if (fileInput) {
        fileInput.addEventListener('change', function() {
            const file = this.files[0];
            
            if (file) {
                if (file.type !== 'text/csv') {
                    showNotification('Please select a CSV file', 'error');
                    this.value = '';
                    return;
                }
                
                if (file.size > 16 * 1024 * 1024) {
                    showNotification('File size must be less than 16MB', 'error');
                    this.value = '';
                    return;
                }
                
                // Show file info
                const fileName = file.name;
                const fileSize = (file.size / 1024 / 1024).toFixed(2);
                
                showNotification(`File selected: ${fileName} (${fileSize} MB)`, 'success');
                
                if (uploadButton) {
                    uploadButton.textContent = `Upload ${fileName}`;
                    uploadButton.disabled = false;
                }
            }
        });
    }
}

// Form submission handling
function handleFormSubmission() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitButton = form.querySelector('button[type="submit"]');
            
            if (submitButton) {
                submitButton.disabled = true;
                submitButton.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';
                
                // Re-enable button after 5 seconds as fallback
                setTimeout(() => {
                    submitButton.disabled = false;
                    submitButton.innerHTML = submitButton.dataset.originalText || 'Submit';
                }, 5000);
            }
        });
    });
}

// Modal handling
function initializeModals() {
    const modals = document.querySelectorAll('.modal');
    
    modals.forEach(modal => {
        modal.addEventListener('show.bs.modal', function() {
            const form = this.querySelector('form');
            if (form) {
                form.reset();
                form.classList.remove('was-validated');
            }
        });
    });
}

// Search functionality
function initializeSearch() {
    const searchInput = document.querySelector('.search-input');
    const searchableItems = document.querySelectorAll('.searchable-item');
    
    if (searchInput && searchableItems.length > 0) {
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            
            searchableItems.forEach(item => {
                const text = item.textContent.toLowerCase();
                const isVisible = text.includes(searchTerm);
                
                item.style.display = isVisible ? 'block' : 'none';
            });
        });
    }
}

// Initialize all dashboard functionality
function initializeAll() {
    initializeDashboard();
    handleFileUpload();
    handleFormSubmission();
    initializeModals();
    initializeSearch();
    animateProgressBars();
}

// Call initialization
initializeAll();

// Export functions for use in other scripts
window.FinanceDashboard = {
    showNotification,
    confirmDelete,
    formatCurrency,
    formatDate,
    animateProgressBars,
    refreshChart
};
