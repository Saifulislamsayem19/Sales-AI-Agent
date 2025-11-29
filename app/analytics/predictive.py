"""
Predictive Analytics Module
What is likely to happen?
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from app.core.logger import app_logger as logger


class PredictiveAnalytics:
    """Predictive analytics engine"""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df
    
    def forecast_sales(self, periods: int = 12, frequency: str = 'M') -> Dict[str, Any]:
        """Forecast sales using simple trend analysis"""
        try:
            # frequency mapping
            freq = 'ME' if frequency == 'M' else frequency
            
            # Aggregate data
            ts_data = self.df.groupby(pd.Grouper(key='Order Date', freq=freq))['Sales'].sum()
            ts_data = ts_data.reset_index()
            
            # Linear trend forecast
            X = np.arange(len(ts_data)).reshape(-1, 1)
            y = ts_data['Sales'].values
            
            # Fit model
            model = LinearRegression()
            model.fit(X, y)
            
            # Generate forecasts
            future_X = np.arange(len(ts_data), len(ts_data) + periods).reshape(-1, 1)
            forecasts = model.predict(future_X)
            
            # Calculate prediction intervals
            residuals = y - model.predict(X)
            std_error = np.std(residuals)
            
            # Generate future dates
            last_date = ts_data['Order Date'].max()
            if freq == 'ME':
                future_dates = pd.date_range(
                    start=last_date + pd.DateOffset(months=1),
                    periods=periods,
                    freq=freq
                )
            else:
                future_dates = pd.date_range(
                    start=last_date + pd.DateOffset(days=1),
                    periods=periods,
                    freq=frequency
                )
            
            forecast_data = []
            for i, (date, forecast) in enumerate(zip(future_dates, forecasts)):
                forecast_data.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'forecast': float(forecast),
                    'lower_bound': float(forecast - 1.96 * std_error),
                    'upper_bound': float(forecast + 1.96 * std_error)
                })
            
            trend = "increasing" if model.coef_[0] > 0 else "decreasing"
            
            return {
                'forecasts': forecast_data,
                'trend': trend,
                'trend_coefficient': float(model.coef_[0]),
                'model_score': float(model.score(X, y)),
                'periods': periods,
                'frequency': frequency
            }
            
        except Exception as e:
            logger.error(f"Error forecasting sales: {e}")
            return {'forecasts': [], 'trend': 'unknown', 'trend_coefficient': 0.0, 'model_score': 0.0, 'periods': periods, 'frequency': frequency}


    def predict_customer_churn(self) -> Dict[str, Any]:
        """Predict customer churn risk"""
        try:
            # Calculate customer metrics
            customer_data = self.df.groupby('Customer ID').agg({
                'Order Date': ['min', 'max', 'count'],
                'Sales': ['sum', 'mean'],
                'Profit': 'sum'
            })
            
            # Flatten column names
            customer_data.columns = ['_'.join(col) if isinstance(col, tuple) else col for col in customer_data.columns]
            customer_data = customer_data.reset_index()
            
            # Rename columns for clarity
            customer_data.columns = ['Customer_ID', 'Order_Date_min', 'Order_Date_max', 'Order_Date_count',
                                    'Sales_sum', 'Sales_mean', 'Profit_sum']
            
            # Calculate days since last purchase
            customer_data['days_since_last'] = (
                pd.Timestamp.now() - pd.to_datetime(customer_data['Order_Date_max'])
            ).dt.days
            
            customer_data['customer_lifetime'] = (
                pd.to_datetime(customer_data['Order_Date_max']) - 
                pd.to_datetime(customer_data['Order_Date_min'])
            ).dt.days
            
            # Churn risk scoring
            customer_data['churn_risk'] = 'Low'
            customer_data.loc[customer_data['days_since_last'] > 180, 'churn_risk'] = 'High'
            customer_data.loc[
                (customer_data['days_since_last'] > 90) & (customer_data['days_since_last'] <= 180),
                'churn_risk'
            ] = 'Medium'
            
            churn_summary = customer_data['churn_risk'].value_counts().to_dict()
            high_risk_customers = customer_data[customer_data['churn_risk'] == 'High']
            
            # Convert to clean records
            high_risk_records = []
            for _, row in high_risk_customers.head(20).iterrows():
                high_risk_records.append({
                    'Customer_ID': str(row['Customer_ID']),
                    'Order_Date_count': int(row['Order_Date_count']),
                    'Sales_sum': float(row['Sales_sum']),
                    'days_since_last': int(row['days_since_last']),
                    'churn_risk': str(row['churn_risk'])
                })
            
            return {
                'churn_summary': churn_summary,
                'high_risk_customers': high_risk_records,
                'total_customers': len(customer_data),
                'churn_rate': float(len(high_risk_customers) / len(customer_data) * 100)
            }
            
        except Exception as e:
            logger.error(f"Error predicting churn: {e}")
            return {'churn_summary': {}, 'high_risk_customers': [], 'total_customers': 0, 'churn_rate': 0.0}
    
    def predict_product_demand(self, category: str = None) -> Dict[str, Any]:
        """Predict product demand"""
        try:
            if category:
                data = self.df[self.df['Category'] == category].copy()
            else:
                data = self.df.copy()
            
            # Aggregate by product and time
            product_demand = data.groupby(['Product ID', 'Product Name']).agg({
                'Quantity': 'sum',
                'Order ID': 'count',
                'Sales': 'sum'
            }).reset_index()
            
            product_demand.columns = ['Product_ID', 'Product_Name', 'Total_Quantity', 
                                     'Order_Count', 'Total_Sales']
            
            # Calculate velocity
            product_demand['Velocity'] = (
                product_demand['Total_Quantity'] / product_demand['Order_Count']
            ).round(2)
            
            # Sort by predicted demand 
            product_demand = product_demand.sort_values('Total_Sales', ascending=False)
            
            return {
                'high_demand_products': product_demand.head(20).to_dict('records'),
                'low_demand_products': product_demand.tail(10).to_dict('records'),
                'category': category or 'All'
            }
            
        except Exception as e:
            logger.error(f"Error predicting product demand: {e}")
            return {}
    
    def predict_revenue(self, months_ahead: int = 3) -> Dict[str, Any]:
        """Predict future revenue"""
        try:
            # Monthly revenue
            monthly_revenue = self.df.groupby(
                pd.Grouper(key='Order Date', freq='M')
            )['Sales'].sum().reset_index()
            
            # Simple moving average prediction
            ma_window = min(6, len(monthly_revenue))
            moving_avg = monthly_revenue['Sales'].rolling(window=ma_window).mean().iloc[-1]
            
            # Growth rate
            recent_growth = monthly_revenue['Sales'].pct_change().tail(6).mean()
            
            predictions = []
            current_value = moving_avg
            
            for month in range(1, months_ahead + 1):
                current_value = current_value * (1 + recent_growth)
                predictions.append({
                    'month': month,
                    'predicted_revenue': float(current_value),
                    'growth_assumption': float(recent_growth * 100)
                })
            
            return {
                'revenue_predictions': predictions,
                'baseline_revenue': float(moving_avg),
                'assumed_growth_rate': float(recent_growth * 100),
                'confidence': 'medium'  
            }
            
        except Exception as e:
            logger.error(f"Error predicting revenue: {e}")
            return {}
    
    def identify_growth_opportunities(self) -> Dict[str, Any]:
        """Identify growth opportunities"""
        try:
            opportunities = []
            
            # Category opportunities
            category_growth = self.df.groupby(['Category', 'Year'])['Sales'].sum().reset_index()
            category_growth['growth_rate'] = category_growth.groupby('Category')['Sales'].pct_change()
            
            high_growth_categories = category_growth.groupby('Category')['growth_rate'].mean().sort_values(ascending=False)
            
            for cat in high_growth_categories.head(3).index:
                opportunities.append({
                    'type': 'Category',
                    'name': cat,
                    'growth_rate': float(high_growth_categories[cat] * 100),
                    'recommendation': f'Expand product line in {cat}'
                })
            
            # Regional opportunities
            regional_performance = self.df.groupby('Region').agg({
                'Sales': 'sum',
                'Profit': 'sum',
                'Customer ID': 'nunique'
            })
            
            regional_performance['profit_margin'] = (
                regional_performance['Profit'] / regional_performance['Sales'] * 100
            )
            
            underserved_regions = regional_performance.nsmallest(2, 'Sales')
            
            for region in underserved_regions.index:
                opportunities.append({
                    'type': 'Region',
                    'name': region,
                    'potential': f'Increase market penetration',
                    'current_sales': float(underserved_regions.loc[region, 'Sales'])
                })
            
            return {
                'opportunities': opportunities,
                'total_opportunities': len(opportunities)
            }
            
        except Exception as e:
            logger.error(f"Error identifying opportunities: {e}")
            return {}
