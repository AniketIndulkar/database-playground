from fastapi import APIRouter, HTTPException
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scenarios.ecommerce import EcommerceScenario

router = APIRouter(prefix="/scenarios", tags=["Scenarios"])

# Global instance
ecommerce = None

@router.post("/ecommerce/initialize")
def initialize_ecommerce():
    """Initialize the e-commerce scenario"""
    global ecommerce
    try:
        ecommerce = EcommerceScenario()
        ecommerce.columnar_db.create_sales_table()
        return {"success": True, "message": "E-commerce system initialized"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ecommerce/run-demo")
def run_demo():
    """Run the complete e-commerce demonstration"""
    global ecommerce
    if not ecommerce:
        ecommerce = EcommerceScenario()
    
    try:
        ecommerce.demo_workflow()
        return {"success": True, "message": "Demo completed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ecommerce/find-similar")
def find_similar_products(query: str, top_k: int = 3):
    """Find similar products"""
    global ecommerce
    if not ecommerce:
        raise HTTPException(status_code=400, detail="E-commerce not initialized")
    
    try:
        results = ecommerce.find_similar_products(query, top_k)
        return {"products": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ecommerce/analytics")
def get_analytics():
    """Get sales analytics"""
    global ecommerce
    if not ecommerce:
        raise HTTPException(status_code=400, detail="E-commerce not initialized")
    
    try:
        analytics = ecommerce.get_sales_analytics()
        return {
            "by_category": analytics['by_category'].to_dict('records'),
            "by_region": analytics['by_region'].to_dict('records'),
            "top_products": analytics['top_products'].to_dict('records')
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))