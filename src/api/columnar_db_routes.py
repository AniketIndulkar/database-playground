from fastapi import APIRouter, HTTPException
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from columnar_db.columnar_client import ColumnarDBClient

router = APIRouter(prefix="/columnar-db", tags=["Columnar Database"])
columnar_db = ColumnarDBClient()

@router.post("/init-sample-data")
def initialize_sample_data():
    """Create table and insert sample sales data"""
    try:
        columnar_db.create_sales_table()
        columnar_db.insert_sample_data()
        return {"success": True, "message": "Sample data initialized"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/{query_type}")
def run_analytics(query_type: str):
    """Run analytics query"""
    try:
        result = columnar_db.analytics_query(query_type)
        return result.to_dict('records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
def get_stats():
    """Get table statistics"""
    return columnar_db.get_table_stats()