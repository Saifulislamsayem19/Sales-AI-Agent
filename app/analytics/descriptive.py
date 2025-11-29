"""
Descriptive Analytics Module
What has happened?
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from app.core.logger import app_logger as logger


class DescriptiveAnalytics:
    """Descriptive analytics engine"""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df
    
    def get_summary_statistics(self) -> Dict[str, Any]:
        """Get comprehensive summary statistics"""
        try:
            summary = {
                'overview': {
                    'total_sales': float(self.df['Sales'].sum()),
                    'total_profit': float(self.df['Profit'].sum()),
                    'total_orders': int(len(self.df)),
                    'total_customers': int(self.df['Customer ID'].nunique()),
                    'total_products': int(self.df['Product ID'].nunique()),
                    'avg_order_value': float(self.df['Sales'].mean()),
                    'profit_margin': float((self.df['Profit'].sum() / self.df['Sales'].sum() * 100)),
                },
                'sales_statistics': {
                    'mean': float(self.df['Sales'].mean()),
                    'median': float(self.df['Sales'].median()),
                    'std': float(self.df['Sales'].std()),
                    'min': float(self.df['Sales'].min()),
                    'max': float(self.df['Sales'].max()),
                    'q1': float(self.df['Sales'].quantile(0.25)),
                    'q3': float(self.df['Sales'].quantile(0.75)),
                },
                'profit_statistics': {
                    'mean': float(self.df['Profit'].mean()),
                    'median': float(self.df['Profit'].median()),
                    'std': float(self.df['Profit'].std()),
                    'min': float(self.df['Profit'].min()),
                    'max': float(self.df['Profit'].max()),
                }
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error in summary statistics: {e}")
            return {}
    
    def get_time_series_analysis(self, metric: str = 'Sales', frequency: str = 'M') -> Dict[str, Any]:
        """Analyze time series trends"""
        try:
        
            freq = 'ME' if frequency == 'M' else frequency
            
            # Resample by frequency
            ts_data = self.df.groupby(pd.Grouper(key='Order Date', freq=freq))[metric].agg([
                'sum', 'mean', 'count'
            ]).reset_index()
            
            ts_data = ts_data.fillna(0)
            
            # Calculate growth rates
            ts_data['growth_rate'] = ts_data['sum'].pct_change() * 100
            ts_data['growth_rate'] = ts_data['growth_rate'].fillna(0).replace([np.inf, -np.inf], 0)
            ts_data['cumulative'] = ts_data['sum'].cumsum()
            
            # Calculate moving averages
            ts_data['ma_3'] = ts_data['sum'].rolling(window=3, min_periods=1).mean()
            ts_data['ma_6'] = ts_data['sum'].rolling(window=6, min_periods=1).mean()
            
            # Convert to records with proper formatting
            records = []
            for _, row in ts_data.iterrows():
                records.append({
                    'Order_Date': row['Order Date'].strftime('%Y-%m-%d'),
                    'sum': float(row['sum']),
                    'mean': float(row['mean']),
                    'count': int(row['count']),
                    'growth_rate': float(row['growth_rate']) if not pd.isna(row['growth_rate']) else 0.0,
                    'cumulative': float(row['cumulative']),
                    'ma_3': float(row['ma_3']) if not pd.isna(row['ma_3']) else 0.0,
                    'ma_6': float(row['ma_6']) if not pd.isna(row['ma_6']) else 0.0,
                })
            
            result = {
                'time_series': records,
                'trend': self._determine_trend(ts_data['sum'].values),
                'average_growth_rate': float(ts_data['growth_rate'].mean()) if len(ts_data) > 0 else 0.0,
                'volatility': float(ts_data['sum'].std()) if len(ts_data) > 0 else 0.0,
                'peak_period': ts_data.loc[ts_data['sum'].idxmax(), 'Order Date'].strftime('%Y-%m') if len(ts_data) > 0 else 'N/A',
                'lowest_period': ts_data.loc[ts_data['sum'].idxmin(), 'Order Date'].strftime('%Y-%m') if len(ts_data) > 0 else 'N/A',
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error in time series analysis: {e}")
            return {}
    
    def get_category_analysis(self) -> Dict[str, Any]:
        """Analyze performance by category"""
        try:
            category_stats = self.df.groupby('Category').agg({
                'Sales': ['sum', 'mean', 'count'],
                'Profit': ['sum', 'mean'],
                'Quantity': 'sum',
                'Discount': 'mean'
            }).round(2)
            
            category_stats.columns = ['_'.join(col).strip() for col in category_stats.columns]
            category_stats = category_stats.reset_index()
            
            # Calculate profit margin
            category_stats['Profit_Margin'] = (
                category_stats['Profit_sum'] / category_stats['Sales_sum'] * 100
            ).round(2)
            
            # Sort by sales
            category_stats = category_stats.sort_values('Sales_sum', ascending=False)
            
            # Convert to records with clean values
            records = []
            for _, row in category_stats.iterrows():
                records.append({
                    'Category': row['Category'],
                    'Sales_sum': float(row['Sales_sum']),
                    'Sales_mean': float(row['Sales_mean']),
                    'Sales_count': int(row['Sales_count']),
                    'Profit_sum': float(row['Profit_sum']),
                    'Profit_mean': float(row['Profit_mean']),
                    'Quantity_sum': float(row['Quantity_sum']),
                    'Discount_mean': float(row['Discount_mean']),
                    'Profit_Margin': float(row['Profit_Margin'])
                })
            
            return {
                'categories': records,
                'top_category': records[0]['Category'] if records else 'N/A',
                'total_categories': len(records)
            }
            
        except Exception as e:
            logger.error(f"Error in category analysis: {e}")
            return {}
    
    def get_regional_analysis(self) -> Dict[str, Any]:
        """Analyze performance by region"""
        try:
            regional_stats = self.df.groupby('Region').agg({
                'Sales': ['sum', 'mean'],
                'Profit': ['sum', 'mean'],
                'Order ID': 'count',
                'Customer ID': 'nunique'
            }).round(2)
            
            regional_stats.columns = ['_'.join(col).strip() for col in regional_stats.columns]
            regional_stats = regional_stats.reset_index()
            regional_stats.columns = ['Region', 'Total_Sales', 'Avg_Sales', 'Total_Profit', 
                                     'Avg_Profit', 'Order_Count', 'Customer_Count']
            
            # Calculate metrics
            regional_stats['Profit_Margin'] = (
                regional_stats['Total_Profit'] / regional_stats['Total_Sales'] * 100
            ).round(2)
            regional_stats['Sales_per_Customer'] = (
                regional_stats['Total_Sales'] / regional_stats['Customer_Count']
            ).round(2)
            
            regional_stats = regional_stats.sort_values('Total_Sales', ascending=False)
            
            # Convert to clean records
            records = []
            for _, row in regional_stats.iterrows():
                records.append({
                    'Region': row['Region'],
                    'Total_Sales': float(row['Total_Sales']),
                    'Avg_Sales': float(row['Avg_Sales']),
                    'Total_Profit': float(row['Total_Profit']),
                    'Avg_Profit': float(row['Avg_Profit']),
                    'Order_Count': int(row['Order_Count']),
                    'Customer_Count': int(row['Customer_Count']),
                    'Profit_Margin': float(row['Profit_Margin']),
                    'Sales_per_Customer': float(row['Sales_per_Customer'])
                })
            
            return {
                'regions': records,
                'top_region': records[0]['Region'] if records else 'N/A',
                'total_regions': len(records)
            }
            
        except Exception as e:
            logger.error(f"Error in regional analysis: {e}")
            return {}
    
    def get_customer_segment_analysis(self) -> Dict[str, Any]:
        """Analyze customer segments"""
        try:
            segment_stats = self.df.groupby('Segment').agg({
                'Sales': ['sum', 'mean'],
                'Profit': ['sum', 'mean'],
                'Order ID': 'count',
                'Customer ID': 'nunique'
            }).round(2)
            
            segment_stats.columns = ['_'.join(col).strip() for col in segment_stats.columns]
            segment_stats = segment_stats.reset_index()
            
            segment_stats['Profit_Margin'] = (
                segment_stats['Profit_sum'] / segment_stats['Sales_sum'] * 100
            ).round(2).fillna(0)
            
            records = []
            for _, row in segment_stats.iterrows():
                records.append({k: (float(v) if isinstance(v, (np.integer, np.floating)) else 
                                   int(v) if isinstance(v, np.integer) else v) 
                               for k, v in row.to_dict().items()})
            
            return {
                'segments': records,
                'total_segments': len(records)
            }
            
        except Exception as e:
            logger.error(f"Error in segment analysis: {e}")
            return {}
    
    def get_product_analysis(self, top_n: int = 20) -> Dict[str, Any]:
        """Analyze top products"""
        try:
            product_stats = self.df.groupby(['Product ID', 'Product Name', 'Category']).agg({
                'Sales': 'sum',
                'Profit': 'sum',
                'Quantity': 'sum',
                'Order ID': 'count'
            }).round(2)
            
            product_stats = product_stats.reset_index()
            product_stats.columns = ['Product_ID', 'Product_Name', 'Category', 
                                    'Total_Sales', 'Total_Profit', 'Total_Quantity', 'Order_Count']
            
            product_stats['Profit_Margin'] = (
                product_stats['Total_Profit'] / product_stats['Total_Sales'] * 100
            ).round(2).fillna(0)
            
            top_products = product_stats.nlargest(top_n, 'Total_Sales')
            bottom_products = product_stats.nsmallest(top_n, 'Total_Sales')
            
            return {
                'top_products': [
                    {k: (float(v) if isinstance(v, (np.floating)) else int(v) if isinstance(v, np.integer) else v)
                     for k, v in row.to_dict().items()}
                    for _, row in top_products.iterrows()
                ],
                'bottom_products': [
                    {k: (float(v) if isinstance(v, (np.floating)) else int(v) if isinstance(v, np.integer) else v)
                     for k, v in row.to_dict().items()}
                    for _, row in bottom_products.iterrows()
                ],
                'total_products': len(product_stats)
            }
            
        except Exception as e:
            logger.error(f"Error in product analysis: {e}")
            return {}
    
    def _determine_trend(self, values: np.ndarray) -> str:
        """Determine overall trend from values"""
        if len(values) < 2:
            return "insufficient_data"
        
        # linear regression slope
        x = np.arange(len(values))
        slope = np.polyfit(x, values, 1)[0]
        
        if slope > 0.05:
            return "increasing"
        elif slope < -0.05:
            return "decreasing"
        else:
            return "stable"
    
    def get_comprehensive_report(self) -> Dict[str, Any]:
        """Get comprehensive descriptive analytics report"""
        return {
            'summary_statistics': self.get_summary_statistics(),
            'time_series_analysis': self.get_time_series_analysis(),
            'category_analysis': self.get_category_analysis(),
            'regional_analysis': self.get_regional_analysis(),
            'customer_segment_analysis': self.get_customer_segment_analysis(),
            'product_analysis': self.get_product_analysis(),
        }
