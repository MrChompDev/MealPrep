"""
Firewall System for MealPrep Application
Provides network-level protection and access control
"""

import re
import json
import time
import socket
import threading
from datetime import datetime, timedelta
from collections import defaultdict, deque
from typing import Dict, List, Set, Optional, Tuple
import ipaddress

class FirewallManager:
    """Advanced firewall and access control system"""
    
    def __init__(self):
        self.firewall_rules = []
        self.blocked_ips = set()
        self.allowed_ips = set()
        self.rate_limiters = defaultdict(lambda: deque())
        self.port_scanners = defaultdict(list)
        self.suspicious_patterns = defaultdict(int)
        self.whitelist_domains = set()
        self.blacklist_domains = set()
        
        # Firewall configuration
        self.max_connections_per_minute = 100
        self.port_scan_threshold = 10
        self.block_duration = 7200  # 2 hours
        self.suspicious_threshold = 5
        
        # Initialize default rules
        self.initialize_default_rules()
    
    def initialize_default_rules(self):
        """Initialize default firewall rules"""
        # Allow localhost
        self.allowed_ips.add('127.0.0.1')
        self.allowed_ips.add('::1')
        
        # Allow private networks (adjust as needed)
        private_networks = [
            '192.168.0.0/16',
            '10.0.0.0/8',
            '172.16.0.0/12'
        ]
        
        for network in private_networks:
            try:
                ip_net = ipaddress.ip_network(network)
                for ip in ip_net.hosts():
                    self.allowed_ips.add(str(ip))
            except:
                pass
        
        # Common attack patterns to block
        self.attack_patterns = {
            'sql_injection': [
                r'union.*select',
                r'select.*from.*where',
                r'insert.*into.*values',
                r'delete.*from.*where',
                r'drop.*table',
                r'exec.*sp_',
                r'xp_cmdshell'
            ],
            'xss': [
                r'<script[^>]*>',
                r'javascript:',
                r'on\w+\s*=',
                r'eval\s*\(',
                r'alert\s*\('
            ],
            'path_traversal': [
                r'\.\.\/',
                r'\.\.\\',
                r'%2e%2e%2f',
                r'%2e%2e%5c'
            ],
            'command_injection': [
                r';\s*cat\s',
                r';\s*ls\s',
                r';\s*dir\s',
                r';\s*whoami',
                r';\s*pwd',
                r'`.*`',
                r'\$\(.*\)'
            ],
            'ldap_injection': [
                r'\*\)\(',
                r'\)\(\|',
                r'\)\(\&'
            ]
        }
    
    def add_firewall_rule(self, rule: Dict):
        """Add a firewall rule"""
        required_fields = ['action', 'type', 'pattern']
        
        for field in required_fields:
            if field not in rule:
                raise ValueError(f"Missing required field: {field}")
        
        self.firewall_rules.append(rule)
    
    def is_ip_allowed(self, ip: str) -> Tuple[bool, str]:
        """Check if IP is allowed"""
        try:
            ip_addr = ipaddress.ip_address(ip)
        except ValueError:
            return False, "Invalid IP address"
        
        # Check if IP is explicitly blocked
        if ip in self.blocked_ips:
            return False, "IP blocked by firewall"
        
        # Check if IP is explicitly allowed
        if ip in self.allowed_ips:
            return True, "IP explicitly allowed"
        
        # Check firewall rules
        for rule in self.firewall_rules:
            if self.matches_rule(ip_addr, rule):
                if rule['action'] == 'allow':
                    return True, f"Allowed by rule: {rule.get('name', 'unnamed')}"
                else:
                    return False, f"Blocked by rule: {rule.get('name', 'unnamed')}"
        
        # Default deny for unknown IPs (can be changed to allow)
        return False, "No matching rule found"
    
    def matches_rule(self, ip: ipaddress.IPv4Address, rule: Dict) -> bool:
        """Check if IP matches firewall rule"""
        if rule['type'] == 'ip_range':
            try:
                network = ipaddress.ip_network(rule['pattern'])
                return ip in network
            except:
                return False
        
        elif rule['type'] == 'ip_list':
            return str(ip) in rule['pattern']
        
        elif rule['type'] == 'country':
            # This would require a GeoIP database in production
            return False
        
        return False
    
    def detect_port_scan(self, ip: str, port: int):
        """Detect port scanning activity"""
        current_time = time.time()
        
        # Clean old entries (older than 1 minute)
        self.port_scanners[ip] = [
            (p, t) for p, t in self.port_scanners[ip] 
            if current_time - t < 60
        ]
        
        # Add current port access
        self.port_scanners[ip].append((port, current_time))
        
        # Check for port scanning pattern
        unique_ports = len(set(p for p, t in self.port_scanners[ip]))
        if unique_ports >= self.port_scan_threshold:
            self.block_ip(ip, "Port scanning detected")
            return True
        
        return False
    
    def analyze_request_content(self, ip: str, content: str) -> bool:
        """Analyze request content for attack patterns"""
        content_lower = content.lower()
        
        for attack_type, patterns in self.attack_patterns.items():
            for pattern in patterns:
                if re.search(pattern, content_lower, re.IGNORECASE):
                    self.suspicious_patterns[ip] += 1
                    self.log_firewall_event(f"{attack_type.upper()}_ATTEMPT", ip, pattern)
                    
                    # Block if too many suspicious patterns
                    if self.suspicious_patterns[ip] >= self.suspicious_threshold:
                        self.block_ip(ip, f"Too many {attack_type} attempts")
                        return True
        
        return False
    
    def check_rate_limiting(self, ip: str, endpoint: str) -> bool:
        """Check rate limiting for IP"""
        current_time = time.time()
        key = f"{ip}:{endpoint}"
        
        # Clean old entries
        self.rate_limiters[key] = deque(
            [req_time for req_time in self.rate_limiters[key] 
             if current_time - req_time < 60]
        )
        
        # Check limit
        if len(self.rate_limiters[key]) >= self.max_connections_per_minute:
            self.log_firewall_event("RATE_LIMIT_EXCEEDED", ip, f"{endpoint}: {len(self.rate_limiters[key])} requests/min")
            return False
        
        # Add current request
        self.rate_limiters[key].append(current_time)
        return True
    
    def block_ip(self, ip: str, reason: str = "Security violation"):
        """Block an IP address"""
        self.blocked_ips.add(ip)
        self.log_firewall_event("IP_BLOCKED", ip, reason)
        
        # Remove from allowed list if present
        self.allowed_ips.discard(ip)
    
    def unblock_ip(self, ip: str):
        """Unblock an IP address"""
        self.blocked_ips.discard(ip)
        self.log_firewall_event("IP_UNBLOCKED", ip, "Manual unblock")
    
    def add_allowed_ip(self, ip: str):
        """Add IP to allowed list"""
        self.allowed_ips.add(ip)
        self.blocked_ips.discard(ip)
    
    def log_firewall_event(self, event_type: str, ip: str, details: str):
        """Log firewall events"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'ip': ip,
            'details': details
        }
        
        # In production, send to security monitoring system
        print(f"FIREWALL: {event_type} from {ip} - {details}")
    
    def get_firewall_status(self) -> Dict:
        """Get firewall status and statistics"""
        return {
            'blocked_ips': len(self.blocked_ips),
            'allowed_ips': len(self.allowed_ips),
            'active_rules': len(self.firewall_rules),
            'port_scanners': len(self.port_scanners),
            'rate_limit_entries': len(self.rate_limiters),
            'suspicious_ips': len([ip for ip, count in self.suspicious_patterns.items() if count > 0])
        }
    
    def export_firewall_log(self) -> List[Dict]:
        """Export firewall log for analysis"""
        # This would typically read from a persistent log file
        return []
    
    def create_default_rules(self):
        """Create default firewall rules"""
        default_rules = [
            {
                'name': 'Allow localhost',
                'action': 'allow',
                'type': 'ip_list',
                'pattern': ['127.0.0.1', '::1']
            },
            {
                'name': 'Block known malicious IPs',
                'action': 'block',
                'type': 'ip_list',
                'pattern': []  # Would be populated with known malicious IPs
            },
            {
                'name': 'Allow private network',
                'action': 'allow',
                'type': 'ip_range',
                'pattern': '192.168.0.0/16'
            }
        ]
        
        for rule in default_rules:
            self.add_firewall_rule(rule)

class IntrusionDetectionSystem:
    """Basic intrusion detection system"""
    
    def __init__(self):
        self.alerts = deque(maxlen=1000)
        self.signatures = []
        self.anomaly_thresholds = {
            'requests_per_minute': 200,
            'failed_logins_per_minute': 10,
            'error_rate_percentage': 50,
            'unique_ips_per_minute': 50
        }
        self.load_signatures()
    
    def load_signatures(self):
        """Load intrusion detection signatures"""
        self.signatures = [
            {
                'name': 'SQL Injection Attempt',
                'pattern': r'union.*select|select.*from.*where|insert.*into',
                'severity': 'high',
                'category': 'sql_injection'
            },
            {
                'name': 'XSS Attempt',
                'pattern': r'<script[^>]*>|javascript:|on\w+\s*=',
                'severity': 'medium',
                'category': 'xss'
            },
            {
                'name': 'Path Traversal',
                'pattern': r'\.\.\/|\.\.\\|%2e%2e%2f',
                'severity': 'high',
                'category': 'path_traversal'
            },
            {
                'name': 'Command Injection',
                'pattern': r';\s*(cat|ls|dir|whoami|pwd)|`.*`|\$\(.*\)',
                'severity': 'critical',
                'category': 'command_injection'
            }
        ]
    
    def analyze_request(self, ip: str, method: str, path: str, headers: Dict, body: str = "") -> Optional[Dict]:
        """Analyze request for intrusion attempts"""
        # Combine request data for analysis
        request_data = f"{method} {path} {headers} {body}".lower()
        
        # Check against signatures
        for signature in self.signatures:
            if re.search(signature['pattern'], request_data, re.IGNORECASE):
                alert = {
                    'timestamp': datetime.now().isoformat(),
                    'ip': ip,
                    'signature': signature['name'],
                    'severity': signature['severity'],
                    'category': signature['category'],
                    'method': method,
                    'path': path
                }
                
                self.alerts.append(alert)
                return alert
        
        return None
    
    def detect_anomalies(self, request_stats: Dict) -> List[Dict]:
        """Detect statistical anomalies"""
        anomalies = []
        
        # Check request rate anomaly
        if request_stats.get('requests_per_minute', 0) > self.anomaly_thresholds['requests_per_minute']:
            anomalies.append({
                'timestamp': datetime.now().isoformat(),
                'type': 'high_request_rate',
                'value': request_stats['requests_per_minute'],
                'threshold': self.anomaly_thresholds['requests_per_minute']
            })
        
        # Check failed login anomaly
        if request_stats.get('failed_logins_per_minute', 0) > self.anomaly_thresholds['failed_logins_per_minute']:
            anomalies.append({
                'timestamp': datetime.now().isoformat(),
                'type': 'high_failed_login_rate',
                'value': request_stats['failed_logins_per_minute'],
                'threshold': self.anomaly_thresholds['failed_logins_per_minute']
            })
        
        return anomalies
    
    def get_recent_alerts(self, minutes: int = 60) -> List[Dict]:
        """Get recent alerts"""
        current_time = datetime.now()
        cutoff_time = current_time - timedelta(minutes=minutes)
        
        recent_alerts = []
        for alert in self.alerts:
            alert_time = datetime.fromisoformat(alert['timestamp'])
            if alert_time > cutoff_time:
                recent_alerts.append(alert)
        
        return recent_alerts

# Global instances
firewall_manager = FirewallManager()
ids = IntrusionDetectionSystem()
