// SAS Agent Frontend JavaScript
// Complete API interactions and utilities

/**
 * Show status message to user
 * @param {string} message - Message to display
 * @param {string} type - 'info', 'success', 'error', 'warning'
 */
function showStatus(message, type = 'info') {
    const statusEl = document.getElementById('status-message');
    if (!statusEl) return;
    
    statusEl.textContent = message;
    statusEl.className = `status-message ${type}`;
    statusEl.style.display = 'block';
    
    // Auto-hide success messages after 3 seconds
    if (type === 'success') {
        setTimeout(() => {
            statusEl.style.display = 'none';
        }, 3000);
    }
}

/**
 * Hide status message
 */
function hideStatus() {
    const statusEl = document.getElementById('status-message');
    if (statusEl) {
        statusEl.style.display = 'none';
    }
}

/**
 * Make API request with error handling
 * @param {string} url - API endpoint
 * @param {object} options - Fetch options
 * @returns {Promise} - Response promise
 */
async function apiRequest(url, options = {}) {
    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        return response;
    } catch (error) {
        console.error('API Request failed:', error);
        throw new Error('Network error: ' + error.message);
    }
}

/**
 * Test backend connectivity
 * @returns {Promise<boolean>} - True if backend is accessible
 */
async function testBackendConnection() {
    try {
        const response = await fetch('/hello');
        return response.ok;
    } catch (error) {
        console.error('Backend connection test failed:', error);
        return false;
    }
}

/**
 * Create a new agent
 * @param {object} agentData - Agent information {name, description}
 * @returns {Promise<object>} - Created agent data
 */
async function createAgent(agentData) {
    const response = await apiRequest('/api/create-agent', {
        method: 'POST',
        body: JSON.stringify(agentData)
    });
    
    if (!response.ok) {
        const error = await response.text();
        throw new Error(error || 'Failed to create agent');
    }
    
    return await response.json();
}

/**
 * Get list of agents
 * @returns {Promise<Array>} - List of agents
 */
async function getAgents() {
    try {
        const response = await apiRequest('/api/agents');
        
        if (response.ok) {
            return await response.json();
        } else {
            // Return demo data if endpoint not implemented
            console.log('/agents endpoint not available, using demo data');
            return [
                { id: 1, name: "Demo Agent", description: "Test agent for development" }
            ];
        }
    } catch (error) {
        console.log('Using demo agents due to error:', error.message);
        return [
            { id: 1, name: "Demo Agent", description: "Test agent for development" }
        ];
    }
}

/**
 * Upload document for an agent
 * @param {number} agentId - Agent ID
 * @param {File} file - File to upload
 * @returns {Promise<object>} - Upload result
 */
async function uploadDocument(agentId, file) {
    const formData = new FormData();
    formData.append('agent_id', agentId);
    formData.append('file', file);
    
    const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData
    });
    
    if (!response.ok) {
        const error = await response.text();
        throw new Error(error || 'Failed to upload document');
    }
    
    return await response.text();
}

/**
 * Send chat message to agent
 * @param {number} agentId - Agent ID
 * @param {string} message - User message
 * @returns {Promise<object>} - Agent response
 */
async function sendChatMessage(agentId, message) {
    const response = await apiRequest('/api/chat', {
        method: 'POST',
        body: JSON.stringify({
            agent_id: agentId.toString(),
            query: message
        })
    });
    
    if (!response.ok) {
        const error = await response.json().catch(() => ({ error: 'Unknown error' }));
        throw new Error(error.error || 'Failed to get response');
    }
    
    return await response.json();
}

/**
 * Format file size for display
 * @param {number} bytes - File size in bytes
 * @returns {string} - Formatted size string
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * Validate file type
 * @param {File} file - File to validate
 * @returns {boolean} - True if file type is supported
 */
function isValidFileType(file) {
    const validTypes = ['.txt', '.pdf', '.md'];
    const fileName = file.name.toLowerCase();
    return validTypes.some(ext => fileName.endsWith(ext));
}

/**
 * Initialize drag and drop for file uploads
 * @param {HTMLElement} dropArea - Drop area element
 * @param {Function} onFileDrop - Callback when files are dropped
 */
function initializeDragAndDrop(dropArea, onFileDrop) {
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, preventDefaults, false);
    });
    
    ['dragenter', 'dragover'].forEach(eventName => {
        dropArea.addEventListener(eventName, highlight, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, unhighlight, false);
    });
    
    dropArea.addEventListener('drop', handleDrop, false);
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    function highlight(e) {
        dropArea.classList.add('highlight');
    }
    
    function unhighlight(e) {
        dropArea.classList.remove('highlight');
    }
    
    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        onFileDrop(files);
    }
}

/**
 * Escape HTML to prevent XSS
 * @param {string} text - Text to escape
 * @returns {string} - Escaped text
 */
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, function(m) { return map[m]; });
}

/**
 * Format timestamp for display
 * @param {Date|string} timestamp - Timestamp to format
 * @returns {string} - Formatted time string
 */
function formatTimestamp(timestamp) {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffMins < 1440) return `${Math.floor(diffMins / 60)}h ago`;
    
    return date.toLocaleDateString();
}

/**
 * Copy text to clipboard
 * @param {string} text - Text to copy
 * @returns {Promise<boolean>} - True if successful
 */
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        return true;
    } catch (error) {
        console.error('Failed to copy text:', error);
        return false;
    }
}

/**
 * Debounce function calls
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in milliseconds
 * @returns {Function} - Debounced function
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

/**
 * Smooth scroll to element
 * @param {HTMLElement} element - Element to scroll to
 * @param {number} duration - Animation duration in ms
 */
function smoothScrollTo(element, duration = 300) {
    element.scrollIntoView({
        behavior: 'smooth',
        block: 'center'
    });
}

/**
 * Generate unique ID
 * @returns {string} - Unique identifier
 */
function generateId() {
    return 'id_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now();
}

/**
 * Validate email format
 * @param {string} email - Email to validate
 * @returns {boolean} - True if valid email format
 */
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

/**
 * Format message content for display
 * @param {string} content - Raw message content
 * @returns {string} - Formatted HTML content
 */
function formatMessageContent(content) {
    // Convert newlines to <br>
    content = content.replace(/\n/g, '<br>');
    
    // Convert URLs to links
    const urlRegex = /(https?:\/\/[^\s]+)/g;
    content = content.replace(urlRegex, '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>');
    
    // Convert **bold** to <strong>
    content = content.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // Convert *italic* to <em>
    content = content.replace(/\*(.*?)\*/g, '<em>$1</em>');
    
    // Convert `code` to <code>
    content = content.replace(/`(.*?)`/g, '<code>$1</code>');
    
    return content;
}

/**
 * Get file extension
 * @param {string} filename - File name
 * @returns {string} - File extension
 */
function getFileExtension(filename) {
    return filename.split('.').pop().toLowerCase();
}

/**
 * Check if file is image
 * @param {File} file - File to check
 * @returns {boolean} - True if file is image
 */
function isImageFile(file) {
    const imageTypes = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'];
    const extension = getFileExtension(file.name);
    return imageTypes.includes(extension);
}

/**
 * Truncate text to specified length
 * @param {string} text - Text to truncate
 * @param {number} maxLength - Maximum length
 * @returns {string} - Truncated text
 */
function truncateText(text, maxLength) {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength - 3) + '...';
}

/**
 * Parse query parameters from URL
 * @returns {object} - Object with query parameters
 */
function getQueryParams() {
    const params = {};
    const urlParams = new URLSearchParams(window.location.search);
    for (const [key, value] of urlParams) {
        params[key] = value;
    }
    return params;
}

/**
 * Update URL without page reload
 * @param {string} url - New URL
 */
function updateURL(url) {
    window.history.pushState(null, null, url);
}

/**
 * Check if element is in viewport
 * @param {HTMLElement} element - Element to check
 * @returns {boolean} - True if element is visible
 */
function isInViewport(element) {
    const rect = element.getBoundingClientRect();
    return (
        rect.top >= 0 &&
        rect.left >= 0 &&
        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
        rect.right <= (window.innerWidth || document.documentElement.clientWidth)
    );
}

/**
 * Create loading spinner element
 * @param {string} message - Loading message
 * @returns {HTMLElement} - Loading element
 */
function createLoader(message = 'Loading...') {
    const loader = document.createElement('div');
    loader.className = 'loader';
    loader.innerHTML = `
        <div class="spinner"></div>
        <div class="loading-text">${message}</div>
    `;
    return loader;
}

/**
 * Show loading overlay
 * @param {string} message - Loading message
 */
function showLoadingOverlay(message = 'Processing...') {
    let overlay = document.getElementById('loading-overlay');
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.id = 'loading-overlay';
        overlay.className = 'loading-overlay';
        document.body.appendChild(overlay);
    }
    
    overlay.innerHTML = `
        <div class="loading-content">
            <div class="spinner"></div>
            <div class="loading-message">${message}</div>
        </div>
    `;
    overlay.style.display = 'flex';
}

/**
 * Hide loading overlay
 */
function hideLoadingOverlay() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.style.display = 'none';
    }
}

/**
 * Save data to localStorage
 * @param {string} key - Storage key
 * @param {any} data - Data to store
 */
function saveToStorage(key, data) {
    try {
        localStorage.setItem(key, JSON.stringify(data));
    } catch (error) {
        console.error('Failed to save to localStorage:', error);
    }
}

/**
 * Load data from localStorage
 * @param {string} key - Storage key
 * @param {any} defaultValue - Default value if not found
 * @returns {any} - Stored data or default value
 */
function loadFromStorage(key, defaultValue = null) {
    try {
        const item = localStorage.getItem(key);
        return item ? JSON.parse(item) : defaultValue;
    } catch (error) {
        console.error('Failed to load from localStorage:', error);
        return defaultValue;
    }
}

/**
 * Remove data from localStorage
 * @param {string} key - Storage key
 */
function removeFromStorage(key) {
    try {
        localStorage.removeItem(key);
    } catch (error) {
        console.error('Failed to remove from localStorage:', error);
    }
}

/**
 * Initialize common event listeners
 */
document.addEventListener('DOMContentLoaded', function() {
    // Close status messages when clicked
    document.addEventListener('click', function(e) {
        if (e.target.matches('.status-message')) {
            hideStatus();
        }
    });
    
    // Handle keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Escape key closes modals/overlays
        if (e.key === 'Escape') {
            const uploadSection = document.getElementById('upload-section');
            if (uploadSection && uploadSection.style.display !== 'none') {
                uploadSection.style.display = 'none';
            }
            
            hideLoadingOverlay();
        }
        
        // Ctrl/Cmd + Enter in textareas submits forms
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            const activeElement = document.activeElement;
            if (activeElement.tagName === 'TEXTAREA' || activeElement.tagName === 'INPUT') {
                const form = activeElement.closest('form');
                if (form) {
                    e.preventDefault();
                    form.dispatchEvent(new Event('submit'));
                }
            }
        }
    });
    
    // Auto-resize textareas
    document.addEventListener('input', function(e) {
        if (e.target.tagName === 'TEXTAREA' && e.target.classList.contains('auto-resize')) {
            e.target.style.height = 'auto';
            e.target.style.height = e.target.scrollHeight + 'px';
        }
    });
    
    // Initialize drag and drop for file upload areas
    const fileUploadAreas = document.querySelectorAll('.file-upload-label, .file-upload-area');
    fileUploadAreas.forEach(area => {
        initializeDragAndDrop(area, handleFilesDrop);
    });
});

/**
 * Handle dropped files
 * @param {FileList} files - Dropped files
 */
function handleFilesDrop(files) {
    const fileInput = document.querySelector('input[type="file"]');
    if (fileInput && files.length > 0) {
        // Create a new FileList-like object
        const dt = new DataTransfer();
        for (let i = 0; i < files.length; i++) {
            if (isValidFileType(files[i])) {
                dt.items.add(files[i]);
            }
        }
        fileInput.files = dt.files;
        
        // Trigger change event
        fileInput.dispatchEvent(new Event('change'));
    }
}

/**
 * Format bytes to human readable format
 * @param {number} bytes - Bytes to format
 * @param {number} decimals - Number of decimals
 * @returns {string} - Formatted string
 */
function formatBytes(bytes, decimals = 2) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
    
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

/**
 * Check if device is mobile
 * @returns {boolean} - True if mobile device
 */
function isMobile() {
    return window.innerWidth <= 768 || /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
}

/**
 * Get current theme preference
 * @returns {string} - 'light' or 'dark'
 */
function getThemePreference() {
    return loadFromStorage('theme', 'light');
}

/**
 * Set theme preference
 * @param {string} theme - 'light' or 'dark'
 */
function setThemePreference(theme) {
    saveToStorage('theme', theme);
    document.body.setAttribute('data-theme', theme);
}

// Export functions for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        showStatus,
        hideStatus,
        apiRequest,
        testBackendConnection,
        createAgent,
        getAgents,
        uploadDocument,
        sendChatMessage,
        formatFileSize,
        isValidFileType,
        initializeDragAndDrop,
        escapeHtml,
        formatTimestamp,
        copyToClipboard,
        debounce,
        smoothScrollTo,
        generateId,
        isValidEmail,
        formatMessageContent,
        getFileExtension,
        isImageFile,
        truncateText,
        getQueryParams,
        updateURL,
        isInViewport,
        createLoader,
        showLoadingOverlay,
        hideLoadingOverlay,
        saveToStorage,
        loadFromStorage,
        removeFromStorage,
        formatBytes,
        isMobile,
        getThemePreference,
        setThemePreference
    };
}