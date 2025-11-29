"""
Prescriptive Analytics Module
What actions should be taken?
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List
from app.core.logger import app_logger as logger


class PrescriptiveAnalytics:
    """Prescriptive analytics engine"""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df
    
    def optimize_inventory(self) -> Dict[str, Any]:
        """Generate inventory optimization recommendations"""
        try:
            # Product velocity analysis
            product_metrics = self.df.groupby(['Product ID', 'Product Name', 'Category']).agg({
                'Quantity': 'sum',
                'Sales': 'sum',
                'Order ID': 'count',
                'Order Date': ['min', 'max']
            })
            
            # Flatten columns
            product_metrics.columns = ['_'.join(col) if isinstance(col, tuple) else col for col in product_metrics.columns]
            product_metrics = product_metrics.reset_index()
            
            # Rename for clarity
            product_metrics.columns = ['Product_ID', 'Product_Name', 'Category', 'Quantity_sum', 
                                    'Sales_sum', 'Order_ID_count', 'Order_Date_min', 'Order_Date_max']
            
            # Calculate days in inventory
            product_metrics['days_in_stock'] = (
                pd.to_datetime(product_metrics['Order_Date_max']) - 
                pd.to_datetime(product_metrics['Order_Date_min'])
            ).dt.days.clip(lower=1)
            
            product_metrics['daily_velocity'] = (
                product_metrics['Quantity_sum'] / product_metrics['days_in_stock']
            ).round(2)
            
            # Categorize recommendations
            velocity_75 = product_metrics['daily_velocity'].quantile(0.75)
            velocity_25 = product_metrics['daily_velocity'].quantile(0.25)
            
            product_metrics['recommendation'] = 'Maintain'
            product_metrics.loc[product_metrics['daily_velocity'] > velocity_75, 'recommendation'] = 'Increase Stock'
            product_metrics.loc[product_metrics['daily_velocity'] < velocity_25, 'recommendation'] = 'Reduce Stock'
            
            # Convert to clean records
            records = []
            for _, row in product_metrics.iterrows():
                records.append({
                    'Product_ID': str(row['Product_ID']),
                    'Product_Name': str(row['Product_Name']),
                    'Category': str(row['Category']),
                    'daily_velocity': float(row['daily_velocity']),
                    'Sales_sum': float(row['Sales_sum']),
                    'recommendation': str(row['recommendation'])
                })
            
            recommendations = product_metrics.groupby('recommendation').agg({
                'Product_ID': 'count',
                'Sales_sum': 'sum'
            }).reset_index()
            
            rec_records = []
            for _, row in recommendations.iterrows():
                rec_records.append({
                    'recommendation': str(row['recommendation']),
                    'Product_ID': int(row['Product_ID']),
                    'Sales_sum': float(row['Sales_sum'])
                })
            
            high_priority = [r for r in records if r['recommendation'] == 'Increase Stock']
            high_priority = sorted(high_priority, key=lambda x: x['Sales_sum'], reverse=True)[:10]
            
            return {
                'inventory_recommendations': records,
                'summary': rec_records,
                'high_priority_items': high_priority
            }
            
        except Exception as e:
            logger.error(f"Error optimizing inventory: {e}")
            return {'inventory_recommendations': [], 'summary': [], 'high_priority_items': []}
    
    def optimize_pricing(self) -> Dict[str, Any]:
        """Generate pricing optimization recommendations"""
        try:
            # Analyze price sensitivity
            price_metrics = self.df.groupby('Category').agg({
                'Sales': 'sum',
                'Profit': 'sum',
                'Discount': 'mean',
                'Quantity': 'sum'
            }).reset_index()
            
            price_metrics['profit_margin'] = (
                price_metrics['Profit'] / price_metrics['Sales'] * 100
            ).round(2)
            
            price_metrics['avg_price'] = (
                price_metrics['Sales'] / price_metrics['Quantity']
            ).round(2)
            
            recommendations = []
            
            for _, row in price_metrics.iterrows():
                category = row['Category']
                margin = row['profit_margin']
                discount = row['Discount']
                
                if margin < 20 and discount > 0.15:
                    recommendations.append({
                        'category': category,
                        'action': 'Reduce Discounts',
                        'current_discount': f"{discount*100:.1f}%",
                        'target_discount': '10-12%',
                        'expected_impact': f'Improve profit margin by {(0.05 * row['Sales']):.0f}'
                    })
                elif margin > 40:
                    recommendations.append({
                        'category': category,
                        'action': 'Consider Price Reduction',
                        'current_margin': f"{margin:.1f}%",
                        'potential': 'Increase market share'
                    })
                else:
                    recommendations.append({
                        'category': category,
                        'action': 'Maintain Current Pricing',
                        'reason': 'Optimal pricing achieved'
                    })
            
            return {
                'pricing_recommendations': recommendations,
                'category_metrics': price_metrics.to_dict('records')
            }
            
        except Exception as e:
            logger.error(f"Error optimizing pricing: {e}")
            return {}
    
    def optimize_marketing_spend(self) -> Dict[str, Any]:
        """Generate marketing budget optimization recommendations"""
        try:
            # Regional ROI analysis
            regional_metrics = self.df.groupby('Region').agg({
                'Sales': 'sum',
                'Profit': 'sum',
                'Customer ID': 'nunique',
                'Order ID': 'count'
            }).reset_index()
            
            regional_metrics['profit_margin'] = (
                regional_metrics['Profit'] / regional_metrics['Sales'] * 100
            ).round(2)
            
            regional_metrics['sales_per_customer'] = (
                regional_metrics['Sales'] / regional_metrics['Customer ID']
            ).round(2)
            
            # Calculate ROI score
            regional_metrics['roi_score'] = (
                regional_metrics['profit_margin'] * regional_metrics['sales_per_customer'] / 100
            ).round(2)
            
            regional_metrics = regional_metrics.sort_values('roi_score', ascending=False)
            
            # Budget allocation recommendations
            total_score = regional_metrics['roi_score'].sum()
            regional_metrics['recommended_budget_pct'] = (
                regional_metrics['roi_score'] / total_score * 100
            ).round(1)
            
            recommendations = []
            for _, row in regional_metrics.iterrows():
                recommendations.append({
                    'region': row['Region'],
                    'current_performance': {
                        'sales': float(row['Sales']),
                        'profit_margin': float(row['profit_margin']),
                        'customers': int(row['Customer ID'])
                    },
                    'recommended_budget_allocation': f"{row['recommended_budget_pct']:.1f}%",
                    'priority': 'High' if row['roi_score'] > regional_metrics['roi_score'].median() else 'Medium'
                })
            
            return {
                'marketing_recommendations': recommendations,
                'allocation_strategy': 'ROI-Based',
                'top_region': regional_metrics.iloc[0]['Region']
            }
            
        except Exception as e:
            logger.error(f"Error optimizing marketing: {e}")
            return {}
    
    def recommend_customer_retention_strategy(self) -> Dict[str, Any]:
        """Generate customer retention recommendations"""
        try:
            # Customer segmentation
            customer_metrics = self.df.groupby('Customer ID').agg({
                'Order ID': 'count',
                'Sales': 'sum',
                'Profit': 'sum',
                'Order Date': 'max'
            }).reset_index()
            
            customer_metrics['recency_days'] = (
                pd.Timestamp.now() - pd.to_datetime(customer_metrics['Order Date'])
            ).dt.days
            
            # RFM-like segmentation
            customer_metrics['segment'] = 'At Risk'
            customer_metrics.loc[
                (customer_metrics['recency_days'] < 90) & (customer_metrics['Order ID'] >= 5),
                'segment'
            ] = 'Champions'
            customer_metrics.loc[
                (customer_metrics['recency_days'] < 90) & (customer_metrics['Order ID'] < 5),
                'segment'
            ] = 'Promising'
            customer_metrics.loc[
                (customer_metrics['recency_days'] >= 90) & (customer_metrics['recency_days'] < 180),
                'segment'
            ] = 'At Risk'
            customer_metrics.loc[
                customer_metrics['recency_days'] >= 180,
                'segment'
            ] = 'Lost'
            
            segment_summary = customer_metrics.groupby('segment').agg({
                'Customer ID': 'count',
                'Sales': 'sum',
                'Profit': 'sum'
            }).reset_index()
            
            # Recommendations by segment
            recommendations = {
                'Champions': {
                    'strategy': 'Reward and engage',
                    'actions': [
                        'Offer exclusive deals',
                        'Request referrals',
                        'Premium customer service'
                    ]
                },
                'Promising': {
                    'strategy': 'Nurture and grow',
                    'actions': [
                        'Personalized recommendations',
                        'Cross-sell opportunities',
                        'Loyalty program enrollment'
                    ]
                },
                'At Risk': {
                    'strategy': 'Re-engage immediately',
                    'actions': [
                        'Win-back campaigns',
                        'Special discounts',
                        'Satisfaction surveys'
                    ]
                },
                'Lost': {
                    'strategy': 'Reactivation campaign',
                    'actions': [
                        'Special comeback offers',
                        'Product updates',
                        'Feedback collection'
                    ]
                }
            }
            
            return {
                'segment_summary': segment_summary.to_dict('records'),
                'retention_strategies': recommendations,
                'priority_segments': ['At Risk', 'Lost']
            }
            
        except Exception as e:
            logger.error(f"Error in retention strategy: {e}")
            return {}
    
    def recommend_product_bundle(self) -> Dict[str, Any]:
        """Recommend product bundling opportunities"""
        try:
            # Product co-occurrence analysis
            orders_with_products = self.df.groupby('Order ID')['Product Name'].apply(list).reset_index()
            
            # Find frequently bought together
            product_pairs = {}
            for products in orders_with_products['Product Name']:
                if len(products) > 1:
                    for i, prod1 in enumerate(products):
                        for prod2 in products[i+1:]:
                            pair = tuple(sorted([prod1, prod2]))
                            product_pairs[pair] = product_pairs.get(pair, 0) + 1
            
            # Sort by frequency
            sorted_pairs = sorted(product_pairs.items(), key=lambda x: x[1], reverse=True)[:10]
            
            bundle_recommendations = []
            for (prod1, prod2), count in sorted_pairs:
                bundle_recommendations.append({
                    'product_1': prod1,
                    'product_2': prod2,
                    'frequency': count,
                    'bundle_name': f'{prod1[:20]}... + {prod2[:20]}...',
                    'recommendation': 'Create bundle offer'
                })
            
            return {
                'bundle_recommendations': bundle_recommendations,
                'total_bundles_identified': len(bundle_recommendations)
            }
            
        except Exception as e:
            logger.error(f"Error in bundle recommendations: {e}")
            return {}
    
    def generate_action_plan(self) -> Dict[str, Any]:
        """Generate comprehensive action plan"""
        try:
            action_plan = {
                'immediate_actions': [
                    'Review and adjust discount strategy to improve profit margins',
                    'Focus marketing efforts on high-ROI regions',
                    'Implement customer retention campaigns for at-risk segments'
                ],
                'short_term_actions': [
                    'Optimize inventory for high-velocity products',
                    'Test product bundling strategies',
                    'Analyze and address regional performance gaps'
                ],
                'long_term_actions': [
                    'Develop predictive models for demand forecasting',
                    'Implement dynamic pricing strategies',
                    'Build customer loyalty programs'
                ],
                'metrics_to_track': [
                    'Customer lifetime value',
                    'Churn rate',
                    'Profit margin by category',
                    'Inventory turnover ratio'
                ]
            }
            
            return action_plan
            
        except Exception as e:
            logger.error(f"Error generating action plan: {e}")
            return {}
