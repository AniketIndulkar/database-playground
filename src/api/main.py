from fastapi import FastAPI
from .object_storage_routes import router as object_storage_router
from .vector_db_routes import router as vector_db_router
from .graph_db_routes import router as graph_db_router
from .columnar_db_routes import router as columnar_db_router
from .benchmark_routes import router as benchmark_router
from .scenario_routes import router as scenario_router

app = FastAPI(title="Database Playground API")

# Include all routers
app.include_router(object_storage_router)
app.include_router(vector_db_router)
app.include_router(graph_db_router)
app.include_router(columnar_db_router)
app.include_router(benchmark_router)
app.include_router(scenario_router)

@app.get("/")
def root():
    return {
        "message": "Welcome to Database Playground API",
        "databases": ["object-storage", "vector-db", "graph-db", "columnar-db"],
        "docs": "/docs"
    }