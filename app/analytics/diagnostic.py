"""
Diagnostic Analytics Module
Why did it happen?
"""
import pandas as pd
import numpy as np
from scipy import stats
from typing import Dict, Any, List
from app.core.logger import app_logger as logger


class DiagnosticAnalytics:
    """Diagnostic analytics engine"""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df
    
    def find_anomalies(self, metric: str = 'Sales', method: str = 'zscore', threshold: float = 3.0) -> Dict[str, Any]:
        """Detect anomalies in data"""
        try:
            if method == 'zscore':
                z_scores = np.abs(stats.zscore(self.df[metric]))
                anomalies = self.df[z_scores > threshold].copy()
            elif method == 'iqr':
                Q1 = self.df[metric].quantile(0.25)
                Q3 = self.df[metric].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                anomalies = self.df[(self.df[metric] < lower_bound) | (self.df[metric] > upper_bound)].copy()
            else:
                anomalies = pd.DataFrame()
            
            if len(anomalies) > 0:
                anomalies['anomaly_score'] = np.abs(stats.zscore(anomalies[metric]))
                anomalies = anomalies.sort_values('anomaly_score', ascending=False)
            
            return {
                'total_anomalies': len(anomalies),
                'anomaly_percentage': float(len(anomalies) / len(self.df) * 100),
                'anomalies': anomalies.head(20).to_dict('records') if len(anomalies) > 0 else [],
                'method': method,
                'threshold': threshold
            }
            
        except Exception as e:
            logger.error(f"Error detecting anomalies: {e}")
            return {}
    
    def analyze_correlations(self, metrics: List[str] = None) -> Dict[str, Any]:
        """Analyze correlations between metrics"""
        try:
            if metrics is None:
                metrics = ['Sales', 'Profit', 'Quantity', 'Discount', 'Shipping Cost']
            
            # Filter numeric columns
            numeric_df = self.df[metrics].select_dtypes(include=[np.number])
            
            # Calculate correlation matrix
            corr_matrix = numeric_df.corr()
            
            # Find strong correlations
            strong_correlations = []
            for i in range(len(corr_matrix.columns)):
                for j in range(i + 1, len(corr_matrix.columns)):
                    corr_value = corr_matrix.iloc[i, j]
                    if abs(corr_value) > 0.5:
                        strong_correlations.append({
                            'metric1': corr_matrix.columns[i],
                            'metric2': corr_matrix.columns[j],
                            'correlation': float(corr_value),
                            'strength': 'strong positive' if corr_value > 0.7 else 'strong negative' if corr_value < -0.7 else 'moderate'
                        })
            
            # Clean correlation matrix
            clean_matrix = {}
            for col in corr_matrix.columns:
                clean_matrix[col] = {}
                for row in corr_matrix.index:
                    val = corr_matrix.loc[row, col]
                    clean_matrix[col][row] = float(val) if not pd.isna(val) else 0.0
            
            return {
                'correlation_matrix': clean_matrix,
                'strong_correlations': sorted(strong_correlations, key=lambda x: abs(x['correlation']), reverse=True),
                'metrics_analyzed': metrics
            }
            
        except Exception as e:
            logger.error(f"Error analyzing correlations: {e}")
            return {}


    def perform_variance_analysis(self, dimension: str, metric: str = 'Sales') -> Dict[str, Any]:
        """Perform variance analysis across dimensions"""
        try:
            overall_mean = float(self.df[metric].mean())
            
            grouped = self.df.groupby(dimension)[metric].agg(['mean', 'std', 'count'])
            grouped['variance'] = grouped['std'] ** 2
            grouped['variance_from_mean'] = ((grouped['mean'] - overall_mean) / overall_mean * 100).round(2)
            
            grouped = grouped.reset_index()
            grouped = grouped.sort_values('variance_from_mean', ascending=False)
            
            # Clean the data format
            records = []
            for _, row in grouped.iterrows():
                records.append({
                    dimension: str(row[dimension]),
                    'mean': float(row['mean']),
                    'std': float(row['std']),
                    'count': int(row['count']),
                    'variance': float(row['variance']),
                    'variance_from_mean': float(row['variance_from_mean'])
                })
            
            # Statistical test (ANOVA TEST)
            groups = [group[metric].values for name, group in self.df.groupby(dimension)]
            f_stat, p_value = stats.f_oneway(*groups)
            
            return {
                'variance_analysis': records,
                'overall_mean': overall_mean,
                'anova_results': {
                    'f_statistic': float(f_stat),
                    'p_value': float(p_value),
                    'significant': bool(p_value < 0.05)
                },
                'dimension': dimension,
                'metric': metric
            }
            
        except Exception as e:
            logger.error(f"Error in variance analysis: {e}")
            return {}
    
    def analyze_seasonality(self, metric: str = 'Sales') -> Dict[str, Any]:
        """Analyze seasonal patterns"""
        try:
            # Monthly analysis
            monthly = self.df.groupby('Month')[metric].agg(['mean', 'std']).reset_index()
            monthly['cv'] = (monthly['std'] / monthly['mean'] * 100).round(2)
            
            # Quarterly analysis
            quarterly = self.df.groupby('Quarter')[metric].agg(['mean', 'std']).reset_index()
            
            # Day of week analysis
            dow = self.df.groupby('Day_of_Week')[metric].agg(['mean', 'std']).reset_index()
            dow['Day_Name'] = dow['Day_of_Week'].map({
                0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday',
                4: 'Friday', 5: 'Saturday', 6: 'Sunday'
            })
            
            return {
                'monthly_pattern': monthly.to_dict('records'),
                'quarterly_pattern': quarterly.to_dict('records'),
                'day_of_week_pattern': dow.to_dict('records'),
                'has_seasonality': monthly['mean'].std() > monthly['mean'].mean() * 0.1
            }
            
        except Exception as e:
            logger.error(f"Error analyzing seasonality: {e}")
            return {}
    
    def analyze_discount_impact(self) -> Dict[str, Any]:
        """Analyze impact of discounts on sales and profit"""
        try:
            # Create discount bins
            self.df['Discount_Bin'] = pd.cut(
                self.df['Discount'],
                bins=[-0.01, 0.0, 0.1, 0.2, 0.3, 1.0],
                labels=['No Discount', '0-10%', '10-20%', '20-30%', '30%+']
            )
            
            discount_analysis = self.df.groupby('Discount_Bin', observed=True).agg({
                'Sales': ['sum', 'mean', 'count'],
                'Profit': ['sum', 'mean'],
                'Quantity': 'sum'
            }).round(2)
            
            discount_analysis.columns = ['_'.join(col).strip() for col in discount_analysis.columns]
            discount_analysis = discount_analysis.reset_index()
            
            # Calculate profit margin for each discount level
            discount_analysis['Profit_Margin'] = (
                discount_analysis['Profit_sum'] / discount_analysis['Sales_sum'] * 100
            ).round(2)
            
            # Calculate ROI
            discount_analysis['ROI'] = (
                discount_analysis['Profit_sum'] / discount_analysis['Sales_sum']
            ).round(4)
            
            return {
                'discount_impact': discount_analysis.to_dict('records'),
                'recommendation': self._get_discount_recommendation(discount_analysis)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing discount impact: {e}")
            return {}
    
    def analyze_customer_behavior(self) -> Dict[str, Any]:
        """Analyze customer purchasing behavior"""
        try:
            # Customer metrics
            customer_metrics = self.df.groupby('Customer ID').agg({
                'Order ID': 'count',
                'Sales': 'sum',
                'Profit': 'sum',
                'Order Date': ['min', 'max']
            })
            
            customer_metrics.columns = ['_'.join(col).strip() for col in customer_metrics.columns]
            customer_metrics = customer_metrics.reset_index()
            customer_metrics.columns = ['Customer_ID', 'Order_Count', 'Total_Sales', 
                                       'Total_Profit', 'First_Purchase', 'Last_Purchase']
            
            # Calculate customer lifetime
            customer_metrics['Customer_Lifetime_Days'] = (
                pd.to_datetime(customer_metrics['Last_Purchase']) - 
                pd.to_datetime(customer_metrics['First_Purchase'])
            ).dt.days
            
            # Calculate average order value
            customer_metrics['Avg_Order_Value'] = (
                customer_metrics['Total_Sales'] / customer_metrics['Order_Count']
            ).round(2)
            
            # Segment customers
            customer_metrics['Segment'] = pd.cut(
                customer_metrics['Order_Count'],
                bins=[0, 2, 5, 10, float('inf')],
                labels=['Occasional', 'Regular', 'Frequent', 'VIP']
            )
            
            segment_summary = customer_metrics.groupby('Segment', observed=True).agg({
                'Customer_ID': 'count',
                'Total_Sales': 'sum',
                'Avg_Order_Value': 'mean'
            }).round(2)
            
            return {
                'customer_segments': segment_summary.to_dict(),
                'top_customers': customer_metrics.nlargest(10, 'Total_Sales').to_dict('records'),
                'average_lifetime_value': float(customer_metrics['Total_Sales'].mean()),
                'average_order_count': float(customer_metrics['Order_Count'].mean())
            }
            
        except Exception as e:
            logger.error(f"Error analyzing customer behavior: {e}")
            return {}
    
    def root_cause_analysis(self, metric: str = 'Sales', period: str = None) -> Dict[str, Any]:
        """Perform root cause analysis for metric changes"""
        try:
            insights = []
            
            # Time-based analysis
            if period:
                period_data = self.df[self.df['Order Date'].dt.to_period('M').astype(str) == period]
                overall_avg = self.df[metric].mean()
                period_avg = period_data[metric].mean()
                
                if period_avg < overall_avg * 0.9:
                    insights.append(f"The {metric} in {period} was {((period_avg/overall_avg - 1) * 100):.1f}% below average")
            
            # Category impact
            category_impact = self.df.groupby('Category')[metric].mean().sort_values(ascending=True)
            if len(category_impact) > 0:
                lowest_category = category_impact.index[0]
                insights.append(f"Category '{lowest_category}' has the lowest average {metric}")
            
            # Discount impact
            high_discount = self.df[self.df['Discount'] > 0.2]
            if len(high_discount) > 0:
                insights.append(f"High discounts (>20%) applied to {len(high_discount)} orders")
            
            # Regional variations
            regional = self.df.groupby('Region')[metric].mean()
            regional_cv = (regional.std() / regional.mean() * 100)
            if regional_cv > 20:
                insights.append(f"High regional variation detected (CV: {regional_cv:.1f}%)")
            
            return {
                'insights': insights,
                'contributing_factors': self._identify_contributing_factors(metric),
                'recommendations': self._generate_diagnostic_recommendations(insights)
            }
            
        except Exception as e:
            logger.error(f"Error in root cause analysis: {e}")
            return {}
    
    def _get_discount_recommendation(self, discount_df: pd.DataFrame) -> str:
        """Generate discount strategy recommendation"""
        try:
            optimal = discount_df.loc[discount_df['Profit_Margin'].idxmax()]
            return f"Optimal discount range: {optimal['Discount_Bin']} with {optimal['Profit_Margin']:.1f}% profit margin"
        except:
            return "Unable to determine optimal discount strategy"
    
    def _identify_contributing_factors(self, metric: str) -> List[Dict[str, Any]]:
        """Identify factors contributing to metric performance"""
        factors = []
        
        try:
            # Discount factor
            discount_corr = self.df[[metric, 'Discount']].corr().iloc[0, 1]
            factors.append({
                'factor': 'Discount',
                'correlation': float(discount_corr),
                'impact': 'negative' if discount_corr < -0.3 else 'neutral'
            })
            
            # Quantity factor
            if 'Quantity' in self.df.columns:
                qty_corr = self.df[[metric, 'Quantity']].corr().iloc[0, 1]
                factors.append({
                    'factor': 'Quantity',
                    'correlation': float(qty_corr),
                    'impact': 'positive' if qty_corr > 0.3 else 'neutral'
                })
        except:
            pass
        
        return factors
    
    def _generate_diagnostic_recommendations(self, insights: List[str]) -> List[str]:
        """Generate recommendations based on diagnostic insights"""
        recommendations = []
        
        for insight in insights:
            if 'below average' in insight.lower():
                recommendations.append("Investigate marketing and sales strategies for underperforming periods")
            if 'discount' in insight.lower():
                recommendations.append("Review discount strategy to optimize profit margins")
            if 'variation' in insight.lower():
                recommendations.append("Standardize operations across regions to reduce variation")
        
        return recommendations
