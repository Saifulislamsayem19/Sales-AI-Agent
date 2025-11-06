"""
Data loading and preprocessing utilities
"""
import pandas as pd
import numpy as np
from typing import Optional, Dict, Any
from pathlib import Path
from backend.app.core.logger import app_logger as logger
from backend.app.core.config import settings


class DataLoader:
    """Data loader and preprocessor"""
    
    def __init__(self, data_path: Optional[str] = None):
        self.data_path = data_path or settings.DATA_PATH
        self.df: Optional[pd.DataFrame] = None
        self.metadata: Dict[str, Any] = {}
    
    def load_data(self, filename: str = "sales_data.csv") -> pd.DataFrame:
        """Load sales data from CSV"""
        try:
            file_path = Path(self.data_path) / filename
            
            if not file_path.exists():
                logger.warning(f"Data file not found: {file_path}. Creating sample data.")
                return self.create_sample_data()
            
            logger.info(f"Loading data from {file_path}")
            self.df = pd.read_csv(file_path)
            
            # Data type conversions
            self.df['Order Date'] = pd.to_datetime(self.df['Order Date'])
            self.df['Ship Date'] = pd.to_datetime(self.df['Ship Date'])
            
            # Numeric conversions
            numeric_columns = ['Sales', 'Quantity', 'Discount', 'Profit', 'Shipping Cost']
            for col in numeric_columns:
                if col in self.df.columns:
                    self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
            
            # Create derived features
            self.df = self.create_derived_features(self.df)
            
            # Store metadata
            self.metadata = self._extract_metadata()
            
            logger.info(f"Data loaded successfully: {len(self.df)} rows, {len(self.df.columns)} columns")
            return self.df
            
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            raise
    
    def create_derived_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create derived features"""
        try:
            # Time-based features
            df['Year'] = df['Order Date'].dt.year
            df['Month'] = df['Order Date'].dt.month
            df['Quarter'] = df['Order Date'].dt.quarter
            df['Day_of_Week'] = df['Order Date'].dt.dayofweek
            df['Week'] = df['Order Date'].dt.isocalendar().week
            df['Month_Name'] = df['Order Date'].dt.strftime('%B')
            
            # Revenue metrics
            df['Revenue'] = df['Sales']
            df['Cost'] = df['Sales'] - df['Profit']
            df['Profit_Margin'] = (df['Profit'] / df['Sales'] * 100).round(2)
            df['Discount_Amount'] = df['Sales'] * df['Discount']
            
            # Order metrics
            df['Days_to_Ship'] = (df['Ship Date'] - df['Order Date']).dt.days
            df['Revenue_per_Quantity'] = (df['Sales'] / df['Quantity']).round(2)
            
            return df
            
        except Exception as e:
            logger.error(f"Error creating derived features: {e}")
            return df
    
    def _extract_metadata(self) -> Dict[str, Any]:
        """Extract metadata from dataset"""
        if self.df is None:
            return {}
        
        return {
            'total_rows': len(self.df),
            'total_columns': len(self.df.columns),
            'date_range': {
                'start': self.df['Order Date'].min().strftime('%Y-%m-%d'),
                'end': self.df['Order Date'].max().strftime('%Y-%m-%d')
            },
            'unique_values': {
                'customers': self.df['Customer ID'].nunique() if 'Customer ID' in self.df.columns else 0,
                'products': self.df['Product ID'].nunique() if 'Product ID' in self.df.columns else 0,
                'categories': self.df['Category'].nunique() if 'Category' in self.df.columns else 0,
                'regions': self.df['Region'].nunique() if 'Region' in self.df.columns else 0,
                'countries': self.df['Country'].nunique() if 'Country' in self.df.columns else 0,
            },
            'total_sales': float(self.df['Sales'].sum()) if 'Sales' in self.df.columns else 0,
            'total_profit': float(self.df['Profit'].sum()) if 'Profit' in self.df.columns else 0,
            'columns': list(self.df.columns)
        }
    
    def create_sample_data(self, n_rows: int = 5000) -> pd.DataFrame:
        """Create sample sales data for demonstration"""
        logger.info(f"Creating sample data with {n_rows} rows")
        
        np.random.seed(42)
        
        # Date range
        start_date = pd.Timestamp('2020-01-01')
        end_date = pd.Timestamp('2024-12-31')
        dates = pd.date_range(start_date, end_date, periods=n_rows)
        
        # Categories and subcategories
        categories = {
            'Technology': ['Phones', 'Computers', 'Accessories'],
            'Furniture': ['Chairs', 'Tables', 'Bookcases'],
            'Office Supplies': ['Paper', 'Binders', 'Art']
        }
        
        # Regions and markets
        regions = ['East', 'West', 'North', 'South', 'Central']
        markets = ['US', 'EU', 'APAC', 'LATAM']
        segments = ['Consumer', 'Corporate', 'Home Office']
        ship_modes = ['Standard Class', 'Second Class', 'First Class', 'Same Day']
        priorities = ['Low', 'Medium', 'High', 'Critical']
        
        # Generate data
        data = []
        for i in range(n_rows):
            category = np.random.choice(list(categories.keys()))
            subcategory = np.random.choice(categories[category])
            
            # Base price varies by category
            base_price = {
                'Technology': np.random.uniform(50, 2000),
                'Furniture': np.random.uniform(100, 1500),
                'Office Supplies': np.random.uniform(5, 200)
            }[category]
            
            quantity = np.random.randint(1, 10)
            discount = np.random.choice([0, 0.05, 0.1, 0.15, 0.2, 0.25])
            sales = base_price * quantity * (1 - discount)
            
            # Profit margin varies by category
            profit_margin = {
                'Technology': np.random.uniform(0.15, 0.35),
                'Furniture': np.random.uniform(0.10, 0.30),
                'Office Supplies': np.random.uniform(0.20, 0.45)
            }[category]
            
            profit = sales * profit_margin
            shipping_cost = np.random.uniform(5, 50)
            
            order_date = dates[i]
            ship_date = order_date + pd.Timedelta(days=np.random.randint(1, 7))
            
            data.append({
                'Row ID': i + 1,
                'Order ID': f'ORD-{i+1000:06d}',
                'Order Date': order_date,
                'Ship Date': ship_date,
                'Ship Mode': np.random.choice(ship_modes),
                'Customer ID': f'CUST-{np.random.randint(1, 1000):05d}',
                'Customer Name': f'Customer {np.random.randint(1, 1000)}',
                'Segment': np.random.choice(segments),
                'City': f'City {np.random.randint(1, 100)}',
                'State': f'State {np.random.randint(1, 50)}',
                'Country': f'Country {np.random.randint(1, 20)}',
                'Postal Code': f'{np.random.randint(10000, 99999)}',
                'Market': np.random.choice(markets),
                'Region': np.random.choice(regions),
                'Product ID': f'PROD-{category[:3].upper()}-{np.random.randint(100, 999)}',
                'Category': category,
                'Sub-Category': subcategory,
                'Product Name': f'{subcategory} {np.random.randint(1, 100)}',
                'Sales': round(sales, 2),
                'Quantity': quantity,
                'Discount': discount,
                'Profit': round(profit, 2),
                'Shipping Cost': round(shipping_cost, 2),
                'Order Priority': np.random.choice(priorities)
            })
        
        df = pd.DataFrame(data)
        
        # Save sample data
        output_path = Path(self.data_path) / 'sales_data.csv'
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False)
        logger.info(f"Sample data saved to {output_path}")
        
        return df
    
    def get_data(self) -> Optional[pd.DataFrame]:
        """Get loaded data"""
        return self.df
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get data metadata"""
        return self.metadata
    
    def filter_data(self, filters: Dict[str, Any]) -> pd.DataFrame:
        """Filter data based on criteria"""
        if self.df is None:
            return pd.DataFrame()
        
        filtered_df = self.df.copy()
        
        for key, value in filters.items():
            if key in filtered_df.columns:
                if isinstance(value, list):
                    filtered_df = filtered_df[filtered_df[key].isin(value)]
                else:
                    filtered_df = filtered_df[filtered_df[key] == value]
        
        return filtered_df


# Global data loader instance
data_loader = DataLoader()
