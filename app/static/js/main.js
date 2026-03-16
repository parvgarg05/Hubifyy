/**
 * Hubify - Main JavaScript functionality
 * Handles authentication, API calls, and dynamic interactions
 */

// ========== Token Management ==========

/**
 * Store JWT token in localStorage
 * @param {string} token - JWT access token
 */
function storeToken(token) {
    localStorage.setItem('access_token', token);
}

/**
 * Retrieve JWT token from localStorage
 * @returns {string|null} - JWT token or null
 */
function getToken() {
    return localStorage.getItem('access_token');
}

/**
 * Check if user is authenticated
 * @returns {boolean} - True if token exists
 */
function isAuthenticated() {
    return getToken() !== null;
}

/**
 * Clear JWT token (logout)
 */
function clearToken() {
    localStorage.removeItem('access_token');
    window.location.href = '/';
}

// ========== Authentication Functions ==========

/**
 * Login user and store JWT token
 * @param {Event} event - Form submission event
 */
async function loginUser(event) {
    event.preventDefault();

    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    try {
        const response = await fetch('/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email: email,
                password: password
            })
        });

        if (!response.ok) {
            const error = await response.json();
            showAlert('Login failed: ' + (error.detail || 'Invalid credentials'), 'danger');
            return;
        }

        const data = await response.json();
        
        // Store token
        storeToken(data.access_token);
        
        // Show success message
        showAlert('Login successful! Redirecting...', 'success');
        
        // Redirect based on role
        setTimeout(() => {
            if (data.role === 'admin') {
                window.location.href = '/dashboard';
            } else {
                window.location.href = '/dashboard';
            }
        }, 1500);

    } catch (error) {
        console.error('Login error:', error);
        showAlert('Network error. Please try again.', 'danger');
    }
}

/**
 * Register new user
 * @param {Event} event - Form submission event
 */
async function registerUser(event) {
    event.preventDefault();

    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const full_name = document.getElementById('full_name').value;

    try {
        const response = await fetch('/auth/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email: email,
                password: password,
                full_name: full_name
            })
        });

        if (!response.ok) {
            const error = await response.json();
            showAlert('Registration failed: ' + (error.detail || 'Please try again'), 'danger');
            return;
        }

        const data = await response.json();
        
        // Show success message
        showAlert('Registration successful! Redirecting to login...', 'success');
        
        // Redirect to login
        setTimeout(() => {
            window.location.href = '/login';
        }, 1500);

    } catch (error) {
        console.error('Registration error:', error);
        showAlert('Network error. Please try again.', 'danger');
    }
}

// ========== Generic API Functions ==========

/**
 * Fetch data from API with automatic JWT header
 * @param {string} url - API endpoint URL
 * @param {string} method - HTTP method (GET, POST, etc.)
 * @param {object} data - Optional request body
 * @returns {Promise<object>} - Parsed response data
 */
async function fetchData(url, method = 'GET', data = null) {
    const headers = {
        'Content-Type': 'application/json',
    };

    // Add JWT token to header if authenticated
    const token = getToken();
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    const options = {
        method: method,
        headers: headers,
    };

    if (data && (method === 'POST' || method === 'PUT' || method === 'PATCH')) {
        options.body = JSON.stringify(data);
    }

    try {
        const response = await fetch(url, options);

        // Handle 401 Unauthorized
        if (response.status === 401) {
            console.warn('Unauthorized access. Redirecting to login.');
            clearToken();
            window.location.href = '/login';
            return null;
        }

        if (!response.ok) {
            const error = await response.json();
            console.error('API Error:', error);
            throw new Error(error.detail || `API Error: ${response.status}`);
        }

        const responseData = await response.json();
        return responseData;

    } catch (error) {
        console.error('Fetch error:', error);
        showAlert('Error: ' + error.message, 'danger');
        return null;
    }
}

/**
 * Register for an event
 * @param {number} eventId - Event ID
 */
async function registerForEvent(eventId) {
    if (!isAuthenticated()) {
        showAlert('Please login to register for events', 'warning');
        window.location.href = '/login';
        return;
    }

    try {
        const response = await fetchData(`/events/${eventId}/register`, 'POST');
        
        if (response) {
            showAlert(response.message, 'success');
            // Optionally refresh the page or update UI
            setTimeout(() => {
                location.reload();
            }, 1500);
        }
    } catch (error) {
        console.error('Registration error:', error);
    }
}

/**
 * Create a club (Admin only)
 * @param {Event} event - Form submission event
 */
async function createClub(event) {
    event.preventDefault();

    const name = document.getElementById('club_name').value;
    const description = document.getElementById('club_description').value;
    const logo_url = document.getElementById('club_logo').value;

    const clubData = {
        name: name,
        description: description,
        logo_url: logo_url
    };

    try {
        const response = await fetchData('/clubs', 'POST', clubData);
        
        if (response) {
            showAlert('Club created successfully!', 'success');
            setTimeout(() => {
                window.location.href = '/clubs/' + response.id;
            }, 1500);
        }
    } catch (error) {
        console.error('Club creation error:', error);
    }
}

/**
 * Create an event (Admin only)
 * @param {Event} event - Form submission event
 */
async function createEvent(event) {
    event.preventDefault();

    const title = document.getElementById('event_title').value;
    const description = document.getElementById('event_description').value;
    const date_time = document.getElementById('event_datetime').value;
    const location = document.getElementById('event_location').value;
    const club_id = document.getElementById('club_id').value;

    const eventData = {
        title: title,
        description: description,
        date_time: date_time,
        location: location,
        club_id: parseInt(club_id)
    };

    try {
        const response = await fetchData('/events', 'POST', eventData);
        
        if (response) {
            showAlert('Event created successfully!', 'success');
            setTimeout(() => {
                window.location.href = '/events/' + response.id;
            }, 1500);
        }
    } catch (error) {
        console.error('Event creation error:', error);
    }
}

// ========== UI Helper Functions ==========

/**
 * Show alert/notification message
 * @param {string} message - Alert message
 * @param {string} type - Alert type (success, danger, warning, info)
 */
function showAlert(message, type = 'info') {
    const alertContainer = document.getElementById('alert-container');
    
    if (!alertContainer) {
        console.warn('Alert container not found');
        return;
    }

    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.innerHTML = `
        <strong>${type.charAt(0).toUpperCase() + type.slice(1)}:</strong> ${message}
        <button type="button" class="alert-close" onclick="this.parentElement.remove();">&times;</button>
    `;

    alertContainer.appendChild(alert);

    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (alert.parentElement) {
            alert.remove();
        }
    }, 5000);
}

/**
 * Format date to readable format
 * @param {string} dateString - ISO date string
 * @returns {string} - Formatted date
 */
function formatDate(dateString) {
    const options = {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    return new Date(dateString).toLocaleDateString('en-US', options);
}

/**
 * Truncate text to specified length
 * @param {string} text - Text to truncate
 * @param {number} length - Max length
 * @returns {string} - Truncated text with ellipsis
 */
function truncateText(text, length = 100) {
    if (text.length > length) {
        return text.substring(0, length) + '...';
    }
    return text;
}

// ========== Page Initialization ==========

/**
 * Initialize page - run on document ready
 */
document.addEventListener('DOMContentLoaded', function() {
    // Add any page-specific initialization here
    console.log('Hubify loaded');
});

// ========== Alert Container Styles ==========

const styleSheet = document.createElement('style');
styleSheet.textContent = `
    .alert-close {
        float: right;
        font-size: 1.5rem;
        font-weight: 700;
        background: none;
        border: none;
        cursor: pointer;
        opacity: 0.7;
        padding: 0;
        margin-left: var(--spacing-md);
    }
    
    .alert-close:hover {
        opacity: 1;
    }

    #alert-container {
        position: fixed;
        top: 80px;
        right: 20px;
        z-index: 999;
        max-width: 400px;
        width: 90%;
    }
`;
document.head.appendChild(styleSheet);
