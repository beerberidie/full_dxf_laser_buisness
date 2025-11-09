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
// Sidebar Navigation
// ============================================================================

/**
 * Toggle expandable sidebar section
 * @param {HTMLElement} element - The parent element that was clicked
 */
function toggleSidebarSection(element) {
    const section = element.closest('.sidebar-expandable');
    if (section) {
        section.classList.toggle('expanded');

        // Save state to localStorage
        const sectionId = element.querySelector('.sidebar-text').textContent.trim();
        const isExpanded = section.classList.contains('expanded');
        localStorage.setItem(`sidebar-section-${sectionId}`, isExpanded);
    }
}

/**
 * Initialize sidebar toggle functionality
 */
function initSidebar() {
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');
    const body = document.body;

    if (!sidebarToggle || !sidebar) return;

    // Load saved sidebar state from localStorage
    const savedState = localStorage.getItem('sidebarCollapsed');
    if (savedState === 'true') {
        body.classList.add('sidebar-collapsed');
    }

    // Check if mobile
    const isMobile = () => window.innerWidth <= 768;

    // Toggle sidebar
    sidebarToggle.addEventListener('click', function() {
        if (isMobile()) {
            // On mobile, toggle sidebar-open class
            body.classList.toggle('sidebar-open');
        } else {
            // On desktop, toggle sidebar-collapsed class
            body.classList.toggle('sidebar-collapsed');

            // Save state to localStorage
            const isCollapsed = body.classList.contains('sidebar-collapsed');
            localStorage.setItem('sidebarCollapsed', isCollapsed);
        }
    });

    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', function(e) {
        if (isMobile() && body.classList.contains('sidebar-open')) {
            if (!sidebar.contains(e.target) && !sidebarToggle.contains(e.target)) {
                body.classList.remove('sidebar-open');
            }
        }
    });

    // Handle window resize
    let resizeTimer;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(function() {
            if (!isMobile()) {
                // Remove mobile-specific class when resizing to desktop
                body.classList.remove('sidebar-open');
            }
        }, 250);
    });
}

// ============================================================================
// File Upload Utilities
// ============================================================================

/**
 * Update file count display when files are selected
 * @param {HTMLInputElement} input - File input element
 * @param {string} countElementId - ID of element to display count
 */
function updateFileCount(input, countElementId) {
    const countElement = document.getElementById(countElementId);
    if (!countElement) return;

    const fileCount = input.files.length;

    if (fileCount === 0) {
        countElement.style.display = 'none';
        countElement.textContent = '';
    } else if (fileCount === 1) {
        countElement.style.display = 'block';
        countElement.textContent = `📎 1 file selected: ${input.files[0].name}`;
    } else {
        countElement.style.display = 'block';

        // Calculate total size
        let totalSize = 0;
        for (let i = 0; i < input.files.length; i++) {
            totalSize += input.files[i].size;
        }

        countElement.textContent = `📎 ${fileCount} files selected (Total: ${formatFileSize(totalSize)})`;
    }
}

/**
 * Validate file upload before submission
 * @param {HTMLInputElement} input - File input element
 * @param {number} maxSizeMB - Maximum file size in MB (default: 50)
 * @param {Array} allowedExtensions - Array of allowed extensions (e.g., ['.pdf', '.jpg'])
 * @returns {Object} Validation result with {valid: boolean, errors: Array}
 */
function validateFileUpload(input, maxSizeMB = 50, allowedExtensions = null) {
    const errors = [];
    const files = input.files;

    if (files.length === 0) {
        errors.push('No files selected');
        return { valid: false, errors };
    }

    const maxSizeBytes = maxSizeMB * 1024 * 1024;

    for (let i = 0; i < files.length; i++) {
        const file = files[i];

        // Check file size
        if (file.size > maxSizeBytes) {
            errors.push(`${file.name}: File too large (${formatFileSize(file.size)}). Maximum: ${maxSizeMB} MB`);
        }

        // Check file extension if specified
        if (allowedExtensions && allowedExtensions.length > 0) {
            const fileName = file.name.toLowerCase();
            const hasValidExtension = allowedExtensions.some(ext =>
                fileName.endsWith(ext.toLowerCase())
            );

            if (!hasValidExtension) {
                errors.push(`${file.name}: Invalid file type. Allowed: ${allowedExtensions.join(', ')}`);
            }
        }
    }

    return {
        valid: errors.length === 0,
        errors: errors
    };
}

/**
 * Show file upload progress (for future AJAX uploads)
 * @param {number} percent - Upload progress percentage (0-100)
 * @param {string} progressElementId - ID of progress element
 */
function updateUploadProgress(percent, progressElementId) {
    const progressElement = document.getElementById(progressElementId);
    if (!progressElement) return;

    progressElement.style.display = 'block';
    progressElement.innerHTML = `
        <div class="progress">
            <div class="progress-bar" role="progressbar" style="width: ${percent}%"
                 aria-valuenow="${percent}" aria-valuemin="0" aria-valuemax="100">
                ${percent}%
            </div>
        </div>
    `;

    if (percent >= 100) {
        setTimeout(() => {
            progressElement.style.display = 'none';
        }, 2000);
    }
}

// ============================================================================
// DOM Ready
// ============================================================================

document.addEventListener('DOMContentLoaded', function() {
    // Initialize sidebar
    initSidebar();

    // Restore expandable section states from localStorage
    document.querySelectorAll('.sidebar-expandable').forEach(section => {
        const parentElement = section.querySelector('.sidebar-parent .sidebar-text');
        if (parentElement) {
            const sectionId = parentElement.textContent.trim();
            const savedState = localStorage.getItem(`sidebar-section-${sectionId}`);

            // If no saved state, check if section should be expanded based on active page
            if (savedState === null) {
                // Section will use the 'expanded' class from template if on active page
            } else if (savedState === 'true') {
                section.classList.add('expanded');
            } else {
                section.classList.remove('expanded');
            }
        }
    });

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

