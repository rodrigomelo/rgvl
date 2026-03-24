# Auth0 JWT Authentication
# RGVL Project

import os
import functools
import requests
from flask import request, jsonify, g

AUTH0_DOMAIN = os.getenv('AUTH0_DOMAIN', 'dev-4mhbzq6x4yvyckmt.us.auth0.com')
AUTH0_AUDIENCE = os.getenv('AUTH0_AUDIENCE', 'http://localhost:5003')

# Cache for Auth0 public keys
_auth0_jwks_cache = None
_jwks_cache_time = 0

def get_auth0_public_key(token):
    """Get the public key from Auth0 for token verification using OIDC metadata."""
    import jwt
    
    global _auth0_jwks_cache, _jwks_cache_time
    
    import time
    now = time.time()
    
    # Cache keys for 1 hour
    if _auth0_jwks_cache is None or (now - _jwks_cache_time) > 3600:
        # Get the OIDC metadata which contains the JWKS
        oidc_url = f'https://{AUTH0_DOMAIN}/.well-known/openid-configuration'
        try:
            oidc_config = requests.get(oidc_url, timeout=10).json()
            jwks_uri = oidc_config.get('jwks_uri')
            if jwks_uri:
                _auth0_jwks_cache = requests.get(jwks_uri, timeout=10).json()
                _jwks_cache_time = now
                print(f'[AUTH] Fetched JWKS from {jwks_uri}')
        except Exception as e:
            print(f'[AUTH] Failed to fetch JWKS: {e}')
            return None
    
    if not _auth0_jwks_cache:
        return None
    
    # Decode header to get kid
    try:
        unverified_header = jwt.decode(token, options={"verify_signature": False})
    except Exception as e:
        print(f'[AUTH] Failed to decode token header: {e}')
        return None
    
    # Get the kid from the header
    header_b64 = token.split('.')[0]
    import base64
    padding = 4 - len(header_b64) % 4
    if padding != 4:
        header_b64 += '=' * padding
    header = jwt.get_unverified_header(token)
    kid = header.get('kid')
    
    print(f'[AUTH] Token header kid: {kid}')
    
    # Find matching key in JWKS
    keys = _auth0_jwks_cache.get('keys', [])
    for key_data in keys:
        if key_data.get('kid') == kid or kid is None:
            # Construct the public key from JWK
            from cryptography.hazmat.primitives import serialization
            from cryptography.hazmat.primitives.asymmetric import rsa
            from cryptography.hazmat.backends import default_backend
            
            # Convert JWK to PEM
            n = int.from_bytes(base64.urlsafe_b64decode(key_data['n'] + '=='), 'big')
            e = int.from_bytes(base64.urlsafe_b64decode(key_data['e'] + '=='), 'big')
            
            public_key = rsa.RSAPublicNumbers(e, n).public_key(default_backend())
            pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            return pem
    
    # If no kid match, try first RSA key anyway (for tokens without kid)
    for key_data in keys:
        if key_data.get('kty') == 'RSA':
            from cryptography.hazmat.primitives import serialization
            from cryptography.hazmat.primitives.asymmetric import rsa
            from cryptography.hazmat.backends import default_backend
            
            n = int.from_bytes(base64.urlsafe_b64decode(key_data['n'] + '=='), 'big')
            e = int.from_bytes(base64.urlsafe_b64decode(key_data['e'] + '=='), 'big')
            
            public_key = rsa.RSAPublicNumbers(e, n).public_key(default_backend())
            pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            return pem
    
    print(f'[AUTH] No matching key found for kid: {kid}')
    return None

def get_token_from_header():
    """Extract Bearer token from Authorization header"""
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        return auth_header[7:]
    return None

def verify_token(token):
    """Verify JWT token with Auth0"""
    import jwt
    
    print(f'[AUTH] Verifying token: {token[:50]}...')
    
    try:
        # Get the public key
        public_key = get_auth0_public_key(token)
        
        if not public_key:
            print('[AUTH] Failed to get public key')
            return None
        
        # Try to decode with audience first
        try:
            payload = jwt.decode(
                token,
                public_key,
                algorithms=['RS256'],
                audience=AUTH0_AUDIENCE,
                issuer=f'https://{AUTH0_DOMAIN}/'
            )
            print(f'[AUTH] Token verified with audience')
            return payload
        except Exception as e:
            print(f'[AUTH] Audience validation failed: {e}')
            # Try without audience
            try:
                payload = jwt.decode(
                    token,
                    public_key,
                    algorithms=['RS256'],
                    issuer=f'https://{AUTH0_DOMAIN}/'
                )
                print(f'[AUTH] Token verified without audience')
                return payload
            except Exception as e2:
                print(f'[AUTH] Token decode failed: {e2}')
                return None
                
    except Exception as e:
        print(f'[AUTH] Token verification error: {e}')
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
