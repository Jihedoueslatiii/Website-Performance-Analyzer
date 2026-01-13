# 🚀 Website Performance Analyzer

A self-hosted tool that analyzes website performance, SEO, accessibility, and best practices with **exact point breakdowns**.

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/flask-3.0.0-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)

---

## Why This Tool?

✅ **Unlimited tests** - No rate limits  
✅ **Precise scoring** - See exactly why you lost points  
✅ **Self-hosted** - Your data stays private  
✅ **Free forever** - No subscriptions  

**Example:**
```
❌ Vague: "Performance: 75"
✅ Clear: "Performance: 75
  - TTFB: -10pts (850ms, 250ms too slow)
  - Page Load: -15pts (3500ms, 500ms over limit)"
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      FRONTEND                           │
│  ┌──────────────────────────────────────────────────┐  │
│  │  HTML/CSS/JavaScript (Vanilla)                   │  │
│  │  • Form input & validation                       │  │
│  │  • Animated score displays                       │  │
│  │  • Results visualization                         │  │
│  └──────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP POST /api/analyze
                     │ {"url": "https://example.com"}
                     ▼
┌─────────────────────────────────────────────────────────┐
│                   FLASK BACKEND                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │  API Routes (app.py)                             │  │
│  │  • URL validation                                │  │
│  │  • Request handling                              │  │
│  │  • Response formatting                           │  │
│  └─────────────────┬────────────────────────────────┘  │
│                    │                                    │
│  ┌─────────────────▼────────────────────────────────┐  │
│  │  Analysis Engine                                 │  │
│  │  • run_analysis()                                │  │
│  │  • calculate_scores()                            │  │
│  └─────────────────┬────────────────────────────────┘  │
└────────────────────┼────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              PLAYWRIGHT (Headless Browser)              │
│  ┌──────────────────────────────────────────────────┐  │
│  │  page.goto(url)                                  │  │
│  │  page.evaluate() - Run JS on page               │  │
│  │  page.screenshot() - Capture preview            │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
│  Collects:                                              │
│  • Performance metrics (TTFB, FCP, load time)          │
│  • SEO data (title, meta tags, HTTPS)                 │
│  • Accessibility (alt tags, headings)                  │
│  • Page structure (elements, links, resources)         │
└─────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
website-analyzer/
├── app.py                      # Flask backend + analysis logic
├── requirements.txt            # Python dependencies
├── templates/
│   └── index.html             # Frontend UI
├── static/
│   └── screenshots/           # Generated page screenshots
└── README.md                  # Documentation
```

**File Breakdown:**

- **app.py** (400 lines)
  - Flask routes (`/`, `/api/analyze`)
  - Playwright automation
  - Scoring algorithms
  - Error handling

- **index.html** (600 lines)
  - Form interface
  - Score visualizations
  - Results display
  - API communication

---

## 🚀 Quick Start

### 1. Install

```bash
# Clone repository
git clone https://github.com/yourusername/website-analyzer.git
cd website-analyzer

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
python -m playwright install chromium

# Create directories
mkdir -p static/screenshots templates
```

### 2. Run

```bash
python app.py
```

Visit **http://localhost:5000**

### 3. Test

```bash
# Via UI: Enter URL and click "Analyze"

# Via API:
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

---

## 🎯 What It Analyzes

### Performance (0-100)
| Metric | Threshold | Points Lost |
|--------|-----------|-------------|
| TTFB | > 600ms | -10 |
| FCP | > 2000ms | -15 |
| Page Load | > 3000ms | -20 |
| Requests | > 50 | -15 |
| Page Size | > 1000KB | -10 |

### SEO (0-100)
- ✅ Title tag (50-60 chars) → -30 if missing
- ✅ Meta description → -25 if missing
- ✅ HTTPS → -15 if HTTP
- ✅ Viewport meta → -10 if missing
- ✅ Open Graph → -10 if missing

### Accessibility (0-100)
- ✅ Image alt tags → -5 per missing (max -40)
- ✅ Viewport meta → -15 if missing
- ✅ Heading structure → checks H1-H6

### Best Practices (0-100)
- ✅ HTTPS encryption → -30 if missing
- ✅ Resource optimization → -10 if > 50 requests
- ✅ Page weight → -10 if > 1000KB

---

## 🔧 Tech Stack

| Component | Technology | Why |
|-----------|-----------|-----|
| **Backend** | Flask 3.0 | Lightweight, easy API creation |
| **Automation** | Playwright | Reliable browser automation, modern API |
| **Frontend** | Vanilla JS | No build tools, simple deployment |
| **Styling** | Custom CSS | Full design control |

**Dependencies:**
```txt
Flask==3.0.0
flask-cors==4.0.0
playwright==1.40.0
```

---

## 📊 API Response Example

```json
{
  "url": "https://example.com",
  "timestamp": "2025-01-10 14:30:25",
  "scores": {
    "performance": 85,
    "seo": 92,
    "accessibility": 78,
    "bestPractices": 95
  },
  "breakdown": {
    "performance": [
      {
        "check": "TTFB",
        "status": "pass",
        "points_lost": 0,
        "reason": "450ms (optimal: <600ms)"
      }
    ]
  },
  "metrics": {
    "ttfb": "450ms",
    "pageLoad": "2500ms",
    "networkRequests": 42
  }
}
```

---

## 🚢 Deployment

### Option 1: Render (Recommended)

1. Push code to GitHub
2. Connect repository to [Render](https://render.com)
3. Add build command:
```bash
pip install -r requirements.txt && playwright install chromium
```
4. Set start command:
```bash
gunicorn app:app
```

### Option 2: Docker

```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN playwright install chromium
RUN playwright install-deps chromium
COPY . .
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
```

```bash
docker build -t website-analyzer .
docker run -p 5000:5000 website-analyzer
```

### Option 3: VPS (DigitalOcean, AWS EC2)

```bash
# SSH into server
ssh user@your-server

# Install dependencies
sudo apt update
sudo apt install python3 python3-pip

# Clone and setup
git clone your-repo
cd website-analyzer
pip3 install -r requirements.txt
python3 -m playwright install chromium

# Run with systemd (production)
sudo nano /etc/systemd/system/analyzer.service
```

---

## 🔍 How Scoring Works

Each category starts at **100 points**. Points are deducted based on failures:

```python
# Example: Performance Score
perf_score = 100

if ttfb > 600:
    perf_score -= 10  # Slow server
    
if fcp > 2000:
    perf_score -= 15  # Content appears late
    
if page_load > 3000:
    perf_score -= 20  # Page loads slowly
    
if network_requests > 50:
    perf_score -= 15  # Too many requests
    
if page_size > 1000:
    perf_score -= 10  # Heavy page

# Final score: max(0, perf_score)
```

**Customize thresholds** in `app.py` → `calculate_scores()`

---

## ⚠️ Troubleshooting

### Issue: "Playwright not found"
```bash
python -m playwright install chromium
```

### Issue: "Port 5000 already in use"
Change port in `app.py`:
```python
app.run(debug=True, port=5001)
```

### Issue: "Screenshot failed"
Ensure `static/screenshots/` directory exists:
```bash
mkdir -p static/screenshots
```

### Issue: "Timeout errors"
Increase timeout in `app.py`:
```python
page.goto(url, wait_until='domcontentloaded', timeout=60000)
```

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

**Ideas for contributions:**
- Add more performance metrics (LCP, CLS, TBT)
- Implement PDF report export
- Add historical tracking
- Create comparison mode
- Build CLI version

---



## ⭐ Support

If this project helped you, give it a ⭐️!

**Questions?** Open an issue or reach out on LinkedIn.

---

Built with ❤️ using Flask & Playwright