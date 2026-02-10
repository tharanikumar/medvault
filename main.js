/**
 * MedVault - Main JavaScript File
 * Healthcare Management System
 */

// ==================== UTILITY FUNCTIONS ====================

/**
 * Format date to readable string
 */
function formatDate(date) {
    const options = { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
    };
    return new Date(date).toLocaleDateString('en-US', options);
}

/**
 * Format date with time
 */
function formatDateTime(date) {
    const options = { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    return new Date(date).toLocaleDateString('en-US', options);
}

/**
 * Format currency
 */
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

/**
 * Truncate text with ellipsis
 */
function truncateText(text, maxLength) {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

/**
 * Debounce function
 */
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

// ==================== NOTIFICATION SYSTEM ====================

/**
 * Show notification
 */
function showNotification(message, type = 'info', duration = 5000) {
    const container = document.getElementById('notification-container');
    
    if (!container) {
        console.log(`Notification [${type}]: ${message}`);
        return;
    }
    
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-icon">
            <i class="fas fa-${getNotificationIcon(type)}"></i>
        </div>
        <div class="notification-content">
            <p>${message}</p>
        </div>
        <button class="notification-close" onclick="this.parentElement.remove()">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    container.appendChild(notification);
    
    // Auto remove
    if (duration > 0) {
        setTimeout(() => {
            notification.style.opacity = '0';
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => notification.remove(), 300);
        }, duration);
    }
}

function getNotificationIcon(type) {
    const icons = {
        success: 'check-circle',
        error: 'times-circle',
        warning: 'exclamation-triangle',
        info: 'info-circle'
    };
    return icons[type] || 'info-circle';
}

// ==================== FORM VALIDATION ====================

/**
 * Validate email format
 */
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

/**
 * Validate phone number
 */
function isValidPhone(phone) {
    const phoneRegex = /^[\d\s\-\+\(\)]{10,}$/;
    return phoneRegex.test(phone);
}

/**
 * Validate password strength
 */
function getPasswordStrength(password) {
    let strength = 0;
    const feedback = [];
    
    if (password.length >= 8) {
        strength += 1;
    } else {
        feedback.push('At least 8 characters');
    }
    
    if (/[a-z]/.test(password) && /[A-Z]/.test(password)) {
        strength += 1;
    } else {
        feedback.push('Mix of uppercase and lowercase');
    }
    
    if (/[0-9]/.test(password)) {
        strength += 1;
    } else {
        feedback.push('Include numbers');
    }
    
    if (/[^a-zA-Z0-9]/.test(password)) {
        strength += 1;
    } else {
        feedback.push('Special characters');
    }
    
    return { strength, feedback };
}

// ==================== AJAX HELPERS ====================

/**
 * Make AJAX request
 */
async function makeRequest(url, method = 'GET', data = null) {
    const options = {
        method,
        headers: {
            'Content-Type': 'application/json'
        }
    };
    
    if (data) {
        options.body = JSON.stringify(data);
    }
    
    try {
        const response = await fetch(url, options);
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.message || 'Request failed');
        }
        
        return result;
    } catch (error) {
        console.error('Request error:', error);
        throw error;
    }
}

/**
 * Submit form via AJAX
 */
async function submitForm(formId, url) {
    const form = document.getElementById(formId);
    const formData = new FormData(form);
    const data = Object.fromEntries(formData);
    
    try {
        showNotification('Processing...', 'info', 0);
        const result = await makeRequest(url, 'POST', data);
        
        if (result.success) {
            showNotification(result.message || 'Success!', 'success');
            return result;
        } else {
            showNotification(result.message || 'Error occurred', 'error');
            return null;
        }
    } catch (error) {
        showNotification(error.message || 'An error occurred', 'error');
        return null;
    }
}

// ==================== UI HELPERS ====================

/**
 * Show loading state
 */
function showLoading(element) {
    element.disabled = true;
    const originalText = element.innerHTML;
    element.dataset.originalText = originalText;
    element.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
}

/**
 * Hide loading state
 */
function hideLoading(element) {
    element.disabled = false;
    element.innerHTML = element.dataset.originalText || element.innerHTML;
}

/**
 * Toggle password visibility
 */
function togglePasswordVisibility(inputId) {
    const input = document.getElementById(inputId);
    const icon = input.parentElement.querySelector('.toggle-password');
    
    if (input.type === 'password') {
        input.type = 'text';
        icon.classList.remove('fa-eye');
        icon.classList.add('fa-eye-slash');
    } else {
        input.type = 'password';
        icon.classList.remove('fa-eye-slash');
        icon.classList.add('fa-eye');
    }
}

// ==================== DASHBOARD HELPERS ====================

/**
 * Update dashboard statistics
 */
function updateStats() {
    // This can be extended to fetch fresh data
    console.log('Updating dashboard stats...');
}

/**
 * Refresh appointments list
 */
function refreshAppointments() {
    const container = document.getElementById('appointments-container');
    if (container) {
        container.innerHTML = '<div class="loading"><i class="fas fa-spinner fa-spin"></i> Loading...</div>';
        // Reload page or fetch new data
        window.location.reload();
    }
}

/**
 * Handle appointment booking
 */
async function bookAppointment(doctorId, date, time, reason) {
    const data = {
        doctor_id: doctorId,
        appointment_date: date,
        appointment_time: time,
        reason: reason
    };
    
    try {
        const result = await makeRequest('/book_appointment', 'POST', data);
        
        if (result.success) {
            showNotification('Appointment booked successfully!', 'success');
            setTimeout(() => {
                window.location.href = '/appointments';
            }, 2000);
        } else {
            showNotification(result.message || 'Failed to book appointment', 'error');
        }
    } catch (error) {
        showNotification('An error occurred while booking', 'error');
    }
}

// ==================== MODAL HELPERS ====================

/**
 * Open modal
 */
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
    }
}

/**
 * Close modal
 */
function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('active');
        document.body.style.overflow = '';
    }
}

/**
 * Close modal on overlay click
 */
document.addEventListener('click', function(e) {
    if (e.target.classList.contains('modal-overlay')) {
        e.target.classList.remove('active');
        document.body.style.overflow = '';
    }
});

// ==================== INITIALIZATION ====================

/**
 * Initialize when DOM is ready
 */
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all tooltips
    initializeTooltips();
    
    // Initialize all dropdowns
    initializeDropdowns();
    
    // Initialize auto-hide alerts
    initializeAlerts();
    
    // Initialize smooth scroll
    initializeSmoothScroll();
    
    console.log('MedVault initialized successfully');
});

function initializeTooltips() {
    const tooltipElements = document.querySelectorAll('[data-tooltip]');
    tooltipElements.forEach(element => {
        element.addEventListener('mouseenter', showTooltip);
        element.addEventListener('mouseleave', hideTooltip);
    });
}

function showTooltip(e) {
    const tooltip = document.createElement('div');
    tooltip.className = 'tooltip';
    tooltip.textContent = e.target.dataset.tooltip;
    document.body.appendChild(tooltip);
    
    const rect = e.target.getBoundingClientRect();
    tooltip.style.left = rect.left + rect.width / 2 - tooltip.offsetWidth / 2 + 'px';
    tooltip.style.top = rect.top - tooltip.offsetHeight - 10 + 'px';
}

function hideTooltip() {
    const tooltip = document.querySelector('.tooltip');
    if (tooltip) tooltip.remove();
}

function initializeDropdowns() {
    const dropdowns = document.querySelectorAll('.dropdown');
    dropdowns.forEach(dropdown => {
        const toggle = dropdown.querySelector('.dropdown-toggle');
        const menu = dropdown.querySelector('.dropdown-menu');
        
        if (toggle && menu) {
            toggle.addEventListener('click', () => {
                menu.classList.toggle('active');
            });
            
            document.addEventListener('click', (e) => {
                if (!dropdown.contains(e.target)) {
                    menu.classList.remove('active');
                }
            });
        }
    });
}

function initializeAlerts() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            alert.style.transform = 'translateX(100%)';
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    });
}

function initializeSmoothScroll() {
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

// Export for use in other scripts
window.MedVault = {
    showNotification,
    makeRequest,
    submitForm,
    formatDate,
    formatDateTime,
    formatCurrency,
    isValidEmail,
    isValidPhone,
    getPasswordStrength,
    openModal,
    closeModal,
    showLoading,
    hideLoading,
    togglePasswordVisibility
};

