import chromadb
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Optional


class VectorDBClient:
    """Client for interacting with ChromaDB vector database"""
    
    def __init__(self, collection_name: str = "documents"):
        # Initialize ChromaDB (persists to disk)
        self.client = chromadb.PersistentClient(path="./data/chromadb")
        
        # Load the embedding model (converts text to vectors)
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "Document embeddings"}
        )
        print(f"✅ Vector DB initialized with collection '{collection_name}'")
    
    def add_document(self, doc_id: str, text: str, metadata: Optional[Dict] = None):
        """Add a document to the vector database"""
        # Convert text to vector using the embedding model
        embedding = self.model.encode(text).tolist()
        
        # Store in ChromaDB
        self.collection.add(
            ids=[doc_id],
            embeddings=[embedding],
            documents=[text],
            metadatas=[metadata or {}]
        )
        print(f"✅ Added document '{doc_id}' to vector DB")
        return doc_id
    
    def search_similar(self, query: str, top_k: int = 5):
        """Search for similar documents"""
        # Convert query to vector
        query_embedding = self.model.encode(query).tolist()
        
        # Search for similar vectors
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        
        print(f"🔍 Found {len(results['documents'][0])} similar documents")
        return results
    
    def get_collection_stats(self):
        """Get statistics about the collection"""
        count = self.collection.count()
        return {"total_documents": count}


# Test it out
if __name__ == "__main__":
    # Initialize client
    vector_db = VectorDBClient()
    
    # Add some sample documents
    vector_db.add_document(
        doc_id="product_1",
        text="Red leather running shoes with cushioned sole",
        metadata={"category": "footwear", "price": 89.99}
    )
    
    vector_db.add_document(
        doc_id="product_2",
        text="Blue athletic sneakers for marathon training",
        metadata={"category": "footwear", "price": 129.99}
    )
    
    vector_db.add_document(
        doc_id="product_3",
        text="Black leather office chair with lumbar support",
        metadata={"category": "furniture", "price": 299.99}
    )
    
    # Search for similar products
    print("\n🔍 Searching for: 'comfortable running footwear'")
    results = vector_db.search_similar("comfortable running footwear", top_k=3)
    
    # Display results
    for i, doc in enumerate(results['documents'][0]):
        distance = results['distances'][0][i]
        print(f"\n{i+1}. {doc}")
        print(f"   Distance: {distance:.4f}")
    
    # Show stats
    print(f"\n📊 Stats: {vector_db.get_collection_stats()}")