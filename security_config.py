"""
Security Configuration for MealPrep Application
This file contains all security-related configurations and settings
"""

# Security Configuration
SECURITY_CONFIG = {
    # Session Security
    'SESSION_TIMEOUT': 3600,  # 1 hour
    'SESSION_COOKIE_SECURE': True,
    'SESSION_COOKIE_HTTPONLY': True,
    'SESSION_COOKIE_SAMESITE': 'Lax',
    
    # Rate Limiting
    'RATE_LIMIT_REQUESTS_PER_MINUTE': 60,
    'RATE_LIMIT_LOGIN_ATTEMPTS': 5,
    'RATE_LIMIT_BLOCK_DURATION': 3600,  # 1 hour
    
    # Password Security
    'PASSWORD_MIN_LENGTH': 8,
    'PASSWORD_REQUIRE_UPPERCASE': True,
    'PASSWORD_REQUIRE_LOWERCASE': True,
    'PASSWORD_REQUIRE_NUMBERS': True,
    'PASSWORD_REQUIRE_SPECIAL': True,
    
    # File Upload Security
    'UPLOAD_MAX_SIZE': 5 * 1024 * 1024,  # 5MB
    'UPLOAD_ALLOWED_EXTENSIONS': ['.jpg', '.jpeg', '.png', '.gif', '.webp'],
    'UPLOAD_ALLOWED_MIME_TYPES': ['image/jpeg', 'image/png', 'image/gif', 'image/webp'],
    
    # Firewall Settings
    'FIREWALL_ENABLED': True,
    'FIREWALL_BLOCK_DURATION': 7200,  # 2 hours
    'FIREWALL_PORT_SCAN_THRESHOLD': 10,
    'FIREWALL_MAX_CONNECTIONS_PER_MINUTE': 100,
    
    # Intrusion Detection
    'IDS_ENABLED': True,
    'IDS_ALERT_THRESHOLD': 5,
    'IDS_LOG_RETENTION_DAYS': 30,
    
    # CSRF Protection
    'CSRF_ENABLED': True,
    'CSRF_TOKEN_EXPIRY': 3600,  # 1 hour
    
    # Input Validation
    'INPUT_MAX_LENGTH_EMAIL': 254,
    'INPUT_MAX_LENGTH_NAME': 100,
    'INPUT_MAX_LENGTH_GENERAL': 1000,
    'INPUT_MAX_LENGTH_SEARCH': 200,
    
    # Security Headers
    'SECURITY_HEADERS': {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self'; connect-src 'self'; frame-ancestors 'none';",
        'Referrer-Policy': 'strict-origin-when-cross-origin',
        'Permissions-Policy': 'geolocation=(), microphone=(), camera=()'
    },
    
    # Logging
    'SECURITY_LOG_ENABLED': True,
    'SECURITY_LOG_LEVEL': 'INFO',
    'SECURITY_LOG_RETENTION_DAYS': 90,
    
    # Encryption
    'ENCRYPTION_ALGORITHM': 'SHA-256',
    'ENCRYPTION_KEY_ROTATION_DAYS': 30,
    
    # API Security
    'API_RATE_LIMIT_PER_MINUTE': 100,
    'API_TIMEOUT': 30,  # 30 seconds
    'API_MAX_REQUEST_SIZE': 10 * 1024 * 1024,  # 10MB
    
    # Database Security
    'DB_CONNECTION_TIMEOUT': 30,
    'DB_QUERY_TIMEOUT': 10,
    'DB_MAX_CONNECTIONS': 100,
    
    # Monitoring
    'MONITORING_ENABLED': True,
    'MONITORING_ALERT_EMAIL': 'admin@mealprep.com',
    'MONITORING_WEBHOOK_URL': None,  # Set to webhook URL for alerts
    
    # Backup Security
    'BACKUP_ENCRYPTION_ENABLED': True,
    'BACKUP_RETENTION_DAYS': 30,
    'BACKUP_SCHEDULE_HOURS': 24,
}

# Allowed IP ranges for admin access
ADMIN_ALLOWED_IPS = [
    '127.0.0.1',  # localhost
    '192.168.0.0/16',  # Private network
    '10.0.0.0/8',  # Private network
    '172.16.0.0/12',  # Private network
]

# Blocked countries (if implementing GeoIP blocking)
BLOCKED_COUNTRIES = [
    # Add country codes to block
    # 'CN', 'RU', 'KP'
]

# Suspicious user agents to block
SUSPICIOUS_USER_AGENTS = [
    'sqlmap', 'nikto', 'dirb', 'nmap', 'masscan',
    'python-requests', 'curl', 'wget', 'scanner',
    'bot', 'crawler', 'spider', 'harvester'
]

# Attack patterns for detection
ATTACK_PATTERNS = {
    'SQL_INJECTION': [
        r'union.*select',
        r'select.*from.*where',
        r'insert.*into.*values',
        r'delete.*from.*where',
        r'drop.*table',
        r'exec.*sp_',
        r'xp_cmdshell',
        r'--',
        r'#',
        r'/\*',
        r'\*/',
    ],
    'XSS': [
        r'<script[^>]*>',
        r'javascript:',
        r'on\w+\s*=',
        r'eval\s*\(',
        r'alert\s*\(',
        r'document\.',
        r'window\.',
        r'location\.',
        r'cookie\s*=',
    ],
    'PATH_TRAVERSAL': [
        r'\.\.\/',
        r'\.\.\\',
        r'%2e%2e%2f',
        r'%2e%2e%5c',
        r'etc/passwd',
        r'etc/shadow',
        r'windows/system32',
    ],
    'COMMAND_INJECTION': [
        r';\s*cat\s',
        r';\s*ls\s',
        r';\s*dir\s',
        r';\s*whoami',
        r';\s*pwd',
        r'`.*`',
        r'\$\(.*\)',
        r'&&',
        r'\|\|',
    ],
    'LDAP_INJECTION': [
        r'\*\)\(',
        r'\)\(\|',
        r'\)\(\&',
        r'\*',
        r'\(',
        r'\)',
    ],
    'FILE_INCLUSION': [
        r'php://',
        r'file://',
        r'ftp://',
        r'http://',
        r'https://',
        r'data://',
        r'expect://',
    ]
}

# Security event types
SECURITY_EVENT_TYPES = {
    'LOGIN_SUCCESS': 'info',
    'LOGIN_FAILURE': 'warning',
    'LOGIN_BLOCKED': 'critical',
    'RATE_LIMIT_EXCEEDED': 'warning',
    'IP_BLOCKED': 'critical',
    'SQL_INJECTION_ATTEMPT': 'critical',
    'XSS_ATTEMPT': 'high',
    'PATH_TRAVERSAL_ATTEMPT': 'critical',
    'COMMAND_INJECTION_ATTEMPT': 'critical',
    'CSRF_VIOLATION': 'high',
    'UNAUTHORIZED_ACCESS': 'warning',
    'SUSPICIOUS_USER_AGENT': 'warning',
    'PORT_SCAN_DETECTED': 'high',
    'FILE_UPLOAD_VIOLATION': 'warning',
    'SESSION_HIJACKING': 'critical',
    'BRUTE_FORCE_ATTEMPT': 'high',
}

# Response actions for security events
SECURITY_RESPONSES = {
    'critical': {
        'block_ip': True,
        'notify_admin': True,
        'log_event': True,
        'session_termination': True,
    },
    'high': {
        'block_ip': False,
        'notify_admin': True,
        'log_event': True,
        'session_termination': False,
    },
    'warning': {
        'block_ip': False,
        'notify_admin': False,
        'log_event': True,
        'session_termination': False,
    },
    'info': {
        'block_ip': False,
        'notify_admin': False,
        'log_event': True,
        'session_termination': False,
    }
}

# Security scoring system
SECURITY_SCORES = {
    'SQL_INJECTION_ATTEMPT': 100,
    'COMMAND_INJECTION_ATTEMPT': 100,
    'PATH_TRAVERSAL_ATTEMPT': 90,
    'XSS_ATTEMPT': 80,
    'CSRF_VIOLATION': 70,
    'BRUTE_FORCE_ATTEMPT': 60,
    'PORT_SCAN_DETECTED': 50,
    'RATE_LIMIT_EXCEEDED': 30,
    'SUSPICIOUS_USER_AGENT': 20,
    'LOGIN_FAILURE': 10,
}

# Thresholds for automatic blocking
AUTO_BLOCK_THRESHOLDS = {
    'SCORE_PER_MINUTE': 200,  # Block if score exceeds 200 in 1 minute
    'SCORE_PER_HOUR': 500,    # Block if score exceeds 500 in 1 hour
    'FAILURES_PER_MINUTE': 10, # Block if 10 failures in 1 minute
    'SUSPICIOUS_REQUESTS_PER_MINUTE': 50, # Block if 50 suspicious requests in 1 minute
}

# Security monitoring intervals
MONITORING_INTERVALS = {
    'REAL_TIME': 1,        # 1 second
    'STATISTICS': 60,      # 1 minute
    'HOURLY_REPORT': 3600,  # 1 hour
    'DAILY_REPORT': 86400,  # 24 hours
}

# Data retention policies
DATA_RETENTION = {
    'SECURITY_LOGS': 90,     # 90 days
    'ACCESS_LOGS': 30,       # 30 days
    'ERROR_LOGS': 30,        # 30 days
    'SESSION_DATA': 7,       # 7 days
    'TEMPORARY_DATA': 1,      # 1 day
}

# Compliance settings
COMPLIANCE = {
    'GDPR_ENABLED': True,
    'CCPA_ENABLED': True,
    'DATA_ENCRYPTION_AT_REST': True,
    'DATA_ENCRYPTION_IN_TRANSIT': True,
    'AUDIT_LOGGING': True,
    'DATA_RETENTION_POLICY': True,
    'USER_CONSENT_REQUIRED': True,
    'RIGHT_TO_DELETION': True,
    'DATA_PORTABILITY': True,
}

# Security testing configuration
SECURITY_TESTING = {
    'PENETRATION_TESTING_ENABLED': False,
    'VULNERABILITY_SCANNING_ENABLED': False,
    'SECURITY_HEADERS_TEST': True,
    'INPUT_VALIDATION_TEST': True,
    'AUTHENTICATION_TEST': True,
    'AUTHORIZATION_TEST': True,
    'SESSION_SECURITY_TEST': True,
}

# Emergency response procedures
EMERGENCY_RESPONSE = {
    'INCIDENT_RESPONSE_TEAM': ['admin@mealprep.com'],
    'ESCALATION_PROCEDURE': True,
    'AUTOMATIC_RESPONSE_ENABLED': True,
    'BACKUP_RECOVERY_PLAN': True,
    'COMMUNICATION_PLAN': True,
    'POST_INCIDENT_REVIEW': True,
}
