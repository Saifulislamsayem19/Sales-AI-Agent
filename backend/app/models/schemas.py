"""
Pydantic models for API requests and responses
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class AnalyticsType(str, Enum):
    """Analytics types"""
    DESCRIPTIVE = "descriptive"
    DIAGNOSTIC = "diagnostic"
    PREDICTIVE = "predictive"
    PRESCRIPTIVE = "prescriptive"


class QueryRequest(BaseModel):
    """User query request"""
    query: str = Field(..., description="User's question or request")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Additional context")
    analytics_type: Optional[AnalyticsType] = Field(default=None, description="Specific analytics type requested")


class QueryResponse(BaseModel):
    """Query response"""
    answer: str = Field(..., description="Agent's response")
    analytics_type: str = Field(..., description="Type of analytics performed")
    insights: List[str] = Field(default=[], description="Key insights")
    visualizations: Optional[List[Dict[str, Any]]] = Field(default=None, description="Visualization data")
    recommendations: Optional[List[str]] = Field(default=None, description="Actionable recommendations")
    confidence: Optional[float] = Field(default=None, description="Confidence score")
    execution_time: float = Field(..., description="Time taken to process")


class SalesMetrics(BaseModel):
    """Sales metrics model"""
    total_sales: float
    total_orders: int
    total_customers: int
    avg_order_value: float
    total_profit: float
    profit_margin: float
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None


class ForecastRequest(BaseModel):
    """Forecast request"""
    metric: str = Field(default="Sales", description="Metric to forecast")
    periods: int = Field(default=12, description="Number of periods to forecast")
    frequency: str = Field(default="M", description="Frequency (D, W, M, Q, Y)")
    confidence_level: float = Field(default=0.95, description="Confidence level")


class ForecastResponse(BaseModel):
    """Forecast response"""
    metric: str
    forecast: List[Dict[str, Any]]
    confidence_intervals: List[Dict[str, Any]]
    model_metrics: Dict[str, float]  
    trend: str
    seasonality: Optional[str] = None
    model_config = {"protected_namespaces": ()}


class AnomalyDetectionRequest(BaseModel):
    """Anomaly detection request"""
    metric: str = Field(default="Sales", description="Metric to check for anomalies")
    sensitivity: float = Field(default=0.05, description="Sensitivity level")
    window: int = Field(default=30, description="Rolling window size")


class AnomalyDetectionResponse(BaseModel):
    """Anomaly detection response"""
    anomalies: List[Dict[str, Any]]
    anomaly_count: int
    anomaly_percentage: float
    severity_distribution: Dict[str, int]


class SegmentationRequest(BaseModel):
    """Customer/Product segmentation request"""
    segmentation_type: str = Field(..., description="Type of segmentation (customer, product)")
    n_clusters: int = Field(default=5, description="Number of clusters")
    features: Optional[List[str]] = Field(default=None, description="Features to use")


class SegmentationResponse(BaseModel):
    """Segmentation response"""
    segments: List[Dict[str, Any]]
    segment_profiles: List[Dict[str, Any]]
    silhouette_score: float
    recommendations: List[str]


class ComparisonRequest(BaseModel):
    """Comparison analysis request"""
    dimension: str = Field(..., description="Dimension to compare (Region, Category, Segment)")
    metric: str = Field(default="Sales", description="Metric to compare")
    top_n: int = Field(default=10, description="Number of top items")


class ComparisonResponse(BaseModel):
    """Comparison response"""
    comparison_data: List[Dict[str, Any]]
    top_performers: List[Dict[str, Any]]
    bottom_performers: List[Dict[str, Any]]
    insights: List[str]


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    timestamp: datetime
    data_loaded: bool
    agents_active: bool
