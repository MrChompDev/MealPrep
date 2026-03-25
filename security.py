"""
Security Module for MealPrep Application
Provides comprehensive security measures including:
- Rate limiting
- CSRF protection
- Input validation and sanitization
- SQL injection prevention
- XSS protection
- Session security
- IP-based access control
- Request logging and monitoring
"""

import re
import hashlib
import time
import json
from datetime import datetime, timedelta
from functools import wraps
from collections import defaultdict, deque
from typing import Dict, List, Optional, Tuple
import ipaddress

class SecurityManager:
    """Comprehensive security management system"""
    
    def __init__(self):
        self.rate_limits = defaultdict(lambda: deque())
        self.blocked_ips = set()
        self.suspicious_activities = defaultdict(list)
        self.session_tokens = {}
        self.csrf_tokens = {}
        self.failed_logins = defaultdict(int)
        self.request_logs = deque(maxlen=10000)
        
        # Security configuration
        self.max_requests_per_minute = 60
        self.max_failed_logins = 5
        self.block_duration = 3600  # 1 hour
        self.session_timeout = 3600  # 1 hour
        self.csrf_token_expiry = 3600
        
        # SQL injection patterns
        self.sql_patterns = [
            r'(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION|SCRIPT)\b)',
            r'(--|\#|\/\*|\*\/)',
            r'(\bOR\b.*=\b.*\bOR\b)',
            r'(\bAND\b.*=\b.*\bAND\b)',
            r'(\bWHERE\b.*\bOR\b)',
            r'(\b1\s*=\s*1\b)',
            r'(\bTRUE\b|\bFALSE\b)',
            r'(\bNULL\b)',
            r'(\bINFORMATION_SCHEMA\b)',
            r'(\bSYS\b|\bMASTER\b)',
            r'(\bXP_\w+\b)',
            r'(\bSP_\w+\b)',
        ]
        
        # XSS patterns
        self.xss_patterns = [
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'on\w+\s*=',
            r'<iframe[^>]*>',
            r'<object[^>]*>',
            r'<embed[^>]*>',
            r'<link[^>]*>',
            r'<meta[^>]*>',
            r'eval\s*\(',
            r'alert\s*\(',
            r'document\.',
            r'window\.',
            r'location\.',
            r'cookie\s*=',
        ]
        
        # Suspicious user agents
        self.suspicious_agents = [
            'sqlmap', 'nikto', 'dirb', 'nmap', 'masscan',
            'python-requests', 'curl', 'wget', 'scanner',
            'bot', 'crawler', 'spider'
        ]
    
    def validate_input(self, data: str, input_type: str = 'general') -> Tuple[bool, str]:
        """Validate and sanitize user input"""
        if not isinstance(data, str):
            return False, "Invalid input type"
        
        # Check for SQL injection
        for pattern in self.sql_patterns:
            if re.search(pattern, data, re.IGNORECASE):
                self.log_suspicious_activity('SQL_INJECTION_ATTEMPT', data)
                return False, "Invalid characters detected"
        
        # Check for XSS
        for pattern in self.xss_patterns:
            if re.search(pattern, data, re.IGNORECASE):
                self.log_suspicious_activity('XSS_ATTEMPT', data)
                return False, "Invalid content detected"
        
        # Length validation
        max_lengths = {
            'email': 254,
            'name': 100,
            'password': 128,
            'general': 1000,
            'search': 200
        }
        
        max_len = max_lengths.get(input_type, max_lengths['general'])
        if len(data) > max_len:
            return False, f"Input too long (max {max_len} characters)"
        
        # Email validation
        if input_type == 'email':
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, data):
                return False, "Invalid email format"
        
        # Name validation (letters, spaces, hyphens, apostrophes only)
        if input_type == 'name':
            name_pattern = r"^[a-zA-Z\s\-']+$"
            if not re.match(name_pattern, data):
                return False, "Invalid name format"
        
        return True, "Valid input"
    
    def sanitize_output(self, data: str) -> str:
        """Sanitize output to prevent XSS"""
        if not isinstance(data, str):
            return str(data)
        
        # HTML escape
        data = data.replace('&', '&amp;')
        data = data.replace('<', '&lt;')
        data = data.replace('>', '&gt;')
        data = data.replace('"', '&quot;')
        data = data.replace("'", '&#x27;')
        
        return data
    
    def check_rate_limit(self, ip: str, endpoint: str = 'general') -> bool:
        """Check if IP has exceeded rate limits"""
        current_time = time.time()
        key = f"{ip}:{endpoint}"
        
        # Clean old requests
        self.rate_limits[key] = deque(
            [req_time for req_time in self.rate_limits[key] 
             if current_time - req_time < 60]
        )
        
        # Check limit
        if len(self.rate_limits[key]) >= self.max_requests_per_minute:
            self.log_suspicious_activity('RATE_LIMIT_EXCEEDED', f"{ip}:{endpoint}")
            return False
        
        # Add current request
        self.rate_limits[key].append(current_time)
        return True
    
    def is_ip_blocked(self, ip: str) -> bool:
        """Check if IP is blocked"""
        return ip in self.blocked_ips
    
    def block_ip(self, ip: str, reason: str = 'Security violation'):
        """Block an IP address"""
        self.blocked_ips.add(ip)
        self.log_suspicious_activity('IP_BLOCKED', f"{ip}:{reason}")
        
        # Auto-unblock after duration
        # Note: In production, this should be handled by a background task
    
    def check_failed_logins(self, ip: str, email: str) -> bool:
        """Check for too many failed login attempts"""
        key = f"{ip}:{email}"
        self.failed_logins[key] += 1
        
        if self.failed_logins[key] >= self.max_failed_logins:
            self.block_ip(ip, f"Too many failed logins for {email}")
            return False
        
        return True
    
    def generate_csrf_token(self, session_id: str) -> str:
        """Generate CSRF token"""
        token = hashlib.sha256(f"{session_id}:{time.time()}:{os.urandom(16)}".encode()).hexdigest()
        self.csrf_tokens[session_id] = {
            'token': token,
            'created': time.time()
        }
        return token
    
    def validate_csrf_token(self, session_id: str, token: str) -> bool:
        """Validate CSRF token"""
        if session_id not in self.csrf_tokens:
            return False
        
        stored_token = self.csrf_tokens[session_id]
        
        # Check expiry
        if time.time() - stored_token['created'] > self.csrf_token_expiry:
            del self.csrf_tokens[session_id]
            return False
        
        return stored_token['token'] == token
    
    def validate_session(self, session_id: str, user_email: str) -> bool:
        """Validate session"""
        if session_id not in self.session_tokens:
            return False
        
        session_data = self.session_tokens[session_id]
        
        # Check timeout
        if time.time() - session_data['last_activity'] > self.session_timeout:
            del self.session_tokens[session_id]
            return False
        
        # Check user match
        if session_data['user_email'] != user_email:
            return False
        
        # Update last activity
        session_data['last_activity'] = time.time()
        return True
    
    def create_session(self, user_email: str, ip: str) -> str:
        """Create secure session"""
        session_id = hashlib.sha256(f"{user_email}:{ip}:{time.time()}:{os.urandom(32)}".encode()).hexdigest()
        
        self.session_tokens[session_id] = {
            'user_email': user_email,
            'ip': ip,
            'created': time.time(),
            'last_activity': time.time()
        }
        
        return session_id
    
    def log_request(self, ip: str, method: str, endpoint: str, user_agent: str, status_code: int):
        """Log request for security monitoring"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'ip': ip,
            'method': method,
            'endpoint': endpoint,
            'user_agent': user_agent,
            'status_code': status_code
        }
        
        self.request_logs.append(log_entry)
        
        # Check for suspicious patterns
        self.analyze_request_patterns(log_entry)
    
    def analyze_request_patterns(self, log_entry: Dict):
        """Analyze request patterns for suspicious activity"""
        ip = log_entry['ip']
        user_agent = log_entry['user_agent'].lower()
        
        # Check for suspicious user agents
        for agent in self.suspicious_agents:
            if agent in user_agent:
                self.log_suspicious_activity('SUSPICIOUS_USER_AGENT', f"{ip}:{agent}")
                break
        
        # Check for 404 errors (potential scanning)
        if log_entry['status_code'] == 404:
            self.suspicious_activities[ip].append({
                'type': '404_ERROR',
                'timestamp': log_entry['timestamp'],
                'endpoint': log_entry['endpoint']
            })
    
    def log_suspicious_activity(self, activity_type: str, details: str):
        """Log suspicious activity"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'type': activity_type,
            'details': details
        }
        
        # In production, this should be sent to a security monitoring system
        print(f"SECURITY ALERT: {activity_type} - {details}")
    
    def get_security_headers(self) -> Dict[str, str]:
        """Get security headers for HTTP responses"""
        return {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self'; connect-src 'self'; frame-ancestors 'none';",
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            'Permissions-Policy': 'geolocation=(), microphone=(), camera=()'
        }
    
    def validate_file_upload(self, filename: str, content_type: str, file_size: int) -> Tuple[bool, str]:
        """Validate file uploads"""
        # Check file extension
        allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
        file_ext = os.path.splitext(filename)[1].lower()
        
        if file_ext not in allowed_extensions:
            return False, "File type not allowed"
        
        # Check MIME type
        allowed_mime_types = {
            'image/jpeg', 'image/jpg', 'image/png', 
            'image/gif', 'image/webp'
        }
        
        if content_type not in allowed_mime_types:
            return False, "Invalid file type"
        
        # Check file size (max 5MB)
        max_size = 5 * 1024 * 1024
        if file_size > max_size:
            return False, "File too large"
        
        # Check filename for suspicious patterns
        if any(pattern in filename.lower() for pattern in ['script', 'exec', 'php', 'asp', 'jsp']):
            return False, "Invalid filename"
        
        return True, "File valid"
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data (basic implementation)"""
        # In production, use proper encryption like AES
        key = "mealprep_security_key_2026"
        encrypted = hashlib.sha256((data + key).encode()).hexdigest()
        return encrypted
    
    def get_security_report(self) -> Dict:
        """Generate security report"""
        current_time = time.time()
        
        # Calculate statistics
        total_requests = len(self.request_logs)
        blocked_ips = len(self.blocked_ips)
        suspicious_activities = sum(len(activities) for activities in self.suspicious_activities.values())
        
        # Recent activity (last hour)
        recent_logs = [
            log for log in self.request_logs 
            if current_time - datetime.fromisoformat(log['timestamp']).timestamp() < 3600
        ]
        
        return {
            'total_requests': total_requests,
            'blocked_ips': blocked_ips,
            'suspicious_activities': suspicious_activities,
            'recent_requests': len(recent_logs),
            'active_sessions': len(self.session_tokens),
            'csrf_tokens': len(self.csrf_tokens),
            'rate_limit_entries': len(self.rate_limits)
        }

# Global security manager instance
security_manager = SecurityManager()

# Decorators for Flask routes
def require_security(f):
    """Security decorator for Flask routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get client IP
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR', 'unknown'))
        
        # Check if IP is blocked
        if security_manager.is_ip_blocked(client_ip):
            return jsonify({'error': 'Access denied'}), 403
        
        # Check rate limiting
        if not security_manager.check_rate_limit(client_ip, request.endpoint):
            return jsonify({'error': 'Too many requests'}), 429
        
        # Log request
        security_manager.log_request(
            client_ip, 
            request.method, 
            request.endpoint,
            request.headers.get('User-Agent', ''),
            200  # Default status, will be updated if response has different status
        )
        
        return f(*args, **kwargs)
    
    return decorated_function

def validate_json_input(required_fields: List[str] = None, input_types: Dict[str, str] = None):
    """Decorator to validate JSON input"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                return jsonify({'error': 'Invalid request format'}), 400
            
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            # Check required fields
            if required_fields:
                missing_fields = [field for field in required_fields if field not in data]
                if missing_fields:
                    return jsonify({'error': f'Missing required fields: {missing_fields}'}), 400
            
            # Validate field types and content
            if input_types:
                for field, field_type in input_types.items():
                    if field in data:
                        is_valid, message = security_manager.validate_input(str(data[field]), field_type)
                        if not is_valid:
                            return jsonify({'error': f'Invalid {field}: {message}'}), 400
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def csrf_protect(f):
    """CSRF protection decorator"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method in ['POST', 'PUT', 'DELETE']:
            csrf_token = request.headers.get('X-CSRF-Token') or request.form.get('csrf_token')
            session_id = session.get('session_id')
            
            if not csrf_token or not session_id:
                return jsonify({'error': 'CSRF token missing'}), 403
            
            if not security_manager.validate_csrf_token(session_id, csrf_token):
                return jsonify({'error': 'Invalid CSRF token'}), 403
        
        return f(*args, **kwargs)
    
    return decorated_function

# Import required modules
try:
    import os
except ImportError:
    os = None
