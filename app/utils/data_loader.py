"""
Data loading and preprocessing utilities
"""
import pandas as pd
import numpy as np
from typing import Optional, Dict, Any
from pathlib import Path
from app.core.logger import app_logger as logger
from app.core.config import settings


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
