# SEC Analysis AI Chatbot 🚀

A sophisticated AI-powered chatbot for analyzing SEC filings including 10-K annual reports, 8-K current events, and Form 4 insider trading data. Features a sleek dark-themed frontend with real-time analysis and comprehensive reporting.

![SEC Analysis AI](https://img.shields.io/badge/Status-Prototype-yellow)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Flask](https://img.shields.io/badge/Flask-2.0%2B-green)
![License](https://img.shields.io/badge/License-MIT-blue)

## ✨ Features

- **🔍 Multi-Source Analysis**: 10-K, 8-K, and Form 4 SEC filings
- **🤖 AI-Powered Insights**: Gemini AI integration for comprehensive analysis
- **🎨 Dark Sleek UI**: Professional gradient interface with glassmorphism effects
- **📊 Real-Time Processing**: Live progress tracking with synchronized loading
- **📋 Source Attribution**: Clear data source references for all analyses
- **🚀 Fast Query Processing**: Optimized for quick SEC data retrieval
- **📱 Responsive Design**: Works perfectly on desktop and mobile devices

## 🛠️ System Requirements

### Prerequisites

- **Python 3.8+**
- **Node.js** (for any future frontend enhancements)
- **Google Gemini API Key**
- **Windows 10/11** or **macOS** or **Linux**
- **4GB RAM minimum** (8GB recommended)
- **2GB free disk space**

### Python Dependencies

```
flask>=2.0.0
flask-cors>=3.0.0
google-generativeai>=0.3.0
requests>=2.28.0
python-dotenv>=0.19.0
```

## 📦 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/DRAGOON21S/ScalarFieldTask.git
cd ScalarFieldTask
```

### 2. Set Up Python Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 3. Install Python Dependencies

```bash
pip install flask flask-cors google-generativeai requests python-dotenv
```

### 4. Configure API Keys

Create a `.env` file in the root directory:

```env
GEMINI_API_KEY=your_gemini_api_key_here
FLASK_ENV=development
FLASK_DEBUG=true
```

**To get your Gemini API Key:**

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy and paste it into your `.env` file

### 5. Prepare SEC Data

Ensure your SEC data files are in the correct directories:

```
pretty-little-baby/
├── proto-3/
│   └── companies/           # Company-specific SEC data
│       ├── Apple_Inc/
│       ├── DoorDash_Inc/
│       ├── JOHNSON_&_JOHNSON/
│       ├── JPMORGAN_CHASE_&_CO/
│       ├── Meta_Platforms_Inc/
│       ├── MICROSOFT_CORP/
│       ├── NVIDIA_CORP/
│       ├── ROKU_INC/
│       ├── UNITEDHEALTH_GROUP_INC/
│       └── Zoom_Communications_Inc/
├── gemini_10k/              # 10-K annual reports
├── gemini_8k/               # 8-K current events
├── gemini_form4/            # Form 4 insider trading
└── frontend/                # Frontend files
```

## 🚀 Quick Start

### 1. Start the Server

```bash
python sec_analysis_server.py
```

### 2. Access the Application

Open your web browser and navigate to:

```
http://localhost:5000
```

### 3. Start Analyzing!

- Enter queries like: "_What are Apple's main business segments?_"
- Ask about: "_Microsoft's cybersecurity incidents_"
- Explore: "_NVIDIA's insider trading activities_"

## 📊 Available Company Data

This system currently contains SEC filing data for the following companies:

- **Apple Inc** - Technology (Consumer Electronics)
- **DoorDash Inc** - Technology (Food Delivery)
- **Johnson & Johnson** - Healthcare (Pharmaceuticals)
- **JPMorgan Chase & Co** - Financial Services (Banking)
- **Meta Platforms Inc** - Technology (Social Media)
- **Microsoft Corp** - Technology (Software & Cloud)
- **NVIDIA Corp** - Technology (Semiconductors & AI)
- **Roku Inc** - Technology (Streaming Platform)
- **UnitedHealth Group Inc** - Healthcare (Insurance)
- **Zoom Communications Inc** - Technology (Video Communications)

You can analyze SEC filings (10-K, 8-K, Form 4) for any of these companies using natural language queries.

## 📁 Project Structure

```
ScalarFieldTask/
├── README.md                           # This file
├── requirements.txt                    # Python dependencies
├── .env                               # Environment variables
├── sec_analysis_server.py             # Main Flask server
├── sec_tools.py                       # 10-K analysis tools
├── sec_8k_analyzer.py                 # 8-K analysis tools
├── sec_insider_analyzer.py            # Form 4 analysis tools
├── sec_master_analyzer.py             # Combined analysis orchestrator
├── proto-3/
│   └── companies/                     # Available company data
│       ├── Apple_Inc/
│       ├── DoorDash_Inc/
│       ├── JOHNSON_&_JOHNSON/
│       ├── JPMORGAN_CHASE_&_CO/
│       ├── Meta_Platforms_Inc/
│       ├── MICROSOFT_CORP/
│       ├── NVIDIA_CORP/
│       ├── ROKU_INC/
│       ├── UNITEDHEALTH_GROUP_INC/
│       └── Zoom_Communications_Inc/
├── frontend/
│   ├── index.html                     # Main frontend interface
│   ├── styles.css                     # Dark theme styling
│   ├── script.js                      # Frontend logic
└── data/
    ├── gemini_10k/                    # 10-K JSON files
    ├── gemini_8k/                     # 8-K JSON files
    └── gemini_form4/                  # Form 4 JSON files
```

## 🔧 Configuration

### Server Configuration

Edit `sec_analysis_server.py` for server settings:

```python
# Server Configuration
HOST = '0.0.0.0'  # Change to '127.0.0.1' for local only
PORT = 5000       # Change port if needed
DEBUG = True      # Set to False in production
```

### Frontend Customization

Modify `frontend/styles.css` for theme customization:

```css
:root {
    --accent-color: #60a5fa;     # Primary accent color
    --bg-primary: #0a0a0a;       # Background color
    --text-primary: #ffffff;      # Text color
}
```

## 🎯 Usage Examples

### Basic Queries (Available Companies)

```
"What are Apple's risk factors?"
"Microsoft's recent 8-K filings"
"NVIDIA's insider trading summary"
"Johnson & Johnson's business segments analysis"
"Meta's regulatory challenges"
"JPMorgan Chase's financial performance"
"UnitedHealth Group's healthcare initiatives"
"Zoom's cybersecurity measures"
"DoorDash's growth strategy"
"Roku's streaming market position"
```

### Advanced Queries

```
"Compare Apple and Microsoft's cybersecurity strategies"
"Analyze NVIDIA's executive compensation changes"
"What are Meta's regulatory challenges in 2024?"
"Compare healthcare strategies between Johnson & Johnson and UnitedHealth Group"
"Analyze technology sector risk factors across Apple, Microsoft, and NVIDIA"
```

## 🔍 API Endpoints

### Main Analysis Endpoint

```http
POST /analyze
Content-Type: application/json

{
  "query": "What are Apple's main business segments?"
}
```

### Health Check

```http
GET /api/health
```

### Server Status

```http
GET /api/status
```

## 🐛 Troubleshooting

### Common Issues

#### **Server Won't Start**

```bash
# Check if port is in use
netstat -ano | findstr :5000

# Kill existing Python processes
taskkill /F /IM python.exe
```

#### **API Key Issues**

- Verify your Gemini API key is correct
- Check `.env` file formatting
- Ensure API key has proper permissions

#### **Empty Analysis Results**

- Check if SEC data files exist in correct directories
- Verify file naming conventions match expected patterns
- Review server logs for detailed error messages

#### **Frontend Not Loading**

- Clear browser cache
- Check browser console for JavaScript errors
- Verify Flask server is running on correct port

### Debug Mode

Enable detailed logging:

```bash
set FLASK_DEBUG=1
python sec_analysis_server.py
```

## 🚦 Performance Optimization

### For Better Performance:

1. **Use SSD storage** for faster file access
2. **Increase RAM** for better caching
3. **Close unnecessary applications** during analysis
4. **Use wired internet connection** for API calls

### Production Deployment:

```bash
# Use production WSGI server
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 sec_analysis_server:app
```

## 📊 System Monitoring

Monitor system performance during analysis:

- **CPU Usage**: Should stay below 80%
- **Memory Usage**: Monitor for memory leaks
- **API Rate Limits**: Track Gemini API usage
- **Response Times**: Typical analysis takes 10-30 seconds

## 🔐 Security Considerations

### For Production Use:

1. **Change default passwords**
2. **Use HTTPS encryption**
3. **Implement rate limiting**
4. **Secure API keys properly**
5. **Regular security updates**

```python
# Example rate limiting
from flask_limiter import Limiter
limiter = Limiter(app, key_func=get_remote_address)

@app.route('/analyze', methods=['POST'])
@limiter.limit("10 per minute")
def analyze():
    # Analysis code
```

## 📝 Development

### Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Make changes and test thoroughly
4. Commit: `git commit -m 'Add feature'`
5. Push: `git push origin feature-name`
6. Create Pull Request

### Testing

```bash
# Run basic functionality test
python test_api.py

# Test individual components
python sec_tools.py "test query"
python sec_8k_analyzer.py "test query"
python sec_insider_analyzer.py "test query"
```

## 📞 Support

### Getting Help

- **Issues**: Create GitHub issues for bugs
- **Features**: Submit feature requests
- **Documentation**: Check inline code comments
- **Community**: Join discussions

### Known Limitations

- **Prototype Status**: This is an early prototype
- **Processing Time**: Analysis can take 10-60 seconds
- **Data Coverage**: Limited to 10 specific companies (see Available Company Data section)
- **API Limits**: Subject to Gemini API rate limits
- **Company Scope**: Currently supports Apple, DoorDash, Johnson & Johnson, JPMorgan Chase, Meta, Microsoft, NVIDIA, Roku, UnitedHealth Group, and Zoom

## 🔄 Updates

### Version History

- **v1.0.0**: Initial prototype release
- **Features**: Multi-source analysis, dark UI, real-time progress
- **Status**: Active development

### Planned Features

- [ ] Real-time SEC filing updates
- [ ] Advanced filtering options
- [ ] Export to PDF/Excel
- [ ] User authentication
- [ ] Historical trend analysis
- [ ] Mobile app version

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Google Gemini AI** for powerful analysis capabilities
- **SEC.gov** for comprehensive filing data
- **Flask Community** for excellent web framework
- **Contributors** who help improve this project

---

## ⚠️ Important Note

**This is a prototype system.** Analysis times may be longer than expected as we optimize the system. Thank you for your patience! 🙏

---

**Made with ❤️ for better SEC analysis**

For questions or support, please create an issue in the repository.
