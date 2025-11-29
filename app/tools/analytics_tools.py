"""
LangChain tools for sales analytics agents
"""
from langchain.tools import tool
from typing import Dict, Any, Optional
import json
from app.utils.data_loader import data_loader
from app.analytics.descriptive import DescriptiveAnalytics
from app.analytics.diagnostic import DiagnosticAnalytics
from app.analytics.predictive import PredictiveAnalytics
from app.analytics.prescriptive import PrescriptiveAnalytics
from app.core.logger import app_logger as logger


@tool
def get_sales_summary() -> str:
    """Get a comprehensive summary of sales data including total sales, profit, orders, and key metrics."""
    try:
        df = data_loader.get_data()
        if df is None or len(df) == 0:
            return "No data available. Please load data first."
        
        analytics = DescriptiveAnalytics(df)
        summary = analytics.get_summary_statistics()
        
        return json.dumps(summary, indent=2)
    except Exception as e:
        logger.error(f"Error in get_sales_summary: {e}")
        return f"Error: {str(e)}"


@tool
def analyze_time_trends(metric: str = "Sales", frequency: str = "M") -> str:
    """Analyze time series trends for a specific metric. 
    
    Args:
        metric: The metric to analyze (Sales, Profit, Quantity)
        frequency: Time frequency (D=daily, W=weekly, M=monthly, Q=quarterly, Y=yearly)
    """
    try:
        df = data_loader.get_data()
        if df is None:
            return "No data available."
        
        analytics = DescriptiveAnalytics(df)
        result = analytics.get_time_series_analysis(metric, frequency)
        
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error: {str(e)}"


@tool
def analyze_by_category() -> str:
    """Analyze sales performance by product category."""
    try:
        df = data_loader.get_data()
        if df is None:
            return "No data available."
        
        analytics = DescriptiveAnalytics(df)
        result = analytics.get_category_analysis()
        
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error: {str(e)}"


@tool
def analyze_by_region() -> str:
    """Analyze sales performance by geographic region."""
    try:
        df = data_loader.get_data()
        if df is None:
            return "No data available."
        
        analytics = DescriptiveAnalytics(df)
        result = analytics.get_regional_analysis()
        
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error: {str(e)}"


@tool
def detect_anomalies(metric: str = "Sales", threshold: float = 3.0) -> str:
    """Detect anomalies or outliers in sales data.
    
    Args:
        metric: The metric to check (Sales, Profit, Quantity)
        threshold: Z-score threshold for anomaly detection (default 3.0)
    """
    try:
        df = data_loader.get_data()
        if df is None:
            return "No data available."
        
        analytics = DiagnosticAnalytics(df)
        result = analytics.find_anomalies(metric, method='zscore', threshold=threshold)
        
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error: {str(e)}"


@tool
def analyze_correlations() -> str:
    """Analyze correlations between different sales metrics to understand relationships."""
    try:
        df = data_loader.get_data()
        if df is None:
            return "No data available."
        
        analytics = DiagnosticAnalytics(df)
        result = analytics.analyze_correlations()
        
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error: {str(e)}"


@tool
def analyze_discount_impact() -> str:
    """Analyze the impact of discounts on sales and profitability."""
    try:
        df = data_loader.get_data()
        if df is None:
            return "No data available."
        
        analytics = DiagnosticAnalytics(df)
        result = analytics.analyze_discount_impact()
        
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error: {str(e)}"


@tool
def forecast_sales(periods: int = 12) -> str:
    """Forecast future sales for the specified number of periods.
    
    Args:
        periods: Number of periods to forecast (default 12 months)
    """
    try:
        df = data_loader.get_data()
        if df is None:
            return "No data available."
        
        analytics = PredictiveAnalytics(df)
        result = analytics.forecast_sales(periods=periods)
        
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error: {str(e)}"


@tool
def predict_customer_churn() -> str:
    """Predict which customers are at risk of churning based on their purchase behavior."""
    try:
        df = data_loader.get_data()
        if df is None:
            return "No data available."
        
        analytics = PredictiveAnalytics(df)
        result = analytics.predict_customer_churn()
        
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error: {str(e)}"


@tool
def identify_growth_opportunities() -> str:
    """Identify potential growth opportunities in categories, regions, or products."""
    try:
        df = data_loader.get_data()
        if df is None:
            return "No data available."
        
        analytics = PredictiveAnalytics(df)
        result = analytics.identify_growth_opportunities()
        
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error: {str(e)}"


@tool
def optimize_pricing() -> str:
    """Get pricing optimization recommendations based on current performance."""
    try:
        df = data_loader.get_data()
        if df is None:
            return "No data available."
        
        analytics = PrescriptiveAnalytics(df)
        result = analytics.optimize_pricing()
        
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error: {str(e)}"


@tool
def optimize_inventory() -> str:
    """Get inventory optimization recommendations for products."""
    try:
        df = data_loader.get_data()
        if df is None:
            return "No data available."
        
        analytics = PrescriptiveAnalytics(df)
        result = analytics.optimize_inventory()
        
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error: {str(e)}"


@tool
def recommend_marketing_strategy() -> str:
    """Get marketing budget allocation recommendations based on regional ROI."""
    try:
        df = data_loader.get_data()
        if df is None:
            return "No data available."
        
        analytics = PrescriptiveAnalytics(df)
        result = analytics.optimize_marketing_spend()
        
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error: {str(e)}"


@tool
def recommend_retention_strategy() -> str:
    """Get customer retention strategy recommendations based on customer segmentation."""
    try:
        df = data_loader.get_data()
        if df is None:
            return "No data available."
        
        analytics = PrescriptiveAnalytics(df)
        result = analytics.recommend_customer_retention_strategy()
        
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error: {str(e)}"


@tool
def get_action_plan() -> str:
    """Generate a comprehensive action plan with immediate, short-term, and long-term recommendations."""
    try:
        df = data_loader.get_data()
        if df is None:
            return "No data available."
        
        analytics = PrescriptiveAnalytics(df)
        result = analytics.generate_action_plan()
        
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error: {str(e)}"


# List of all tools
ALL_TOOLS = [
    get_sales_summary,
    analyze_time_trends,
    analyze_by_category,
    analyze_by_region,
    detect_anomalies,
    analyze_correlations,
    analyze_discount_impact,
    forecast_sales,
    predict_customer_churn,
    identify_growth_opportunities,
    optimize_pricing,
    optimize_inventory,
    recommend_marketing_strategy,
    recommend_retention_strategy,
    get_action_plan,
]
