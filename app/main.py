"""
FastAPI Application - Sales Analytics AI Agent
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
from datetime import datetime
import os
from pathlib import Path

from app.core.config import settings
from app.core.logger import app_logger as logger
from app.models.schemas import (
    QueryRequest, QueryResponse, HealthResponse,
    ForecastRequest, ForecastResponse,
    SalesMetrics
)
from app.agents.sales_agent import sales_agent
from app.utils.data_loader import data_loader
from app.utils.json_utils import clean_for_json
from app.analytics.descriptive import DescriptiveAnalytics
from app.analytics.diagnostic import DiagnosticAnalytics
from app.analytics.predictive import PredictiveAnalytics
from app.analytics.prescriptive import PrescriptiveAnalytics

# Get absolute paths
BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_PATH = BASE_DIR / "templates"
FRONTEND_HTML = FRONTEND_PATH / "index.html"
STATIC_DIR = BASE_DIR / "static"

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Advanced AI-powered sales analytics system with multi-agent architecture"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
if FRONTEND_PATH.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Frontend path: {FRONTEND_PATH}")
    logger.info(f"Frontend exists: {FRONTEND_PATH.exists()}")
    
    # Load data
    try:
        data_loader.load_data()
        logger.info("Data loaded successfully")
    except Exception as e:
        logger.error(f"Error loading data: {e}")


@app.get("/")
async def read_root():
    """Serve the frontend HTML"""
    if FRONTEND_HTML.exists():
        return FileResponse(str(FRONTEND_HTML))
    return {
        "message": "Sales Analytics AI Agent API",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    df = data_loader.get_data()
    
    return HealthResponse(
        status="healthy",
        version=settings.APP_VERSION,
        timestamp=datetime.now(),
        data_loaded=df is not None and len(df) > 0,
        agents_active=True
    )


@app.post("/api/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Process user query using AI agent"""
    try:
        logger.info(f"Processing query: {request.query}")
        
        # Process query through agent
        result = await sales_agent.process_query(
            query=request.query,
            context=request.context
        )
        
        return QueryResponse(**result)
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/summary", response_model=SalesMetrics)
async def get_summary():
    """Get sales summary statistics"""
    try:
        df = data_loader.get_data()
        if df is None:
            raise HTTPException(status_code=404, detail="No data loaded")
        
        analytics = DescriptiveAnalytics(df)
        summary = analytics.get_summary_statistics()
        
        return SalesMetrics(
            total_sales=summary['overview']['total_sales'],
            total_orders=summary['overview']['total_orders'],
            total_customers=summary['overview']['total_customers'],
            avg_order_value=summary['overview']['avg_order_value'],
            total_profit=summary['overview']['total_profit'],
            profit_margin=summary['overview']['profit_margin']
        )
        
    except Exception as e:
        logger.error(f"Error getting summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/forecast", response_model=ForecastResponse)
async def forecast_sales_endpoint(request: ForecastRequest):
    """Forecast sales"""
    try:
        df = data_loader.get_data()
        if df is None:
            raise HTTPException(status_code=404, detail="No data loaded")
        
        analytics = PredictiveAnalytics(df)
        result = analytics.forecast_sales(
            periods=request.periods,
            frequency=request.frequency
        )
        
        return ForecastResponse(
            metric=request.metric,
            forecast=result['forecasts'],
            confidence_intervals=[],
            model_metrics={'r2_score': result.get('model_score', 0.0)},
            trend=result['trend']
        )
        
    except Exception as e:
        logger.error(f"Error forecasting: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analytics/descriptive")
async def get_descriptive_analytics():
    """Get comprehensive descriptive analytics"""
    try:
        df = data_loader.get_data()
        if df is None:
            raise HTTPException(status_code=404, detail="No data loaded")
        
        analytics = DescriptiveAnalytics(df)
        result = analytics.get_comprehensive_report()
        return clean_for_json(result)  
        
    except Exception as e:
        logger.error(f"Error in descriptive analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analytics/diagnostic")
async def get_diagnostic_analytics():
    """Get diagnostic analytics"""
    try:
        df = data_loader.get_data()
        if df is None:
            raise HTTPException(status_code=404, detail="No data loaded")
        
        analytics = DiagnosticAnalytics(df)
        
        result = {
            'anomalies': analytics.find_anomalies(),
            'correlations': analytics.analyze_correlations(),
            'seasonality': analytics.analyze_seasonality(),
            'discount_impact': analytics.analyze_discount_impact(),
            'customer_behavior': analytics.analyze_customer_behavior()
        }
        
        return clean_for_json(result)  
        
    except Exception as e:
        logger.error(f"Error in diagnostic analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analytics/predictive")
async def get_predictive_analytics():
    """Get predictive analytics"""
    try:
        df = data_loader.get_data()
        if df is None:
            raise HTTPException(status_code=404, detail="No data loaded")
        
        analytics = PredictiveAnalytics(df)
        
        result = {
            'sales_forecast': analytics.forecast_sales(periods=12),
            'churn_prediction': analytics.predict_customer_churn(),
            'growth_opportunities': analytics.identify_growth_opportunities(),
            'revenue_prediction': analytics.predict_revenue(months_ahead=6)
        }
        
        return clean_for_json(result)  
        
    except Exception as e:
        logger.error(f"Error in predictive analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analytics/prescriptive")
async def get_prescriptive_analytics():
    """Get prescriptive analytics and recommendations"""
    try:
        df = data_loader.get_data()
        if df is None:
            raise HTTPException(status_code=404, detail="No data loaded")
        
        analytics = PrescriptiveAnalytics(df)
        
        result = {
            'pricing_optimization': analytics.optimize_pricing(),
            'inventory_optimization': analytics.optimize_inventory(),
            'marketing_optimization': analytics.optimize_marketing_spend(),
            'retention_strategy': analytics.recommend_customer_retention_strategy(),
            'action_plan': analytics.generate_action_plan()
        }
        
        return clean_for_json(result)  
        
    except Exception as e:
        logger.error(f"Error in prescriptive analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/data/metadata")
async def get_data_metadata():
    """Get dataset metadata"""
    try:
        metadata = data_loader.get_metadata()
        if not metadata:
            raise HTTPException(status_code=404, detail="No data loaded")
        
        return metadata
        
    except Exception as e:
        logger.error(f"Error getting metadata: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/agent/reset")
async def reset_agent():
    """Reset agent conversation memory"""
    try:
        sales_agent.reset_conversation()
        return {"message": "Agent memory reset successfully"}
        
    except Exception as e:
        logger.error(f"Error resetting agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
