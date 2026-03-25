# MealPrep - Enterprise Food Delivery Application with AI & Security

[![Security Status](https://img.shields.io/badge/Security-Enterprise%20Grade-green)](https://github.com/yourusername/mealprep)
[![Python Version](https://img.shields.io/badge/Python-3.8%2B-blue)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.0%2B-red)](https://flask.palletsprojects.com)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

🍽️ **MealPrep** is a comprehensive food delivery application featuring intelligent AI ordering, modern Uber Eats-style UI, complete checkout system, developer tools, and enterprise-grade cybersecurity protection.

## 🚀 Features

### 🤖 **Intelligent AI System**
- Natural language meal ordering
- Personalized recommendations
- Learning from user behavior
- Real-time chatbot configuration
- Intent recognition and confidence scoring

### 🎨 **Modern UI/UX**
- Uber Eats-inspired design
- Mobile-responsive interface
- Real-time cart management
- Interactive meal browsing
- Smooth animations and transitions

### 🛒 **Complete Commerce**
- Full checkout process
- Multiple payment methods
- Order tracking system
- Subscription management
- User profiles and preferences

### 👨‍💻 **Developer Tools**
- System monitoring dashboard
- Chatbot configuration interface
- Real-time analytics
- Performance metrics
- Error tracking and logs

### 🛡️ **Enterprise Security**
- Advanced firewall system
- Intrusion Detection System (IDS)
- Real-time threat monitoring
- CSRF protection
- Input validation and sanitization
- Rate limiting and DDoS protection
- Security dashboard
- Automated security testing

## 📋 Quick Start

### Prerequisites
- Python 3.8+
- No external dependencies required (self-contained)

### Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/mealprep.git
cd mealprep

# Start the application
python app.py

# Access the application
# Web: http://localhost:5000
# Security Dashboard: http://localhost:5000/security (admin only)
```

### Default Accounts
- **Admin**: `admin@mealprep.com` / `mealprepadmin#123`
- **Developer**: `dev@mealprep.com` / `mealprepdev#123`
- **Test User**: `buhnerboy2@gmail.com` / (any password for testing)

## 🔒 Security Features

### 🛡️ **Firewall Protection**
- IP blocking and whitelisting
- Port scan detection
- Geographic filtering
- User agent filtering
- Rate limiting (60 req/min per IP)

### 🔍 **Intrusion Detection**
- SQL injection detection
- XSS attack prevention
- Command injection blocking
- Path traversal protection
- Real-time threat alerts

### 🚨 **Security Monitoring**
- Live security dashboard
- Real-time statistics
- Automated alert system
- Comprehensive audit logs
- Security event tracking

### 🧪 **Security Testing**
```bash
# Run comprehensive security tests
python security_test.py

# Generate security report
python -c "from security import security_manager; print('Security OK')"
```

## 📊 Application Architecture

### 🏗️ **Technology Stack**
- **Backend**: Flask (self-contained)
- **Database**: SQLite with DatabaseManager
- **AI**: Custom IntelligentAI system
- **Frontend**: HTML5, CSS3, JavaScript
- **Security**: Custom firewall and IDS

### 📁 **Project Structure**
```
mealprep/
├── app.py                 # Main Flask application
├── database_manager.py     # Database operations
├── intelligent_ai.py       # AI system
├── security.py            # Security management
├── firewall.py            # Firewall and IDS
├── security_config.py      # Security configuration
├── security_test.py       # Security testing suite
├── templates/             # HTML templates
├── static/               # CSS, JS, images
├── data/                 # Database and data files
└── tests/               # Test suite
```

### 🔧 **Configuration**
All security settings are configurable in `security_config.py`:
```python
RATE_LIMIT_REQUESTS_PER_MINUTE = 60
SESSION_TIMEOUT = 3600  # 1 hour
CSRF_TOKEN_EXPIRY = 3600  # 1 hour
FIREWALL_BLOCK_DURATION = 7200  # 2 hours
```

## 🌐 API Endpoints

### 🍽️ **Food & Ordering**
- `GET /api/meals` - Get all meals
- `POST /api/orders` - Create order
- `GET /api/orders/{id}` - Get order details

### 🤖 **AI & Chat**
- `POST /api/ai/chat` - Chat with AI
- `POST /api/ai/track` - Track user behavior
- `GET /api/ai/recommendations` - Get recommendations

### 🔐 **Security**
- `GET /api/security/status` - Security status (admin)
- `POST /api/security/block-ip` - Block IP (admin)
- `GET /api/security/alerts` - Security alerts (admin)

### 👤 **User Management**
- `POST /api/login` - User login
- `POST /api/register` - User registration
- `GET /api/profile` - User profile

## 🛠️ Development

### 🧪 **Testing**
```bash
# Run all tests
python -m pytest tests/

# Security testing
python security_test.py

# Health check
python health_check.py
```

### 📝 **Code Quality**
- Comprehensive error handling
- Input validation and sanitization
- Security best practices
- OWASP Top 10 compliance
- GDPR ready

### 🔄 **Database Management**
```bash
# Check database
python check_db.py

# Migrate data
python migrate_json_to_sql.py

# Update meal images
python update_db_images.py
```

## 📈 Monitoring & Analytics

### 📊 **System Monitoring**
- Real-time performance metrics
- User behavior tracking
- AI learning analytics
- Security event monitoring
- System health indicators

### 📋 **Analytics Dashboard**
- User registration statistics
- Popular meals and trends
- Order completion rates
- AI chat analytics
- Security threat statistics

## 🔐 Security Compliance

### 🛡️ **Security Standards**
- OWASP Top 10 protection
- GDPR compliance ready
- Data encryption at rest and in transit
- Secure session management
- Comprehensive audit logging

### 🚨 **Threat Protection**
- SQL injection prevention
- XSS attack blocking
- CSRF protection
- Command injection prevention
- Path traversal protection
- Brute force attack prevention

## 📚 Documentation

- **[Complete Documentation](readme.md)** - Comprehensive feature documentation
- **[Security Summary](SECURITY_SUMMARY.md)** - Security implementation details
- **[API Documentation](docs/api.md)** - Complete API reference
- **[Security Guide](docs/security.md)** - Security configuration guide

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🎯 Roadmap

### 🚀 **Upcoming Features**
- Real payment integration (Stripe/PayPal)
- Mobile app development
- Advanced AI features
- Multi-language support
- Real-time delivery tracking

### 🔒 **Security Enhancements**
- Two-factor authentication
- Advanced threat detection
- Machine learning security
- Zero-trust architecture
- Compliance automation

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/mealprep/issues)
- **Documentation**: [Wiki](https://github.com/yourusername/mealprep/wiki)
- **Security**: Report security issues to security@mealprep.com

## 🎉 Acknowledgments

- Flask framework for the robust backend
- Uber Eats for UI/UX inspiration
- OWASP for security guidelines
- The open-source community

---

**🍽️ MealPrep - Enterprise Food Delivery with AI & Security** 🛡️

Made with ❤️ by Daniel
