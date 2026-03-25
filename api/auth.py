# Auth0 JWT Authentication - Simplified
# RGVL Project

import os
import functools
import requests
from flask import request, jsonify, g

AUTH0_DOMAIN = os.getenv('AUTH0_DOMAIN', 'dev-4mhbzq6x4yvyckmt.us.auth0.com')
AUTH0_AUDIENCE = os.getenv('AUTH0_AUDIENCE', 'http://localhost:5003')

def get_token_from_header():
    """Extract Bearer token from Authorization header"""
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        return auth_header[7:]
    return None

# Cache for verified tokens (token -> payload, expires in 5 min)
_token_cache = {}
_cache_times = {}

# Allowed emails/domains for access (comma-separated in AUTH_ALLOWED_USERS env var)
def is_user_allowed(payload):
    import os
    email = payload.get('email', '')
    if not email:
        sub = payload.get('sub', '')
        if sub and '|' in sub:
            email = sub.split('|')[-1] + '@placeholder.com'
    
    allowlist = os.getenv('AUTH_ALLOWED_USERS', '')
    if not allowlist:
        return True
    
    for allowed in allowlist.split(','):
        allowed = allowed.strip()
        if not allowed:
            continue
        if '@' in allowed:
            if email.lower() == allowed.lower():
                return True
        else:
            if email.lower().endswith('@' + allowed.lower()):
                return True
    return False

def verify_token(token):
    """Verify JWT token by calling Auth0's userinfo endpoint (with caching)."""
    import time
    
    # Check cache first (valid for 5 minutes)
    if token in _token_cache:
        cache_time = _cache_times.get(token, 0)
        if time.time() - cache_time < 300:
            pass  # cached
            return _token_cache[token]
        else:
            # Expired
            del _token_cache[token]
            del _cache_times[token]
    
    pass  # verifying
    
    try:
        resp = requests.get(
            f'https://{AUTH0_DOMAIN}/userinfo',
            headers={'Authorization': f'Bearer {token}'},
            timeout=10
        )
        
        if resp.status_code == 200:
            payload = resp.json()
            # Cache the result
            _token_cache[token] = payload
            _cache_times[token] = time.time()
            pass  # valid
            return payload
        else:
            pass  # invalid
            return None
    except Exception as e:
        pass  # error
        return None

def require_auth(f):
    """Decorator to require authentication on endpoints"""
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_from_header()
        
        if not token:
            print('[AUTH] No token provided')
            return jsonify({'error': 'Authorization required'}), 401
        
        payload = verify_token(token)
        
        if not payload:
            print('[AUTH] Token verification failed')
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        # Store user info in Flask's g object
        g.user = payload
        return f(*args, **kwargs)
    return decorated

def optional_auth(f):
    """Decorator for optional authentication - continues even if no token"""
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_from_header()
        
        if token:
            payload = verify_token(token)
            g.user = payload if payload else None
        else:
            g.user = None
        
        return f(*args, **kwargs)
    return decorated
