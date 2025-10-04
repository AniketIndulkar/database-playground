import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from object_storage.storage_client import ObjectStorageClient
from vector_db.vector_client import VectorDBClient
from graph_db.graph_client import GraphDBClient
from columnar_db.columnar_client import ColumnarDBClient

class EcommerceScenario:
    """Demonstration of how all 4 databases work together in e-commerce"""
    
    def __init__(self):
        self.object_storage = ObjectStorageClient()
        self.vector_db = VectorDBClient(collection_name="products")
        self.graph_db = GraphDBClient()
        self.columnar_db = ColumnarDBClient()
        
        print("✅ E-commerce system initialized with all 4 databases")
    
    def add_product(self, product_id: str, name: str, description: str, 
                    category: str, price: float, image_path: str = None):
        """
        Add a product to the e-commerce system
        - Image → Object Storage
        - Description → Vector DB (for recommendations)
        """
        print(f"\n📦 Adding product: {name}")
        
        # 1. Store product image in Object Storage
        if image_path:
            object_name = f"products/{product_id}.jpg"
            self.object_storage.upload_file(image_path, object_name)
            print(f"  ✓ Image stored in Object Storage")
        
        # 2. Store product description in Vector DB for similarity search
        self.vector_db.add_document(
            doc_id=product_id,
            text=f"{name}. {description}",
            metadata={
                "name": name,
                "category": category,
                "price": price
            }
        )
        print(f"  ✓ Description indexed in Vector DB")
    
    def find_similar_products(self, product_description: str, top_k: int = 3):
        """
        Find similar products using Vector DB
        """
        print(f"\n🔍 Finding products similar to: '{product_description}'")
        
        results = self.vector_db.search_similar(product_description, top_k)
        
        similar_products = []
        for i, (doc, distance, metadata) in enumerate(zip(
            results['documents'][0],
            results['distances'][0],
            results['metadatas'][0]
        )):
            similar_products.append({
                "rank": i + 1,
                "name": metadata.get('name', 'Unknown'),
                "category": metadata.get('category', 'Unknown'),
                "price": metadata.get('price', 0),
                "similarity_score": round(1 - distance, 3)  # Convert distance to similarity
            })
            print(f"  {i+1}. {metadata.get('name')} (Score: {round(1-distance, 3)})")
        
        return similar_products
    
    def add_customer(self, customer_id: str, name: str, age: int):
        """
        Add a customer to the social graph
        """
        print(f"\n👤 Adding customer: {name}")
        self.graph_db.create_user(customer_id, name, age)
    
    def add_customer_relationship(self, customer1_id: str, customer2_id: str, 
                                  relationship_type: str = "FOLLOWS"):
        """
        Create a relationship between customers in Graph DB
        """
        print(f"\n🤝 Creating {relationship_type} relationship")
        self.graph_db.create_friendship(customer1_id, customer2_id)
    
    def get_customer_network(self, customer_id: str):
        """
        Get customer's network for social recommendations
        """
        print(f"\n🌐 Getting network for customer: {customer_id}")
        
        friends = self.graph_db.find_friends(customer_id)
        fofs = self.graph_db.find_friends_of_friends(customer_id)
        
        print(f"  Direct connections: {len(friends)}")
        print(f"  Extended network: {len(fofs)}")
        
        return {
            "direct": friends,
            "extended": fofs
        }
    
    def record_sale(self, order_id: int, product_name: str, category: str,
                    quantity: int, price: float, region: str):
        """
        Record a sale in Columnar DB for analytics
        """
        print(f"\n💰 Recording sale: {product_name}")
        
        from datetime import datetime
        
        self.columnar_db.conn.execute(f"""
            INSERT INTO sales VALUES
            ({order_id}, '{product_name}', '{category}', {quantity}, 
             {price}, '{datetime.now().date()}', '{region}')
        """)
        print(f"  ✓ Sale recorded in analytics database")
    
    def get_sales_analytics(self):
        """
        Get sales analytics from Columnar DB
        """
        print(f"\n📊 Generating sales analytics...")
        
        analytics = {
            "by_category": self.columnar_db.analytics_query("total_by_category"),
            "by_region": self.columnar_db.analytics_query("total_by_region"),
            "top_products": self.columnar_db.analytics_query("top_products")
        }
        
        return analytics
    
    def demo_workflow(self):
        """
        Run a complete e-commerce workflow demonstration
        """
        print("\n" + "="*60)
        print("🛒 E-COMMERCE WORKFLOW DEMONSTRATION")
        print("="*60)
        
        # Initialize columnar DB
        self.columnar_db.create_sales_table()
        
        print("\n--- STEP 1: Add Products ---")
        self.add_product(
            "prod_001", 
            "Wireless Headphones",
            "Premium noise-canceling wireless headphones with 30-hour battery",
            "Electronics",
            199.99
        )
        
        self.add_product(
            "prod_002",
            "Bluetooth Speaker",
            "Portable waterproof speaker with amazing sound quality",
            "Electronics",
            79.99
        )
        
        self.add_product(
            "prod_003",
            "Office Chair",
            "Ergonomic office chair with lumbar support",
            "Furniture",
            299.99
        )
        
        print("\n--- STEP 2: Find Similar Products ---")
        similar = self.find_similar_products("wireless audio device", top_k=2)
        
        print("\n--- STEP 3: Add Customers & Relationships ---")
        self.add_customer("cust_001", "Alice", 28)
        self.add_customer("cust_002", "Bob", 32)
        self.add_customer("cust_003", "Charlie", 25)
        
        self.add_customer_relationship("cust_001", "cust_002")
        self.add_customer_relationship("cust_002", "cust_003")
        
        network = self.get_customer_network("cust_001")
        
        print("\n--- STEP 4: Record Sales ---")
        self.record_sale(1, "Wireless Headphones", "Electronics", 2, 199.99, "North")
        self.record_sale(2, "Bluetooth Speaker", "Electronics", 1, 79.99, "South")
        self.record_sale(3, "Office Chair", "Furniture", 1, 299.99, "East")
        
        print("\n--- STEP 5: Generate Analytics ---")
        analytics = self.get_sales_analytics()
        
        print("\n📈 Revenue by Category:")
        print(analytics['by_category'])
        
        print("\n" + "="*60)
        print("✅ E-COMMERCE WORKFLOW COMPLETE")
        print("="*60)


if __name__ == "__main__":
    # Run the demonstration
    ecommerce = EcommerceScenario()
    ecommerce.demo_workflow()