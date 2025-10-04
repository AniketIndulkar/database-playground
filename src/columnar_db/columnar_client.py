import duckdb
import pandas as pd
from typing import List, Dict


class ColumnarDBClient:
    """Client for interacting with DuckDB columnar database"""
    
    def __init__(self, db_path: str = "./data/duckdb/analytics.db"):
        self.conn = duckdb.connect(db_path)
        print(f"✅ Columnar DB initialized at '{db_path}'")
    
    def create_sales_table(self):
        """Create a sample sales table"""
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS sales (
                order_id INTEGER,
                product_name VARCHAR,
                category VARCHAR,
                quantity INTEGER,
                price DECIMAL(10,2),
                order_date DATE,
                region VARCHAR
            )
        """)
        print("✅ Created 'sales' table")
    
    def insert_sample_data(self):
        """Insert sample sales data"""
        self.conn.execute("""
            INSERT INTO sales VALUES
            (1, 'Laptop', 'Electronics', 2, 1200.00, '2024-01-15', 'North'),
            (2, 'Mouse', 'Electronics', 5, 25.00, '2024-01-16', 'South'),
            (3, 'Desk', 'Furniture', 1, 450.00, '2024-01-17', 'East'),
            (4, 'Chair', 'Furniture', 4, 150.00, '2024-01-18', 'West'),
            (5, 'Monitor', 'Electronics', 3, 300.00, '2024-01-19', 'North'),
            (6, 'Keyboard', 'Electronics', 10, 75.00, '2024-01-20', 'South'),
            (7, 'Bookshelf', 'Furniture', 2, 200.00, '2024-01-21', 'East'),
            (8, 'Laptop', 'Electronics', 1, 1200.00, '2024-01-22', 'West')
        """)
        print("✅ Inserted sample sales data")
    
    def analytics_query(self, query_type: str) -> pd.DataFrame:
        """Run different types of analytics queries"""
        
        queries = {
            "total_by_category": """
                SELECT category, 
                       SUM(quantity * price) as total_revenue,
                       COUNT(*) as order_count,
                       AVG(price) as avg_price
                FROM sales
                GROUP BY category
                ORDER BY total_revenue DESC
            """,
            
            "total_by_region": """
                SELECT region,
                       SUM(quantity * price) as total_revenue,
                       SUM(quantity) as total_quantity
                FROM sales
                GROUP BY region
                ORDER BY total_revenue DESC
            """,
            
            "top_products": """
                SELECT product_name,
                       SUM(quantity) as total_sold,
                       SUM(quantity * price) as revenue
                FROM sales
                GROUP BY product_name
                ORDER BY revenue DESC
                LIMIT 5
            """
        }
        
        if query_type not in queries:
            raise ValueError(f"Unknown query type: {query_type}")
        
        result = self.conn.execute(queries[query_type]).fetchdf()
        print(f"🔍 Executed '{query_type}' query")
        return result
    
    def get_table_stats(self) -> Dict:
        """Get statistics about the sales table"""
        row_count = self.conn.execute("SELECT COUNT(*) FROM sales").fetchone()[0]
        
        return {
            "total_rows": row_count,
            "columns": ["order_id", "product_name", "category", "quantity", "price", "order_date", "region"]
        }
    
    def close(self):
        """Close the database connection"""
        self.conn.close()


# Test it out
if __name__ == "__main__":
    # Initialize client
    columnar_db = ColumnarDBClient()
    
    # Create table and insert data
    columnar_db.create_sales_table()
    columnar_db.insert_sample_data()
    
    # Run analytics queries
    print("\n📊 Revenue by Category:")
    print(columnar_db.analytics_query("total_by_category"))
    
    print("\n📊 Revenue by Region:")
    print(columnar_db.analytics_query("total_by_region"))
    
    print("\n📊 Top Products:")
    print(columnar_db.analytics_query("top_products"))
    
    # Show stats
    print(f"\n📊 Stats: {columnar_db.get_table_stats()}")
    
    columnar_db.close()