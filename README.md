# Sales Analytics AI Agent System 

[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104%2B-009688.svg)](https://fastapi.tiangolo.com)
[![LangChain](https://img.shields.io/badge/LangChain-latest-green)](https://www.langchain.com/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

AI-driven sales analytics platform built with a multi-agent architecture. It offers a comprehensive suite of analytics, including Descriptive, Diagnostic, Predictive, and Prescriptive insights, empowering businesses to make data-driven decisions. The system features an intuitive web interface designed for seamless user interaction, providing actionable insights and fostering intelligent sales strategies.


<img width="1432" height="948" alt="image" src="https://github.com/user-attachments/assets/802bccbf-0b8f-43eb-adac-851539892149" />


## 🌟 Key Features

### 🧠 Multi-Agent Architecture
- **Orchestrator Agent**: Coordinates analysis and intelligently routes queries
- **Descriptive Agent**: Analyzes historical patterns and trends
- **Diagnostic Agent**: Investigates root causes and relationships
- **Predictive Agent**: Forecasts future outcomes with ML models
- **Prescriptive Agent**: Recommends data-driven action plans

### 📊 Comprehensive Analytics Suite

**Descriptive Analytics**
- Sales summary statistics and KPIs
- Time series trends with seasonality detection
- Multi-dimensional breakdowns (category, region, segment)
- Customer segmentation and profiling

**Diagnostic Analytics**
- Statistical anomaly detection (Z-score, IQR)
- Correlation analysis between metrics
- Seasonality pattern identification
- Discount effectiveness analysis
- Root cause analysis

**Predictive Analytics**
- Time series forecasting (12-month outlook)
- Customer churn prediction
- Product demand forecasting
- Revenue projections with confidence intervals
- Growth opportunity identification

**Prescriptive Analytics**
- Inventory optimization strategies
- Dynamic pricing recommendations
- Marketing budget allocation (ROI-based)
- Customer retention strategies (RFM segmentation)
- Comprehensive action plans (immediate, short-term, long-term)

### 🛠️ Technology Stack
- **Backend**: FastAPI (Python 3.12)
- **AI Framework**: LangChain + OpenAI GPT-4
- **Analytics**: Pandas, NumPy, Scikit-learn, Statsmodels
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Visualization**: Plotly.js


## 🏗️ Architecture

The system implements a hierarchical multi-agent architecture using LangChain and OpenAI GPT-4. For detailed technical design, see [ARCHITECTURE.md](docs/ARCHITECTURE.md).

```
                                            ┌─────────────────────────────────────────┐
                                            │         User Interface (Web)            │
                                            │    HTML5 + CSS3 + Vanilla JS + Plotly   │
                                            └──────────────────┬──────────────────────┘
                                                               │ REST API
                                            ┌──────────────────▼──────────────────────┐
                                            │         FastAPI Backend                 │
                                            │  ┌────────────────────────────────────┐ │
                                            │  │   Orchestrator Agent (Manager)     │ │
                                            │  │   Routes queries to specialists    │ │
                                            │  └───┬────────────────────────────┬───┘ │
                                            │      │                            │     │
                                            │  ┌───▼───────┐  ┌────────┐  ┌─────▼────┐│
                                            │  │Descriptive│  │Diagnos-│  │Predictive││
                                            │  │  Agent    │  │tic     │  │  Agent   ││
                                            │  └───────────┘  │Agent   │  └──────────┘│
                                            │                 └────────┘              │
                                            │  ┌────────────────────────────────────┐ │
                                            │  │    Prescriptive Agent              │ │
                                            │  └────────────────────────────────────┘ │
                                            └──────────────────┬──────────────────────┘
                                                               │
                                                ┌──────────────┼──────────────┐
                                                │              │              │
                                            ┌───▼────┐  ┌──────▼─────┐  ┌─────▼────┐
                                            │ 15+    │  │ Analytics  │  │  Data    │
                                            │ Tools  │  │ Modules    │  │  Layer   │
                                            └────────┘  └────────────┘  └──────────┘
```

### Agent Hierarchy
1. **Orchestrator**: Master coordinator that analyzes queries and delegates to specialists
2. **Specialized Agents**: Domain experts for each analytics type
3. **Tool Layer**: 15+ custom LangChain tools for specific operations
4. **Analytics Engine**: Core computation modules (pandas, scikit-learn, statsmodels)

## 🚀 Installation

### Prerequisites

- **Python**: 3.12 or higher
- **pip**: Latest version
- **Virtual Environment**: Recommended for isolation
- **OpenAI API Key**: Required for GPT-4 access

### Step-by-Step Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/Saifulislamsayem19/Sales-AI-Agent.git
   cd Sales-AI-Agent
   ```

2. **Create Virtual Environment**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**
   ```bash
   # Copy example environment file
   cp .env.example .env
   
   # Edit .env with your credentials
   nano .env  # or use your preferred editor
   ```

5. **Prepare Data**
   - Place your sales CSV in `data/sales_data.csv`
   - Or let the system generate sample data automatically

6. **Verify Installation**
   ```bash
   python -c "import fastapi, langchain, pandas; print('All dependencies installed!')"
   ```

## 🎯 Running the Application

### Start the Server

```bash
# From project root
python run.py 
Or
python -m app.main
```

Or using uvicorn directly:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Access the Application

Open your browser and navigate to:
- **Web Interface**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 💬 Using the AI Assistant

### Example Queries

**Descriptive Analytics:**
- "What are my total sales and profit?"
- "Show me sales trends by category"
- "Which region has the highest sales?"
- "Analyze sales performance by customer segment"

**Diagnostic Analytics:**
- "Why did sales drop last quarter?"
- "What's the impact of discounts on profitability?"
- "Are there any anomalies in my sales data?"
- "Which factors correlate with high sales?"

**Predictive Analytics:**
- "Forecast sales for the next 12 months"
- "Which customers are likely to churn?"
- "What will be the top selling products?"
- "Predict revenue for next quarter"

**Prescriptive Analytics:**
- "How should I optimize my pricing?"
- "What's the best marketing budget allocation?"
- "Recommend a customer retention strategy"
- "Give me an action plan to increase profit"

## 📊 API Endpoints

### Core Endpoints

- `GET /health` - Health check
- `POST /api/query` - Process natural language query
- `GET /api/summary` - Get sales summary
- `POST /api/forecast` - Get sales forecast

### Analytics Endpoints

- `GET /api/analytics/descriptive` - Descriptive analytics
- `GET /api/analytics/diagnostic` - Diagnostic analytics
- `GET /api/analytics/predictive` - Predictive analytics
- `GET /api/analytics/prescriptive` - Prescriptive analytics

### Utility Endpoints

- `GET /api/data/metadata` - Dataset metadata
- `POST /api/agent/reset` - Reset agent memory

## 🏗️ Project Structure

```
sales-analytics-ai-agent/
├── 
│   ├── app/
│   │   ├── agents/            # Multi-agent system
│   │   │   └── sales_agent.py # Main + specialized agents
│   │   ├── analytics/         # Four analytics modules
│   │   │   ├── descriptive.py
│   │   │   ├── diagnostic.py
│   │   │   ├── predictive.py
│   │   │   └── prescriptive.py
│   │   ├── tools/             # LangChain tools
│   │   │   └── analytics_tools.py # 15+ tools
│   │   ├── core/              # Configuration & logging
│   │   │   ├── config.py
│   │   │   └── logger.py
│   │   ├── models/            # Pydantic schemas
│   │   │   └── schemas.py
│   │   ├── utils/             # Data utilities
│   │   │   └── data_loader.py
│   │   └── main.py            # FastAPI application
│   └── data/                  # Data directory
│
├── frontend/
│   ├── index.html             # Main interface
│   ├── css/
│   │   └── styles.css         # Beautiful styling
│   └── js/
│       └── app.js             # Frontend application
│
├── logs/                      # Application logs
└── models/                    # ML models directory
├── run.py                     # Run the application form project root
├── README.md                    # Comprehensive documentation
├── ARCHITECTURE.md             # Technical architecture details
├── requirements.txt            # All Python dependencies
├── .env.example               # Configuration template
```

## 🔧 Configuration

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `OPENAI_MODEL`: Model to use (default: gpt-4o-mini)
- `DEBUG`: Enable debug mode (default: True)
- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)
- `MAX_ITERATIONS`: Max agent iterations (default: 10)
- `AGENT_TEMPERATURE`: LLM temperature (default: 0.2)
- `FORECAST_PERIODS`: Default forecast periods (default: 12)

## 📈 Analytics Features Detail

### Descriptive Analytics
- Summary statistics (totals, averages, distributions)
- Time series analysis with trends and seasonality
- Multi-dimensional breakdowns (category, region, segment)
- Product performance analysis
- Customer segmentation

### Diagnostic Analytics
- Statistical anomaly detection (Z-score, IQR methods)
- Correlation analysis between metrics
- Variance analysis across dimensions
- Seasonal pattern identification
- Discount effectiveness analysis
- Customer behavior patterns
- Root cause analysis

### Predictive Analytics
- Time series forecasting (Linear Regression, Moving Averages)
- Customer churn prediction
- Product demand forecasting
- Revenue projections with confidence intervals
- Growth opportunity identification

### Prescriptive Analytics
- Inventory optimization recommendations
- Pricing strategy optimization
- Marketing budget allocation (ROI-based)
- Customer retention strategies (RFM segmentation)
- Product bundling recommendations
- Comprehensive action plans (immediate, short-term, long-term)

## 🤖 Agent Architecture

### Main Orchestrator
Coordinates all specialized agents and tools. Routes queries to appropriate analytical modules based on intent.

### Specialized Agents
- **DescriptiveAgent**: Focuses on summarization and reporting
- **DiagnosticAgent**: Investigates causes and relationships
- **PredictiveAgent**: Generates forecasts and predictions
- **PrescriptiveAgent**: Provides recommendations and strategies

### LangChain Tools
15+ custom tools for data analysis:
- get_sales_summary
- analyze_time_trends
- analyze_by_category
- analyze_by_region
- detect_anomalies
- analyze_correlations
- analyze_discount_impact
- forecast_sales
- predict_customer_churn
- identify_growth_opportunities
- optimize_pricing
- optimize_inventory
- recommend_marketing_strategy
- recommend_retention_strategy
- get_action_plan

## 🎨 Frontend Features

- **Modern UI**: Clean, dark-themed interface
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Interactive Chat**: Natural language query interface
- **Visual Analytics**: Interactive charts using Plotly.js
- **Multi-View Dashboard**: Separate views for each analytics type
- **Real-time Updates**: Live statistics and status indicators

## 🧪 Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=backend

# Run specific test file
pytest tests/test_analytics.py
```

## 📝 Logging

Logs are stored in the `logs/` directory:
- Console output with color-coded levels
- File rotation (10MB per file)
- 30-day retention
- Automatic compression

View logs:
```bash
tail -f logs/app.log
```

## 🚨 Troubleshooting

### Common Issues

**1. OpenAI API Key Error**
```
Solution: Ensure OPENAI_API_KEY is set in .env file
```

**2. Port Already in Use**
```
Solution: Change PORT in .env or kill process using port 8000
```

**3. Data Not Loading**
```
Solution: Check data file format and location (data/sales_data.csv)
```

**4. Module Import Errors**
```bash
Solution: Ensure all dependencies are installed
pip install -r requirements.txt
```

## 📊 Performance

- Average query response: 2-5 seconds
- Concurrent requests: 50+
- Data processing: 100K+ rows efficiently
- Memory usage: ~500MB typical

## 🔒 Security

- Environment variable configuration
- No hardcoded credentials
- CORS protection
- Input validation
- Secure API endpoints

## 👥 Support

For issues and questions:
1. Check the troubleshooting section
2. Review API documentation at `/docs`
3. Check logs in `logs/app.log`

## 📄 License

This project is provided as-is for evaluation purposes.

## 🙏 Acknowledgments

- OpenAI for GPT models
- LangChain framework
- FastAPI framework
- Plotly visualization library

---

**Built with ❤️ using Python, FastAPI, LangChain, and OpenAI GPT-4**
