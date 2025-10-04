import time
import json
from functools import wraps
from typing import Dict, List
from datetime import datetime

class BenchmarkTracker:
    """Track performance metrics for database operations"""
    
    def __init__(self):
        self.metrics = []
    
    def record(self, db_type: str, operation: str, duration: float, metadata: Dict = None):
        """Record a benchmark metric"""
        metric = {
            "timestamp": datetime.now().isoformat(),
            "db_type": db_type,
            "operation": operation,
            "duration_ms": round(duration * 1000, 2),
            "metadata": metadata or {}
        }
        self.metrics.append(metric)
    
    def get_metrics(self, db_type: str = None, operation: str = None) -> List[Dict]:
        """Get filtered metrics"""
        filtered = self.metrics
        
        if db_type:
            filtered = [m for m in filtered if m['db_type'] == db_type]
        
        if operation:
            filtered = [m for m in filtered if m['operation'] == operation]
        
        return filtered
    
    def get_average(self, db_type: str, operation: str) -> float:
        """Get average duration for an operation"""
        metrics = self.get_metrics(db_type, operation)
        if not metrics:
            return 0
        return sum(m['duration_ms'] for m in metrics) / len(metrics)
    
    def clear(self):
        """Clear all metrics"""
        self.metrics = []
    
    def save_to_file(self, filepath: str):
        """Save metrics to JSON file"""
        with open(filepath, 'w') as f:
            json.dump(self.metrics, f, indent=2)
    
    def get_summary(self) -> Dict:
        """Get summary statistics"""
        summary = {}
        
        for metric in self.metrics:
            db_type = metric['db_type']
            operation = metric['operation']
            key = f"{db_type}_{operation}"
            
            if key not in summary:
                summary[key] = {
                    "db_type": db_type,
                    "operation": operation,
                    "count": 0,
                    "total_ms": 0,
                    "min_ms": float('inf'),
                    "max_ms": 0
                }
            
            summary[key]["count"] += 1
            summary[key]["total_ms"] += metric['duration_ms']
            summary[key]["min_ms"] = min(summary[key]["min_ms"], metric['duration_ms'])
            summary[key]["max_ms"] = max(summary[key]["max_ms"], metric['duration_ms'])
        
        # Calculate averages
        for key in summary:
            summary[key]["avg_ms"] = round(
                summary[key]["total_ms"] / summary[key]["count"], 2
            )
        
        return list(summary.values())

# Global tracker instance
tracker = BenchmarkTracker()

def benchmark(db_type: str, operation: str):
    """Decorator to benchmark database operations"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            
            tracker.record(db_type, operation, duration)
            return result
        return wrapper
    return decorator