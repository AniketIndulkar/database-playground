from fastapi import APIRouter
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.benchmarking import tracker

router = APIRouter(prefix="/benchmarks", tags=["Benchmarks"])

@router.get("/metrics")
def get_all_metrics():
    """Get all recorded metrics"""
    return tracker.metrics

@router.get("/summary")
def get_summary():
    """Get summary statistics"""
    return tracker.get_summary()

@router.get("/metrics/{db_type}")
def get_metrics_by_db(db_type: str):
    """Get metrics for a specific database"""
    return tracker.get_metrics(db_type=db_type)

@router.delete("/clear")
def clear_metrics():
    """Clear all metrics"""
    tracker.clear()
    return {"success": True, "message": "Metrics cleared"}