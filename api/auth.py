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

def verify_token(token):
    """Verify JWT token by calling Auth0's userinfo endpoint."""
    print(f'[AUTH] Verifying token: {token[:30]}...')
    
    try:
        # Auth0's userinfo endpoint validates the token
        # If token is valid, returns user info
        # If invalid, returns 401
        resp = requests.get(
            f'https://{AUTH0_DOMAIN}/userinfo',
            headers={'Authorization': f'Bearer {token}'},
            timeout=10
        )
        
        if resp.status_code == 200:
            payload = resp.json()
            print(f'[AUTH] Token valid, user: {payload.get("sub")}')
            return payload
        else:
            print(f'[AUTH] Token invalid: {resp.status_code}')
            return None
    except Exception as e:
        print(f'[AUTH] Verification error: {e}')
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
