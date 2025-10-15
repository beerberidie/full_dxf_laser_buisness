/**
 * Laser OS Tier 1 - Main JavaScript
 * 
 * Common utilities and functions used across the application.
 */

// ============================================================================
// Utility Functions
// ============================================================================

/**
 * Show a toast notification
 * @param {string} message - Message to display
 * @param {string} type - Type of notification (success, error, warning, info)
 * @param {number} duration - Duration in milliseconds (default: 3000)
 */
function showToast(message, type = 'info', duration = 3000) {
    const toast = document.createElement('div');
    toast.className = `alert alert-${type}`;
    toast.innerHTML = `
        ${message}
        <button class="alert-close" onclick="this.parentElement.remove()">&times;</button>
    `;
    
    // Find or create flash messages container
    let container = document.querySelector('.flash-messages .container');
    if (!container) {
        const flashMessages = document.createElement('div');
        flashMessages.className = 'flash-messages';
        flashMessages.innerHTML = '<div class="container"></div>';
        document.querySelector('.main').insertAdjacentElement('beforebegin', flashMessages);
        container = flashMessages.querySelector('.container');
    }
    
    container.appendChild(toast);
    
    // Auto-dismiss after duration
    if (duration > 0) {
        setTimeout(() => {
            toast.remove();
        }, duration);
    }
}

/**
 * Confirm an action with a custom message
 * @param {string} message - Confirmation message
 * @param {Function} callback - Function to call if confirmed
 */
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

/**
 * Format a date string
 * @param {string} dateString - ISO date string
 * @param {string} format - Format type ('date', 'datetime', 'time')
 * @returns {string} Formatted date
 */
function formatDate(dateString, format = 'date') {
    if (!dateString) return '';
    
    const date = new Date(dateString);
    
    if (format === 'date') {
        return date.toLocaleDateString('en-ZA');
    } else if (format === 'datetime') {
        return date.toLocaleString('en-ZA');
    } else if (format === 'time') {
        return date.toLocaleTimeString('en-ZA');
    }
    
    return dateString;
}

/**
 * Format a datetime string
 * @param {string} dateString - ISO date string
 * @returns {string} Formatted datetime
 */
function formatDateTime(dateString) {
    return formatDate(dateString, 'datetime');
}

/**
 * Format a number as currency (ZAR)
 * @param {number} amount - Amount to format
 * @returns {string} Formatted currency
 */
function formatCurrency(amount) {
    if (amount === null || amount === undefined) return 'R 0.00';
    return `R ${amount.toLocaleString('en-ZA', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

/**
 * Format bytes as human-readable file size
 * @param {number} bytes - File size in bytes
 * @returns {string} Formatted file size
 */
function formatFileSize(bytes) {
    if (!bytes) return '0 B';
    
    const units = ['B', 'KB', 'MB', 'GB', 'TB'];
    let size = bytes;
    let unitIndex = 0;
    
    while (size >= 1024 && unitIndex < units.length - 1) {
        size /= 1024;
        unitIndex++;
    }
    
    return `${size.toFixed(1)} ${units[unitIndex]}`;
}

/**
 * Debounce a function
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in milliseconds
 * @returns {Function} Debounced function
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

// ============================================================================
// AJAX Utilities
// ============================================================================

/**
 * Make an AJAX request
 * @param {string} url - URL to request
 * @param {Object} options - Fetch options
 * @returns {Promise} Fetch promise
 */
async function ajax(url, options = {}) {
    const defaults = {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        },
    };
    
    const config = { ...defaults, ...options };
    
    try {
        const response = await fetch(url, config);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
            return await response.json();
        } else {
            return await response.text();
        }
    } catch (error) {
        console.error('AJAX error:', error);
        throw error;
    }
}

/**
 * Make a GET request
 * @param {string} url - URL to request
 * @returns {Promise} Fetch promise
 */
function get(url) {
    return ajax(url, { method: 'GET' });
}

/**
 * Make a POST request
 * @param {string} url - URL to request
 * @param {Object} data - Data to send
 * @returns {Promise} Fetch promise
 */
function post(url, data) {
    return ajax(url, {
        method: 'POST',
        body: JSON.stringify(data),
    });
}

/**
 * Make a PUT request
 * @param {string} url - URL to request
 * @param {Object} data - Data to send
 * @returns {Promise} Fetch promise
 */
function put(url, data) {
    return ajax(url, {
        method: 'PUT',
        body: JSON.stringify(data),
    });
}

/**
 * Make a DELETE request
 * @param {string} url - URL to request
 * @returns {Promise} Fetch promise
 */
function del(url) {
    return ajax(url, { method: 'DELETE' });
}

// ============================================================================
// Form Validation
// ============================================================================

/**
 * Validate email format
 * @param {string} email - Email to validate
 * @returns {boolean} True if valid
 */
function isValidEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

/**
 * Validate phone format (South African)
 * @param {string} phone - Phone to validate
 * @returns {boolean} True if valid
 */
function isValidPhone(phone) {
    // Accept various formats: +27 11 123 4567, 011 123 4567, etc.
    const re = /^(\+27|0)[0-9\s-]{9,}$/;
    return re.test(phone);
}

/**
 * Check if a field is required and not empty
 * @param {string} value - Value to check
 * @returns {boolean} True if not empty
 */
function isRequired(value) {
    return value !== null && value !== undefined && value.trim() !== '';
}

/**
 * Add form validation to a form
 * @param {HTMLFormElement} form - Form element
 */
function addFormValidation(form) {
    form.addEventListener('submit', function(e) {
        let isValid = true;
        
        // Check required fields
        const requiredFields = form.querySelectorAll('[required]');
        requiredFields.forEach(field => {
            if (!isRequired(field.value)) {
                isValid = false;
                field.classList.add('error');
                showToast(`${field.name} is required`, 'error');
            } else {
                field.classList.remove('error');
            }
        });
        
        // Check email fields
        const emailFields = form.querySelectorAll('input[type="email"]');
        emailFields.forEach(field => {
            if (field.value && !isValidEmail(field.value)) {
                isValid = false;
                field.classList.add('error');
                showToast('Invalid email format', 'error');
            } else {
                field.classList.remove('error');
            }
        });
        
        if (!isValid) {
            e.preventDefault();
        }
    });
}

// ============================================================================
// DOM Ready
// ============================================================================

document.addEventListener('DOMContentLoaded', function() {
    // Auto-dismiss flash messages after 5 seconds
    const flashMessages = document.querySelectorAll('.flash-messages .alert');
    flashMessages.forEach(message => {
        setTimeout(() => {
            message.remove();
        }, 5000);
    });
    
    // Add form validation to all forms
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        // Skip forms with novalidate attribute
        if (!form.hasAttribute('novalidate')) {
            addFormValidation(form);
        }
    });
});

