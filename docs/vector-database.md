# Vector Database (ChromaDB) Documentation

## Overview

Vector databases store data as high-dimensional numerical arrays (vectors) that represent the semantic meaning of content. Unlike traditional databases that search for exact matches, vector databases enable **similarity search** - finding items that are conceptually similar even if they don't share exact words.

## What is a Vector?

A vector is an array of numbers that represents the semantic meaning of text, images, or other data:

```
"Red running shoes" → [0.8, 0.9, 0.2, 0.1, 0.7, ...] (384 dimensions)
```

Each number in the vector captures different aspects of meaning. Similar content produces vectors that are "close" together in high-dimensional space.

## Key Concepts

### 1. Embeddings

**Embeddings** are the process of converting text/images into vectors. We use the `sentence-transformers` library which uses AI models to create these vectors.

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')
vector = model.encode("Red running shoes")
# Returns: array of 384 numbers
```

**Important:** The same model must be used for both:
- Creating vectors when adding documents
- Creating query vectors when searching

### 2. Semantic Search

Traditional search:
```
Query: "running shoes"
Matches: Documents containing exact words "running" and "shoes"
```

Semantic search:
```
Query: "athletic footwear"
Matches: Documents about "running shoes", "sneakers", "trainers" 
         (similar meaning, different words)
```

### 3. Distance Metrics

Vector similarity is measured by **distance**:
- **Lower distance = More similar**
- **Higher distance = Less similar**

Common distance metrics:
- **Euclidean Distance**: Straight-line distance between vectors
- **Cosine Distance**: Measures angle between vectors (what ChromaDB uses by default)

Example from our test:
```
Query: "comfortable running footwear"
Results:
  1. "Red leather running shoes" - Distance: 0.6554 ✓ Most similar
  2. "Blue athletic sneakers"     - Distance: 0.8360 ✓ Similar
  3. "Black office chair"         - Distance: 1.4581 ✗ Not similar
```

## Implementation Details

### Architecture

```
User Input
    ↓
Sentence Transformer (AI Model)
    ↓
Vector [0.8, 0.2, ...]
    ↓
ChromaDB Collection
    ↓
Search Results (with distances)
```

### Storage Structure

ChromaDB stores three things together:

1. **Vector**: The numerical embedding
2. **Document**: Original text (optional, for display)
3. **Metadata**: Additional key-value data for filtering

```python
{
  "vector": [0.8, 0.9, 0.2, ...],
  "document": "Red leather running shoes with cushioned sole",
  "metadata": {
    "product_id": "123",
    "category": "footwear",
    "price": 89.99
  }
}
```

### Multiple Vectors Per Object

For complex objects, you can store separate vectors:

```python
# Product with multiple searchable aspects
vector_db.add_document(
    doc_id="product_1_description",
    text="Red leather running shoes",
    metadata={"product_id": "123", "type": "description"}
)

vector_db.add_document(
    doc_id="product_1_reviews",
    text="Comfortable, great for marathons",
    metadata={"product_id": "123", "type": "reviews"}
)
```

Then search and filter:
```python
# Find products with similar descriptions
results = vector_db.search_similar(
    query="athletic footwear",
    filter={"type": "description"}
)
```

## When to Use Vector Databases

### Ideal Use Cases

**1. Semantic Search**
- Document search: "Find papers about machine learning"
- Product discovery: "Show me comfortable shoes"
- FAQ matching: User question → most relevant answer

**2. Recommendation Systems**
- "Users who liked this also liked..."
- "Find similar products"
- Content-based recommendations

**3. AI/ML Applications**
- RAG (Retrieval Augmented Generation): Give LLMs relevant context
- Chatbots: Find relevant knowledge base articles
- Image similarity: Find visually similar images

**4. Duplicate Detection**
- Near-duplicate content detection
- Plagiarism checking
- Similar support ticket detection

### When NOT to Use Vector Databases

❌ **Exact match queries**: Use traditional databases
   - "Find user with email='john@example.com'"
   - "Get all orders from 2024"

❌ **Structured data queries**: Use SQL/NoSQL
   - "Sum of sales by region"
   - "Join customers with orders"

❌ **Simple keyword search**: Use full-text search
   - "Find documents containing 'invoice'"

❌ **High write throughput**: Vectors are expensive to compute
   - Real-time analytics
   - High-frequency updates

## Performance Characteristics

### Strengths
- **Fast similarity search**: O(log n) with proper indexing
- **Scales well**: Can handle millions of vectors
- **Flexible**: Works with text, images, audio

### Limitations
- **Expensive writes**: Computing embeddings takes time
- **Storage overhead**: Vectors are large (384-1536 dimensions)
- **Model dependency**: Must use same model for indexing and querying
- **No exact match guarantees**: Semantic similarity is approximate

## ChromaDB Specifics

### Why ChromaDB?

1. **Easy to use**: Simple Python API
2. **Runs locally**: No external services needed
3. **Persistent storage**: Data saved to disk
4. **Lightweight**: Perfect for learning and prototyping
5. **Free and open source**

### Persistence

ChromaDB stores data in a local directory:
```python
client = chromadb.PersistentClient(path="./data/chromadb")
```

This creates:
```
data/chromadb/
  ├── chroma.sqlite3       # Metadata and indices
  └── [binary data files]  # Vector embeddings
```

### Collections

Collections are like tables in SQL - they group related vectors:

```python
# Create/get collection
collection = client.get_or_create_collection(
    name="documents",
    metadata={"description": "Product descriptions"}
)

# Multiple collections for different data types
products_col = client.get_or_create_collection("products")
reviews_col = client.get_or_create_collection("reviews")
images_col = client.get_or_create_collection("images")
```

## Code Examples

### Basic Operations

```python
from vector_db.vector_client import VectorDBClient

# Initialize
vector_db = VectorDBClient(collection_name="my_docs")

# Add documents
vector_db.add_document(
    doc_id="doc_1",
    text="Machine learning is a subset of AI",
    metadata={"category": "AI", "year": 2024}
)

# Search
results = vector_db.search_similar(
    query="artificial intelligence",
    top_k=5
)

# Access results
for i, doc in enumerate(results['documents'][0]):
    print(f"{i+1}. {doc}")
    print(f"   Distance: {results['distances'][0][i]}")
    print(f"   Metadata: {results['metadatas'][0][i]}")
```

### Batch Operations

```python
# Add multiple documents at once
docs = [
    ("doc_1", "Text 1", {"category": "tech"}),
    ("doc_2", "Text 2", {"category": "health"}),
    ("doc_3", "Text 3", {"category": "tech"}),
]

for doc_id, text, metadata in docs:
    vector_db.add_document(doc_id, text, metadata)
```

### Filtering with Metadata

```python
# Add documents with metadata
vector_db.add_document(
    "prod_1", 
    "Red shoes",
    metadata={"price": 50, "in_stock": True}
)

vector_db.add_document(
    "prod_2",
    "Blue shoes", 
    metadata={"price": 150, "in_stock": False}
)

# Search with filter (ChromaDB supports where clauses)
results = collection.query(
    query_embeddings=[query_vector],
    where={"in_stock": True, "price": {"$lt": 100}}
)
```

## Comparison with Other Databases

| Feature | Vector DB | Relational DB | Document DB |
|---------|-----------|---------------|-------------|
| **Search Type** | Semantic similarity | Exact match | Full-text search |
| **Query** | "Find similar" | "Find where X=Y" | "Find containing word" |
| **Speed** | Fast (indexed) | Very fast (indexed) | Medium |
| **Storage** | Large (vectors) | Small | Medium |
| **Use Case** | AI/ML, recommendations | Transactions, analytics | Semi-structured data |

## Model Selection

### Popular Embedding Models

**all-MiniLM-L6-v2** (Used in our implementation)
- Dimensions: 384
- Speed: Fast
- Quality: Good for general use
- Size: ~80MB

**all-mpnet-base-v2**
- Dimensions: 768
- Speed: Slower
- Quality: Better quality
- Size: ~420MB

**text-embedding-ada-002** (OpenAI)
- Dimensions: 1536
- Speed: API call required
- Quality: Excellent
- Cost: Paid API

### Choosing a Model

Consider:
1. **Speed vs Quality**: Smaller models are faster but less accurate
2. **Use case**: General text? Code? Scientific papers?
3. **Resources**: Model size and computational requirements
4. **Cost**: Free local models vs paid APIs

## Best Practices

### 1. Consistent Preprocessing
Always preprocess text the same way for indexing and querying:
```python
def preprocess(text):
    text = text.lower()
    text = text.strip()
    # Remove special characters if needed
    return text
```

### 2. Meaningful Metadata
Store metadata that helps filtering and debugging:
```python
metadata = {
    "source": "product_catalog",
    "created_at": "2024-01-15",
    "category": "electronics",
    "id": "PROD-123"
}
```

### 3. Chunk Long Documents
Break long documents into smaller chunks for better retrieval:
```python
# Instead of one long document
long_doc = "50 pages of text..."

# Split into sections
chunks = [
    "Introduction section...",
    "Methods section...",
    "Results section..."
]

for i, chunk in enumerate(chunks):
    vector_db.add_document(f"doc_1_chunk_{i}", chunk)
```

### 4. Monitor Distance Thresholds
Set distance thresholds to filter poor matches:
```python
results = vector_db.search_similar(query, top_k=10)

# Only keep results with distance < 1.0
good_results = [
    r for r in results['documents'][0] 
    if results['distances'][0][i] < 1.0
]
```

## Troubleshooting

### Common Issues

**Problem: Search returns irrelevant results**
- Solution: Try a different embedding model
- Solution: Add more context to your query
- Solution: Use metadata filters to narrow results

**Problem: Slow performance**
- Solution: Reduce dimensions (use smaller model)
- Solution: Limit `top_k` parameter
- Solution: Use batch operations

**Problem: High memory usage**
- Solution: Use smaller embedding model
- Solution: Split data into multiple collections
- Solution: Consider cloud-based vector DB for large datasets

## Advanced Topics

### 1. Hybrid Search
Combine vector search with keyword search:
```python
# 1. Vector search for semantic similarity
vector_results = vector_db.search_similar(query)

# 2. Keyword search for exact matches
keyword_results = traditional_search(query)

# 3. Combine and rank results
final_results = merge_and_rank(vector_results, keyword_results)
```

### 2. Re-ranking
Use a more powerful model to re-rank top results:
```python
# 1. Fast search with small model (get top 100)
candidates = vector_db.search_similar(query, top_k=100)

# 2. Re-rank with powerful model (get top 10)
final_results = rerank_model.rank(query, candidates[:100])[:10]
```

### 3. Fine-tuning
Fine-tune embedding models for your specific domain:
- Collect domain-specific data
- Fine-tune sentence-transformers model
- Use custom model in your vector DB

## Resources

### Documentation
- [ChromaDB Docs](https://docs.trychroma.com/)
- [Sentence Transformers](https://www.sbert.net/)
- [Vector Database Guide](https://www.pinecone.io/learn/vector-database/)

### Alternative Vector Databases
- **Pinecone**: Managed cloud service
- **Weaviate**: Open source with GraphQL
- **Milvus**: High performance, scalable
- **Qdrant**: Rust-based, fast
- **FAISS**: Facebook's library (not a full DB)

## Summary

Vector databases excel at:
- Semantic similarity search
- AI/ML applications
- Recommendation systems
- Finding conceptually related content

Key takeaways:
1. Vectors represent semantic meaning
2. Lower distance = more similar
3. Use same model for indexing and querying
4. Complement traditional databases, don't replace them
5. Best for similarity search, not exact matches

---

**Next Steps:**
- Experiment with different embedding models
- Try filtering with metadata
- Compare results with traditional keyword search
- Build a simple recommendation system