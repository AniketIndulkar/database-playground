# 🗄️ Database Playground

An interactive learning platform to understand different database types through hands-on examples. Compare **Object Storage**, **Vector Databases**, **Graph Databases**, and **Columnar Databases** to learn when to use each one.

![Python](https://img.shields.io/badge/python-3.13-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.29-red.svg)

## 📚 What You'll Learn

- **When to choose which database** for different use cases
- **Performance characteristics** and trade-offs of each database type
- **Query complexity** differences between database paradigms
- **Practical implementations** with working code examples

## 🎯 Database Types Covered

| Database Type | Technology | Best For |
|--------------|------------|----------|
| **Object Storage** | MinIO (S3-compatible) | Files, images, videos, backups |
| **Vector Database** | ChromaDB | AI/ML, semantic search, recommendations |
| **Graph Database** | Neo4j | Social networks, relationships, fraud detection |
| **Columnar Database** | DuckDB | Analytics, data warehousing, BI reports |

## 🏗️ Architecture

```
database-playground/
├── src/
│   ├── object_storage/      # MinIO client
│   ├── vector_db/            # ChromaDB client
│   ├── graph_db/             # Neo4j client
│   ├── columnar_db/          # DuckDB client
│   ├── api/                  # FastAPI backend
│   │   ├── main.py
│   │   ├── object_storage_routes.py
│   │   ├── vector_db_routes.py
│   │   ├── graph_db_routes.py
│   │   └── columnar_db_routes.py
│   └── ui/                   # Streamlit frontend
│       └── app.py
├── data/                     # Data storage
│   ├── uploads/
│   ├── processed/
│   ├── chromadb/
│   └── duckdb/
├── docs/                     # Documentation
│   ├── object-storage.md
│   ├── vector-database.md
│   ├── graph-database.md
│   ├── columnar-database.md
│   └── advanced-object-storage.md
└── tests/
```

## 🚀 Quick Start

### Prerequisites

- Python 3.13+
- Docker (for MinIO and Neo4j)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/database-playground.git
   cd database-playground
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start Docker containers**
   ```bash
   # MinIO (Object Storage)
   docker run -d \
     -p 9000:9000 \
     -p 9001:9001 \
     --name minio-storage \
     -e "MINIO_ROOT_USER=minioadmin" \
     -e "MINIO_ROOT_PASSWORD=minioadmin" \
     minio/minio server /data --console-address ":9001"
   
   # Neo4j (Graph Database)
   docker run -d \
     --name neo4j-db \
     -p 7474:7474 -p 7687:7687 \
     -e NEO4J_AUTH=neo4j/password123 \
     neo4j:latest
   ```

5. **Create necessary directories**
   ```bash
   mkdir -p data/uploads data/processed data/chromadb data/duckdb
   ```

6. **Configure environment variables**
   
   Create a `.env` file in the project root:
   ```env
   # MinIO Object Storage
   MINIO_ENDPOINT=localhost:9000
   MINIO_ACCESS_KEY=minioadmin
   MINIO_SECRET_KEY=minioadmin
   MINIO_BUCKET_NAME=content-storage
   MINIO_SECURE=False
   
   # Neo4j Graph Database
   NEO4J_URI=bolt://localhost:7687
   NEO4J_USER=neo4j
   NEO4J_PASSWORD=password123
   ```

### Running the Application

You need **two terminals**:

**Terminal 1 - Start FastAPI backend:**
```bash
python -m uvicorn src.api.main:app --reload
```

**Terminal 2 - Start Streamlit UI:**
```bash
streamlit run src/ui/app.py
```

Then visit:
- **Streamlit UI**: http://localhost:8501
- **FastAPI Docs**: http://127.0.0.1:8000/docs
- **MinIO Console**: http://localhost:9001
- **Neo4j Browser**: http://localhost:7474

## 📖 Documentation

Comprehensive guides for each database type:

- **[Object Storage](docs/object-storage.md)** - Understanding blob storage, S3-compatible APIs, and when to use object storage
- **[Vector Database](docs/vector-database.md)** - Semantic search, embeddings, similarity search, and AI/ML applications
- **[Graph Database](docs/graph-database.md)** - Nodes, edges, traversals, Cypher queries, and relationship modeling
- **[Columnar Database](docs/columnar-database.md)** - Column-oriented storage, analytics optimization, and OLAP queries
- **[Advanced Object Storage](docs/advanced-object-storage.md)** - Versioning, immutability, and advanced patterns

## 🎮 Usage Examples

### Object Storage
```python
from src.object_storage.storage_client import ObjectStorageClient

storage = ObjectStorageClient()
storage.upload_file("local_file.pdf", "stored_file.pdf")
storage.list_files()
storage.download_file("stored_file.pdf", "downloaded.pdf")
```

### Vector Database
```python
from src.vector_db.vector_client import VectorDBClient

vector_db = VectorDBClient()
vector_db.add_document("doc1", "Machine learning is awesome", {"category": "AI"})
results = vector_db.search_similar("artificial intelligence", top_k=5)
```

### Graph Database
```python
from src.graph_db.graph_client import GraphDBClient

graph = GraphDBClient()
graph.create_user("u1", "Alice", 25)
graph.create_user("u2", "Bob", 30)
graph.create_friendship("u1", "u2")
friends = graph.find_friends("u1")
```

### Columnar Database
```python
from src.columnar_db.columnar_client import ColumnarDBClient

columnar_db = ColumnarDBClient()
columnar_db.create_sales_table()
columnar_db.insert_sample_data()
results = columnar_db.analytics_query("total_by_category")
```

## 🔧 API Endpoints

### Object Storage
- `POST /object-storage/upload` - Upload file
- `GET /object-storage/files` - List all files
- `GET /object-storage/download/{filename}` - Download file

### Vector Database
- `POST /vector-db/add-document` - Add document
- `POST /vector-db/search` - Search similar documents
- `GET /vector-db/stats` - Collection statistics

### Graph Database
- `POST /graph-db/create-user` - Create user node
- `POST /graph-db/create-friendship` - Create friendship edge
- `GET /graph-db/friends/{user_id}` - Get direct friends
- `GET /graph-db/friends-of-friends/{user_id}` - Get friends of friends
- `DELETE /graph-db/clear` - Clear all data

### Columnar Database
- `POST /columnar-db/init-sample-data` - Initialize sample data
- `GET /columnar-db/analytics/{query_type}` - Run analytics query
- `GET /columnar-db/stats` - Table statistics

## 🎯 Use Case Decision Guide

### Choose Object Storage when:
- ✅ Storing files, images, videos, or documents
- ✅ Need cheap, scalable storage
- ✅ Simple get/put operations
- ❌ Don't need complex queries
- ❌ Don't need transactional guarantees

### Choose Vector Database when:
- ✅ Building semantic search
- ✅ Recommendation systems
- ✅ AI/ML applications with embeddings
- ❌ Don't need exact match queries
- ❌ Don't have relationship data

### Choose Graph Database when:
- ✅ Data has complex relationships
- ✅ Need to traverse connections
- ✅ Social networks, fraud detection
- ❌ Don't need heavy aggregations
- ❌ Simple key-value lookups suffice

### Choose Columnar Database when:
- ✅ Running analytics and aggregations
- ✅ Data warehousing, BI reports
- ✅ Reading few columns from many rows
- ❌ Don't need row-by-row updates
- ❌ OLTP workload (transactions)

## 🧪 Testing

Run individual database clients:
```bash
# Object Storage
python src/object_storage/storage_client.py

# Vector Database
python src/vector_db/vector_client.py

# Graph Database
python src/graph_db/graph_client.py

# Columnar Database
python src/columnar_db/columnar_client.py
```

## 📊 Performance Characteristics

| Database | Read Speed | Write Speed | Storage Efficiency | Query Complexity |
|----------|------------|-------------|-------------------|------------------|
| Object Storage | Good | Good | Excellent | Low |
| Vector DB | Excellent | Medium | Medium | Medium |
| Graph DB | Excellent | Medium | Medium | High |
| Columnar DB | Excellent | Low | Excellent | Medium |

## 🤝 Contributing

Contributions are welcome! Here are some ways you can help:

1. **Add more database types** - Time-series, key-value, document stores
2. **Improve documentation** - More examples, better explanations
3. **Add benchmarks** - Performance comparisons
4. **Enhance UI** - Better visualizations, more interactive demos
5. **Write tests** - Unit tests, integration tests

Please open an issue first to discuss major changes.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **MinIO** - High-performance object storage
- **ChromaDB** - Embeddings database for AI applications
- **Neo4j** - World's leading graph database
- **DuckDB** - In-process analytical database
- **FastAPI** - Modern Python web framework
- **Streamlit** - Rapid UI development

## 🔗 Resources

### Database Documentation
- [MinIO Documentation](https://min.io/docs/minio/linux/index.html)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [Neo4j Documentation](https://neo4j.com/docs/)
- [DuckDB Documentation](https://duckdb.org/docs/)

### Learning Resources
- [Database Design Course](https://www.coursera.org/learn/database-design)
- [System Design Primer](https://github.com/donnemartin/system-design-primer)
- [Designing Data-Intensive Applications](https://dataintensive.net/)

## 📧 Contact

For questions or feedback, please open an issue on GitHub.

---

**Built with ❤️ for learning database systems**