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
function logout(reason) {
    // Clear all auth data
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    localStorage.removeItem('id_token');
    
    // Redirect to home with message
    if (reason) {
        window.location.href = '/?logout=' + encodeURIComponent(reason);
    } else {
        window.location.href = '/';
    }
}

// Handle callback - extract token from URL hash
function handleCallback() {
    const hash = window.location.hash;
    if (!hash) return null;
    
    const params = new URLSearchParams(hash.substring(1));
    
    // Check for Auth0 error
    const error = params.get('error');
    const errorDesc = params.get('error_description');
    if (error) {
        console.error('Auth0 error:', error, errorDesc);
        alert('Erro no login: ' + (errorDesc || error));
        window.location.href = '/';
        return null;
    }
    
    const accessToken = params.get('access_token');
    const idToken = params.get('id_token');
    
    if (!accessToken) {
        console.error('No access token in callback');
        return null;
    }
    
    localStorage.setItem('access_token', accessToken);
    
    if (idToken) {
        localStorage.setItem('id_token', idToken);
    }
    
    // Fetch user info from Auth0 /userinfo endpoint
    if (accessToken) {
        try {
            const resp = await fetch('https://' + AUTH0_DOMAIN + '/userinfo', {
                headers: { 'Authorization': 'Bearer ' + accessToken }
            });
            if (resp.ok) {
                const userInfo = await resp.json();
                localStorage.setItem('user', JSON.stringify({
                    name: userInfo.name || userInfo.email,
                    email: userInfo.email,
                    picture: userInfo.picture || null
                }));
            }
        } catch(e) {
            console.error('Failed to fetch user info:', e);
        }
    }
    
    // Clear hash
    window.history.replaceState(null, '', window.location.pathname);
    return accessToken;
}

// Note: apiRequest is deprecated - use fetch with Authorization header directly

// Render user menu in header
function renderUserMenu() {
    const user = getUser();
    const container = document.getElementById('user-menu');
    if (!container) return;
    
    if (isAuthenticated()) {
        const name = (user && (user.name || user.email)) || 'Usuário';
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
