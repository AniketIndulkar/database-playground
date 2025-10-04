# Columnar Database (DuckDB) Documentation

## Overview

Columnar databases store data by column rather than by row. This fundamentally different storage model makes them exceptionally fast for analytical queries that aggregate data across many rows but only need a few columns.

## Row-Based vs Columnar Storage

### Traditional Row-Based Storage (PostgreSQL, MySQL)

Data stored as complete rows:
```
Row 1: [ID=1, Name="Alice", Age=25, City="NYC", Salary=75000]
Row 2: [ID=2, Name="Bob", Age=30, City="LA", Salary=85000]
Row 3: [ID=3, Name="Charlie", Age=28, City="NYC", Salary=90000]
```

**Query: "What's the average salary?"**
- Must read ALL columns for ALL rows
- Then extract only the Salary column
- Wasteful I/O for analytics

### Columnar Storage (DuckDB, Redshift, ClickHouse)

Data stored by column:
```
ID column:     [1, 2, 3]
Name column:   ["Alice", "Bob", "Charlie"]
Age column:    [25, 30, 28]
City column:   ["NYC", "LA", "NYC"]
Salary column: [75000, 85000, 90000]
```

**Query: "What's the average salary?"**
- Read ONLY the Salary column
- Skip all other columns entirely
- Much less I/O, much faster

## Key Advantages

### 1. Analytics Performance

Columnar storage excels at aggregations:

```sql
-- This query only reads 2 columns (category, price)
-- In row storage, would read all 7 columns
SELECT category, AVG(price), COUNT(*)
FROM sales
GROUP BY category
```

**Why it's faster:**
- Only loads needed columns into memory
- Sequential memory access (cache-friendly)
- SIMD (Single Instruction Multiple Data) parallel processing

### 2. Compression

Columns compress much better than rows:

```
Row storage:
[1, "Alice", 25, "NYC", 75000]
[2, "Bob", 30, "LA", 85000]
Hard to compress - mixed data types

Columnar storage:
City: ["NYC", "NYC", "NYC", "LA", "LA", "LA", ...]
Easy to compress - repetitive values
Can use: Dictionary encoding, Run-length encoding
```

**Compression ratios:** Often 10-20x better than row storage

### 3. Efficient Filtering

When filtering data, only relevant columns are scanned:

```sql
-- Only reads 'region' column to filter
-- Then reads 'revenue' column for matching rows
SELECT SUM(revenue)
FROM sales
WHERE region = 'North'
```

## When to Use Columnar Databases

### Ideal Use Cases

**1. Data Warehousing**
- Business intelligence
- Historical data analysis
- Management reports

**2. Analytics Workloads**
- Aggregations (SUM, AVG, COUNT, MAX, MIN)
- Time-series analysis
- Statistical calculations

**3. OLAP (Online Analytical Processing)**
- Multi-dimensional analysis
- Complex queries on large datasets
- Read-heavy workloads

**4. Data Science**
- Feature engineering
- Large-scale data processing
- Model training data preparation

### When NOT to Use Columnar Databases

❌ **OLTP (Online Transaction Processing)**
```sql
-- Bad for columnar: Updates individual records
UPDATE users SET email = 'new@email.com' WHERE id = 123
```

❌ **Row-by-row operations**
```sql
-- Bad for columnar: Needs all columns for each row
SELECT * FROM users WHERE id IN (1, 2, 3)
```

❌ **Frequent updates/deletes**
- Columnar databases optimize for reads, not writes
- Updates require rewriting entire columns

❌ **Transactional systems**
- Banking transactions
- E-commerce orders
- User authentication

## DuckDB Specifics

### Why DuckDB?

1. **Embedded database** - Like SQLite, runs in-process
2. **Zero dependencies** - No external services needed
3. **SQL-compliant** - Standard SQL syntax
4. **Fast** - Columnar storage + vectorized execution
5. **Perfect for analytics** - Built specifically for OLAP

### Architecture

DuckDB uses:
- **Columnar storage format** for efficient analytics
- **Vectorized query execution** for parallel processing
- **Compression** to reduce storage and I/O
- **In-memory processing** with disk persistence

### Integration with Pandas

DuckDB seamlessly works with Pandas:

```python
import duckdb
import pandas as pd

# Execute query, get DataFrame
df = duckdb.execute("SELECT * FROM sales").fetchdf()

# Or query Pandas DataFrames directly
duckdb.query("SELECT AVG(price) FROM df")
```

## Implementation Details

### Connection Management

```python
import duckdb

# Persistent database (file-based)
conn = duckdb.connect('analytics.db')

# In-memory database (faster, but data lost on close)
conn = duckdb.connect(':memory:')

# Always close when done
conn.close()
```

### Creating Tables

```python
# Create table with schema
conn.execute("""
    CREATE TABLE sales (
        order_id INTEGER,
        product_name VARCHAR,
        category VARCHAR,
        quantity INTEGER,
        price DECIMAL(10,2),
        order_date DATE,
        region VARCHAR
    )
""")
```

### Data Types

Common DuckDB data types:
- **INTEGER, BIGINT** - Whole numbers
- **DECIMAL(p,s)** - Fixed-point numbers
- **VARCHAR** - Variable-length strings
- **DATE, TIMESTAMP** - Dates and times
- **BOOLEAN** - True/false
- **ARRAY, STRUCT** - Complex types

### Inserting Data

```python
# Single insert
conn.execute("""
    INSERT INTO sales VALUES
    (1, 'Laptop', 'Electronics', 2, 1200.00, '2024-01-15', 'North')
""")

# Bulk insert from CSV
conn.execute("COPY sales FROM 'data.csv' (HEADER)")

# From Pandas DataFrame
conn.execute("CREATE TABLE sales AS SELECT * FROM df")
```

## Performance Optimization

### 1. Use Appropriate Data Types

```python
# Bad: Everything as VARCHAR
price VARCHAR

# Good: Use specific types
price DECIMAL(10,2)
quantity INTEGER
```

### 2. Filter Before Aggregating

```python
# Bad: Aggregate everything, then filter
SELECT category, SUM(revenue)
FROM sales
GROUP BY category
HAVING SUM(revenue) > 1000

# Good: Filter first, then aggregate
SELECT category, SUM(revenue)
FROM sales
WHERE price > 50  -- Filter early
GROUP BY category
```

### 3. Select Only Needed Columns

```python
# Bad: Select everything
SELECT * FROM sales WHERE region = 'North'

# Good: Select only what you need
SELECT product_name, price FROM sales WHERE region = 'North'
```

### 4. Use Batch Operations

```python
# Bad: Row-by-row inserts
for row in data:
    conn.execute(f"INSERT INTO sales VALUES (...)")

# Good: Bulk insert
conn.executemany("INSERT INTO sales VALUES (?, ?, ...)", data)
```

## Common Analytical Queries

### Aggregations

```sql
-- Total revenue by category
SELECT 
    category,
    SUM(quantity * price) as total_revenue,
    COUNT(*) as order_count,
    AVG(price) as avg_price
FROM sales
GROUP BY category
ORDER BY total_revenue DESC
```

### Time-Series Analysis

```sql
-- Daily revenue trend
SELECT 
    DATE_TRUNC('day', order_date) as day,
    SUM(quantity * price) as daily_revenue
FROM sales
GROUP BY day
ORDER BY day
```

### Window Functions

```sql
-- Running total by region
SELECT 
    region,
    order_date,
    SUM(quantity * price) OVER (
        PARTITION BY region 
        ORDER BY order_date
    ) as running_total
FROM sales
```

### Top-N Queries

```sql
-- Top 10 products by revenue
SELECT 
    product_name,
    SUM(quantity * price) as revenue
FROM sales
GROUP BY product_name
ORDER BY revenue DESC
LIMIT 10
```

## Comparison with Other Databases

| Feature | Columnar (DuckDB) | Row-Based (PostgreSQL) | Document (MongoDB) |
|---------|-------------------|------------------------|-------------------|
| **Analytics** | Excellent | Medium | Poor |
| **OLTP** | Poor | Excellent | Good |
| **Compression** | Excellent (10-20x) | Good (2-3x) | Medium |
| **Write Speed** | Medium | Fast | Very Fast |
| **Read Speed (Analytics)** | Very Fast | Medium | Slow |
| **Storage** | Compact | Medium | Large |
| **Use Case** | Reporting, BI | Transactions | Semi-structured data |

## Real-World Performance

### Typical Speed Improvements

Aggregation queries on large datasets:
- **10-100x faster** than row-based databases
- **5-20x less storage** due to compression
- **50-90% less I/O** by reading only needed columns

### Example Benchmark

Dataset: 100 million rows, 20 columns

```sql
SELECT region, AVG(revenue)
FROM sales
GROUP BY region
```

- **PostgreSQL (row-based):** 45 seconds
- **DuckDB (columnar):** 2 seconds
- **Speedup:** 22.5x faster

## Best Practices

### 1. Design for Analytics

Structure data for typical queries:
```python
# Good: Denormalized for analytics
CREATE TABLE sales_fact (
    date DATE,
    product VARCHAR,
    region VARCHAR,
    revenue DECIMAL,
    quantity INTEGER
)

# Avoid: Normalized (better for OLTP)
CREATE TABLE orders (...) 
CREATE TABLE order_items (...)
CREATE TABLE products (...)
```

### 2. Batch Loads

Load data in large batches:
```python
# Load from CSV
conn.execute("COPY sales FROM 'data.csv'")

# Or from Parquet (very efficient)
conn.execute("COPY sales FROM 'data.parquet'")
```

### 3. Use Views for Complex Queries

```python
# Create reusable view
conn.execute("""
    CREATE VIEW monthly_revenue AS
    SELECT 
        DATE_TRUNC('month', order_date) as month,
        category,
        SUM(quantity * price) as revenue
    FROM sales
    GROUP BY month, category
""")

# Query the view
result = conn.execute("SELECT * FROM monthly_revenue").fetchdf()
```

### 4. Partition Large Tables

For very large datasets, consider partitioning:
```python
# Partition by date range
CREATE TABLE sales_2024 AS 
SELECT * FROM sales WHERE YEAR(order_date) = 2024
```

## Integration Patterns

### With Python Data Science Stack

```python
import duckdb
import pandas as pd
import matplotlib.pyplot as plt

# Load data
conn = duckdb.connect('analytics.db')

# Query into DataFrame
df = conn.execute("""
    SELECT category, SUM(revenue) as total
    FROM sales
    GROUP BY category
""").fetchdf()

# Visualize
df.plot(x='category', y='total', kind='bar')
plt.show()
```

### With FastAPI

```python
from fastapi import FastAPI
import duckdb

app = FastAPI()
conn = duckdb.connect('analytics.db')

@app.get("/analytics/revenue-by-category")
def get_revenue():
    result = conn.execute("""
        SELECT category, SUM(revenue) as total
        FROM sales
        GROUP BY category
    """).fetchdf()
    return result.to_dict('records')
```

## Troubleshooting

### Common Issues

**1. Out of Memory**
```python
# Problem: Query uses too much memory
SELECT * FROM huge_table

# Solution: Use LIMIT or streaming
SELECT * FROM huge_table LIMIT 1000
```

**2. Slow Writes**
```python
# Problem: Many small inserts
for row in data:
    conn.execute("INSERT...")

# Solution: Use batch insert
conn.executemany("INSERT INTO sales VALUES (?, ...)", data)
```

**3. Query Still Slow**
- Check if you're selecting unnecessary columns
- Verify data types are appropriate
- Consider creating indexes on filter columns
- Profile query with EXPLAIN

## Further Reading

### Documentation
- [DuckDB Official Docs](https://duckdb.org/docs/)
- [DuckDB Python API](https://duckdb.org/docs/api/python)
- [SQL Reference](https://duckdb.org/docs/sql/introduction)

### Alternative Columnar Databases
- **ClickHouse** - High-performance for real-time analytics
- **Amazon Redshift** - Cloud data warehouse
- **Google BigQuery** - Serverless data warehouse
- **Apache Parquet** - Columnar file format
- **Apache Arrow** - In-memory columnar format

## Summary

Columnar databases excel at:
- Analytical queries with aggregations
- Reading few columns from many rows
- Data warehousing and BI
- Read-heavy workloads

Key takeaways:
1. Store data by column for faster analytics
2. Compression is much more effective
3. Read only the columns you need
4. Perfect for OLAP, poor for OLTP
5. DuckDB combines columnar storage with SQL

---

**Next Steps:**
- Try running analytics queries on your own data
- Compare performance with row-based databases
- Explore window functions for time-series analysis
- Build a data warehouse with DuckDB