// Auth0 Authentication Helper
// RGVL Project

const AUTH0_DOMAIN = 'dev-4mhbzq6x4yvyckmt.us.auth0.com';
const AUTH0_CLIENT_ID = '8DwXpULitPs2L1CyT4QKRdLMAOZ3mXJi';
const AUTH0_AUDIENCE = 'http://localhost:5003';
const CALLBACK_URL = window.location.origin + '/callback';

// Check if authenticated
function isAuthenticated() {
    return !!localStorage.getItem('access_token');
}

// Get user info from localStorage
function getUser() {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
}

// Login - redirect to Auth0
function login() {
    const authUrl = `https://${AUTH0_DOMAIN}/authorize?` + 
        `response_type=token&` +
        `client_id=${AUTH0_CLIENT_ID}&` +
        `redirect_uri=${encodeURIComponent(CALLBACK_URL)}&` +
        `scope=openid profile email`;
    window.location.href = authUrl;
}

// Logout - clear local storage and redirect
function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    localStorage.removeItem('id_token');
    
    const logoutUrl = `https://${AUTH0_DOMAIN}/v2/logout?` +
        `client_id=${AUTH0_CLIENT_ID}&` +
        `returnTo=${encodeURIComponent(window.location.origin)}`;
    window.location.href = logoutUrl;
}

// Handle callback - extract token from URL hash
function handleCallback() {
    const hash = window.location.hash;
    if (!hash || hash.indexOf('access_token=') === -1) {
        return null;
    }
    
    const params = new URLSearchParams(hash.substring(1));
    const accessToken = params.get('access_token');
    const idToken = params.get('id_token');
    
    if (accessToken) {
        localStorage.setItem('access_token', accessToken);
    }
    if (idToken) {
        localStorage.setItem('id_token', idToken);
        // Decode user info from JWT payload
        try {
            const payload = JSON.parse(atob(idToken.split('.')[1]));
            const user = {
                name: payload.name || payload.email,
                email: payload.email,
                picture: payload.picture || null
            };
            localStorage.setItem('user', JSON.stringify(user));
        } catch(e) {
            console.error('Failed to decode user:', e);
        }
    }
    
    // Clear hash
    window.history.replaceState(null, '', window.location.pathname);
    return accessToken;
}

// API request with Bearer token
async function apiRequest(endpoint, options = {}) {
    const token = localStorage.getItem('access_token');
    
    if (!token) {
        login();
        return null;
    }
    
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };
    
    // Add Authorization header if we have a token
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    
    try {
        const resp = await fetch(endpoint, {
            ...options,
            headers
        });
        
        if (resp.status === 401) {
            // Token expired or invalid
            logout();
            return null;
        }
        
        return resp;
    } catch(e) {
        console.error('API request failed:', e);
        return null;
    }
}

// Render user menu in header
function renderUserMenu() {
    const user = getUser();
    const container = document.getElementById('user-menu');
    if (!container) return;
    
    if (isAuthenticated() && user) {
        const name = user.name || user.email || 'User';
        const initials = name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase();
        container.innerHTML = `
            <div class="user-menu">
                <span class="user-name">${escapeHtml(name)}</span>
                <button class="btn-logout" onclick="logout()">Sair</button>
            </div>
        `;
    } else {
        container.innerHTML = `
            <button class="btn-login" onclick="login()">🔐 Login</button>
        `;
    }
}

// Escape HTML to prevent XSS
function escapeHtml(s) {
    if (!s) return '';
    return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}
