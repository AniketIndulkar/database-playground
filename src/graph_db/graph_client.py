from neo4j import GraphDatabase
import os
from dotenv import load_dotenv
from utils.benchmarking import benchmark

load_dotenv()


class GraphDBClient:
    """Client for interacting with Neo4j graph database"""
    
    def __init__(self):
        self.uri = os.getenv("NEO4J_URI")
        self.user = os.getenv("NEO4J_USER")
        self.password = os.getenv("NEO4J_PASSWORD")
        
        self.driver = GraphDatabase.driver(
            self.uri,
            auth=(self.user, self.password)
        )
        print("✅ Graph DB client initialized")
    
    def close(self):
        """Close the database connection"""
        self.driver.close()
    
    @benchmark("graph_db", "create_user")
    def create_user(self, user_id: str, name: str, age: int):
        """Create a user node"""
        with self.driver.session() as session:
            result = session.run(
                "CREATE (u:User {id: $user_id, name: $name, age: $age}) RETURN u",
                user_id=user_id, name=name, age=age
            )
            print(f"✅ Created user: {name}")
            return result.single()[0]
    
    @benchmark("graph_db", "create_friendship")
    def create_friendship(self, user1_id: str, user2_id: str):
        """Create a friendship relationship between two users"""
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (u1:User {id: $user1_id})
                MATCH (u2:User {id: $user2_id})
                CREATE (u1)-[r:FRIENDS_WITH]->(u2)
                RETURN r
                """,
                user1_id=user1_id, user2_id=user2_id
            )
            print(f"✅ Created friendship: {user1_id} -> {user2_id}")
            return result.single()[0]
    
    @benchmark("graph_db", "find_friends")
    def find_friends(self, user_id: str):
        """Find all direct friends of a user"""
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (u:User {id: $user_id})-[:FRIENDS_WITH]->(friend:User)
                RETURN friend.name AS name, friend.id AS id
                """,
                user_id=user_id
            )
            friends = [{"name": record["name"], "id": record["id"]} 
                      for record in result]
            print(f"🔍 Found {len(friends)} friends")
            return friends
    
    @benchmark("graph_db", "find_friends_of_friends")
    def find_friends_of_friends(self, user_id: str):
        """Find friends of friends (2 degrees away)"""
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (u:User {id: $user_id})-[:FRIENDS_WITH*2]->(fof:User)
                WHERE fof.id <> $user_id
                AND NOT (u)-[:FRIENDS_WITH]->(fof)
                RETURN DISTINCT fof.name AS name, fof.id AS id
                """,
                user_id=user_id
            )
            fofs = [{"name": record["name"], "id": record["id"]} 
                   for record in result]
            print(f"🔍 Found {len(fofs)} friends of friends")
            return fofs
    
    def clear_database(self):
        """Clear all nodes and relationships"""
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            print("🗑️  Database cleared")
    
    @benchmark("graph_db", "shortest_path")
    def find_shortest_path(self, user1_id: str, user2_id: str):
        """Find shortest path between two users"""
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH path = shortestPath(
                    (u1:User {id: $user1_id})-[:FRIENDS_WITH*]-(u2:User {id: $user2_id})
                )
                RETURN [node in nodes(path) | node.name] as path_names,
                    length(path) as degrees_of_separation
                """,
                user1_id=user1_id, user2_id=user2_id
            )
            
            record = result.single()
            if record:
                path = record["path_names"]
                degrees = record["degrees_of_separation"]
                print(f"🔍 Path found: {' -> '.join(path)} ({degrees} degrees)")
                return {
                    "path": path,
                    "degrees_of_separation": degrees
                }
            else:
                print("❌ No path found")
                return None


# Test it out
if __name__ == "__main__":
    graph = GraphDBClient()
    
    # Clear any existing data
    graph.clear_database()
    
    # Create users
    graph.create_user("u1", "Alice", 25)
    graph.create_user("u2", "Bob", 30)
    graph.create_user("u3", "Charlie", 28)
    graph.create_user("u4", "Diana", 26)
    graph.create_user("u5", "Eve", 29)
    
    # Create friendships
    # Alice -> Bob -> Charlie
    # Alice -> Diana -> Eve
    graph.create_friendship("u1", "u2")  # Alice -> Bob
    graph.create_friendship("u2", "u3")  # Bob -> Charlie
    graph.create_friendship("u1", "u4")  # Alice -> Diana
    graph.create_friendship("u4", "u5")  # Diana -> Eve
    
    # Find Alice's direct friends
    print("\n👥 Alice's friends:")
    friends = graph.find_friends("u1")
    for f in friends:
        print(f"  - {f['name']}")
    
    # Find Alice's friends of friends
    print("\n🌐 Alice's friends of friends (people she might know):")
    fofs = graph.find_friends_of_friends("u1")
    for f in fofs:
        print(f"  - {f['name']}")
    
    graph.close()