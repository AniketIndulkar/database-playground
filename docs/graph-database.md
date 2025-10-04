# Graph Database (Neo4j) Documentation

## Overview

Graph databases store data as **nodes** (entities) and **edges** (relationships). Unlike relational databases where relationships require expensive JOIN operations, graph databases treat relationships as first-class citizens, making relationship-heavy queries extremely efficient.

## Core Concepts

### Nodes

Nodes represent entities in your data:

```
(Alice:User {name: "Alice", age: 25})
```

- `Alice` - Node identifier (optional)
- `:User` - Label (type of node)
- `{name: "Alice", age: 25}` - Properties (key-value pairs)

### Relationships (Edges)

Relationships connect nodes and have direction:

```
(Alice)-[:FRIENDS_WITH]->(Bob)
```

- `-[:FRIENDS_WITH]->` - Directed relationship with type
- Relationships can also have properties:

```
(Alice)-[:FRIENDS_WITH {since: 2020}]->(Bob)
```

### Labels

Labels categorize nodes (like tables in SQL):

```
(:User)       - User nodes
(:Product)    - Product nodes
(:Company)    - Company nodes
```

A node can have multiple labels:

```
(:Person:Employee)
```

## Cypher Query Language

Neo4j uses **Cypher**, a declarative query language designed for graphs.

### Basic Patterns

**Create a node:**
```cypher
CREATE (u:User {name: "Alice", age: 25})
```

**Create a relationship:**
```cypher
MATCH (a:User {name: "Alice"})
MATCH (b:User {name: "Bob"})
CREATE (a)-[:FRIENDS_WITH]->(b)
```

**Find nodes:**
```cypher
MATCH (u:User {name: "Alice"})
RETURN u
```

**Find relationships:**
```cypher
MATCH (a:User)-[r:FRIENDS_WITH]->(b:User)
RETURN a, r, b
```

### Pattern Matching

Graph databases excel at pattern matching:

**Direct friends:**
```cypher
MATCH (u:User {id: "alice"})-[:FRIENDS_WITH]->(friend)
RETURN friend
```

**Friends of friends (2 hops):**
```cypher
MATCH (u:User {id: "alice"})-[:FRIENDS_WITH*2]->(fof)
RETURN fof
```

**Variable-length paths (1-3 hops):**
```cypher
MATCH (u:User {id: "alice"})-[:FRIENDS_WITH*1..3]->(connection)
RETURN connection
```

**Shortest path:**
```cypher
MATCH p = shortestPath(
  (alice:User {name: "Alice"})-[:FRIENDS_WITH*]-(bob:User {name: "Bob"})
)
RETURN p
```

## Key Advantages

### 1. Relationship Queries are Fast

**Relational DB (slow):**
```sql
-- Find friends of friends
SELECT u3.name 
FROM users u1
JOIN friendships f1 ON u1.id = f1.user_id
JOIN users u2 ON f1.friend_id = u2.id
JOIN friendships f2 ON u2.id = f2.user_id
JOIN users u3 ON f2.friend_id = u3.id
WHERE u1.id = 'alice'
  AND u3.id != 'alice'
  AND u3.id NOT IN (
    SELECT friend_id FROM friendships WHERE user_id = 'alice'
  )
```

**Graph DB (fast):**
```cypher
MATCH (alice:User {id: "alice"})-[:FRIENDS_WITH*2]->(fof)
WHERE NOT (alice)-[:FRIENDS_WITH]->(fof)
RETURN fof
```

### 2. Index-Free Adjacency

In graph databases, each node directly references its adjacent nodes. No index lookups needed for traversal - just follow pointers.

**Performance:**
- Relational: O(n log n) with indexes, O(n²) without
- Graph: O(1) per hop regardless of database size

### 3. Intuitive Data Modeling

Graphs naturally represent real-world relationships:
- Social networks
- Recommendation engines
- Knowledge graphs
- Fraud detection networks
- Supply chain dependencies

## When to Use Graph Databases

### Ideal Use Cases

**1. Social Networks**
- Friend suggestions (friends of friends)
- Influence analysis
- Community detection
- Six degrees of separation

**2. Recommendation Systems**
- "Customers who bought this also bought..."
- Content recommendations based on user behavior
- Collaborative filtering

**3. Fraud Detection**
- Identify suspicious patterns
- Find rings of fraudulent accounts
- Detect money laundering chains

**4. Knowledge Graphs**
- Wikipedia-style linked data
- Semantic search
- Question answering systems

**5. Network and IT Operations**
- Dependency mapping
- Impact analysis (what breaks if X fails?)
- Root cause analysis

**6. Access Control**
- Role-based permissions
- Inherited access rights
- Complex authorization rules

### When NOT to Use Graph Databases

**Simple lookups by ID:**
```cypher
MATCH (u:User {id: "123"})
RETURN u
```
Use key-value store instead.

**Aggregations over large datasets:**
```cypher
MATCH (p:Product)
RETURN AVG(p.price), SUM(p.quantity)
```
Use columnar database instead.

**No relationship queries:**
If you're not traversing relationships, traditional databases are simpler.

**High-volume transactional updates:**
Graph databases optimize for reads, not rapid writes.

## Neo4j Architecture

### Storage

Neo4j stores data in fixed-size records optimized for traversal:

```
data/databases/neo4j/
  ├── neostore.nodestore.db          # Nodes
  ├── neostore.relationshipstore.db  # Relationships
  ├── neostore.propertystore.db      # Properties
  └── neostore.labeltokenstore.db    # Labels
```

### Indexes

While traversal is index-free, you still need indexes for entry points:

```cypher
CREATE INDEX user_id FOR (u:User) ON (u.id)
```

Without this, `MATCH (u:User {id: "alice"})` would scan all User nodes.

### Transactions

Neo4j is ACID compliant:

```python
with driver.session() as session:
    with session.begin_transaction() as tx:
        tx.run("CREATE (u:User {name: 'Alice'})")
        tx.run("CREATE (u:User {name: 'Bob'})")
        tx.commit()  # or tx.rollback()
```

## Python Client Usage

### Connection Management

```python
from neo4j import GraphDatabase

# Create driver (reuse across application)
driver = GraphDatabase.driver(
    "bolt://localhost:7687",
    auth=("neo4j", "password")
)

# Use sessions for queries
with driver.session() as session:
    result = session.run("MATCH (n) RETURN n")
    
# Close when done
driver.close()
```

### Running Queries

**Simple query:**
```python
result = session.run(
    "MATCH (u:User {name: $name}) RETURN u",
    name="Alice"
)
for record in result:
    print(record["u"])
```

**Transaction functions (recommended):**
```python
def create_user(tx, name, age):
    result = tx.run(
        "CREATE (u:User {name: $name, age: $age}) RETURN u",
        name=name, age=age
    )
    return result.single()[0]

with driver.session() as session:
    user = session.execute_write(create_user, "Alice", 25)
```

### Working with Results

```python
result = session.run("MATCH (u:User) RETURN u.name AS name, u.age AS age")

# Iterate records
for record in result:
    print(f"{record['name']}: {record['age']}")

# Get single result
result = session.run("MATCH (u:User {id: $id}) RETURN u", id="123")
user = result.single()[0]

# Get all results
result = session.run("MATCH (u:User) RETURN u")
users = [record["u"] for record in result]
```

## Common Graph Patterns

### 1. Social Network

```cypher
// Create users
CREATE (alice:User {name: "Alice"})
CREATE (bob:User {name: "Bob"})
CREATE (charlie:User {name: "Charlie"})

// Create friendships
CREATE (alice)-[:FRIENDS_WITH]->(bob)
CREATE (bob)-[:FRIENDS_WITH]->(charlie)

// Find mutual friends
MATCH (alice:User {name: "Alice"})-[:FRIENDS_WITH]->(mutual)<-[:FRIENDS_WITH]-(bob:User {name: "Bob"})
RETURN mutual

// Degrees of separation
MATCH path = shortestPath(
  (alice:User {name: "Alice"})-[:FRIENDS_WITH*]-(charlie:User {name: "Charlie"})
)
RETURN length(path)
```

### 2. Recommendation System

```cypher
// Users who liked similar products
MATCH (user:User {id: "alice"})-[:LIKES]->(product:Product)
      <-[:LIKES]-(other:User)-[:LIKES]->(recommendation:Product)
WHERE NOT (user)-[:LIKES]->(recommendation)
RETURN recommendation, COUNT(*) AS score
ORDER BY score DESC
LIMIT 10
```

### 3. Organizational Hierarchy

```cypher
// Create org structure
CREATE (ceo:Employee {name: "CEO"})
CREATE (vp1:Employee {name: "VP Sales"})
CREATE (vp2:Employee {name: "VP Engineering"})
CREATE (manager:Employee {name: "Engineering Manager"})
CREATE (developer:Employee {name: "Developer"})

CREATE (ceo)-[:MANAGES]->(vp1)
CREATE (ceo)-[:MANAGES]->(vp2)
CREATE (vp2)-[:MANAGES]->(manager)
CREATE (manager)-[:MANAGES]->(developer)

// Find all reports under VP Engineering
MATCH (vp:Employee {name: "VP Engineering"})-[:MANAGES*]->(report)
RETURN report
```

### 4. Supply Chain Dependencies

```cypher
// Find impact of component failure
MATCH (component:Part {id: "chip-x"})<-[:DEPENDS_ON*]-(affected)
RETURN affected

// Find critical single points of failure
MATCH (part:Part)<-[:DEPENDS_ON]-(dependent)
WITH part, COUNT(dependent) AS dependents
WHERE dependents > 10
RETURN part, dependents
ORDER BY dependents DESC
```

## Performance Optimization

### 1. Use Indexes

```cypher
// Create index on frequently-queried properties
CREATE INDEX user_email FOR (u:User) ON (u.email)

// Check existing indexes
SHOW INDEXES
```

### 2. Limit Traversal Depth

```cypher
// Bad: unlimited depth
MATCH (a)-[:FRIENDS_WITH*]->(b)

// Good: limit depth
MATCH (a)-[:FRIENDS_WITH*1..3]->(b)
```

### 3. Use LIMIT Early

```cypher
// Get first 10, then process
MATCH (u:User)
WITH u LIMIT 10
MATCH (u)-[:FRIENDS_WITH]->(friend)
RETURN u, friend
```

### 4. Profile Queries

```cypher
PROFILE MATCH (u:User {email: "alice@example.com"})
RETURN u
```

Shows execution plan and actual row counts.

## Advanced Features

### Aggregations

```cypher
// Count friends per user
MATCH (u:User)-[:FRIENDS_WITH]->(friend)
RETURN u.name, COUNT(friend) AS friend_count
ORDER BY friend_count DESC

// Most connected users
MATCH (u:User)
WITH u, SIZE((u)-[:FRIENDS_WITH]->()) AS connections
WHERE connections > 10
RETURN u.name, connections
```

### Conditional Logic

```cypher
MATCH (u:User)
RETURN u.name,
       CASE 
         WHEN u.age < 18 THEN "Minor"
         WHEN u.age < 65 THEN "Adult"
         ELSE "Senior"
       END AS category
```

### List Operations

```cypher
// Collect friends into list
MATCH (u:User {name: "Alice"})-[:FRIENDS_WITH]->(friend)
RETURN u.name, COLLECT(friend.name) AS friends

// Unwind list into rows
WITH ["Alice", "Bob", "Charlie"] AS names
UNWIND names AS name
CREATE (u:User {name: name})
```

### Path Operations

```cypher
// Find all paths between two users
MATCH path = (alice:User {name: "Alice"})-[:FRIENDS_WITH*]-(bob:User {name: "Bob"})
RETURN path, length(path) AS hops
ORDER BY hops
LIMIT 1
```

## Comparison with Other Databases

| Feature | Graph DB | Relational DB | Document DB |
|---------|----------|---------------|-------------|
| **Relationship queries** | Excellent | Poor (JOINs) | Poor |
| **Hierarchical data** | Excellent | Medium | Good |
| **Aggregations** | Medium | Excellent | Medium |
| **Schema flexibility** | High | Low | High |
| **ACID compliance** | Yes | Yes | Varies |
| **Horizontal scaling** | Limited | Good | Excellent |

## Best Practices

### 1. Model for Queries

Design your graph based on the questions you need to answer:

```cypher
// If you frequently ask "Who are Alice's friends?"
(Alice)-[:FRIENDS_WITH]->(friend)

// If you ask "What products did Alice buy?"
(Alice)-[:PURCHASED]->(product)
```

### 2. Bidirectional vs Unidirectional

```cypher
// Bidirectional (two relationships)
CREATE (a)-[:FRIENDS_WITH]->(b)
CREATE (b)-[:FRIENDS_WITH]->(a)

// Query either direction
MATCH (a)-[:FRIENDS_WITH]-(b)  // Note: no arrow direction

// Unidirectional (one relationship)
CREATE (user)-[:PURCHASED]->(product)

// Query specific direction
MATCH (user)-[:PURCHASED]->(product)
```

### 3. Denormalization is OK

Unlike relational databases, duplicating data can improve query performance:

```cypher
// Store calculated value on relationship
CREATE (a)-[:FRIENDS_WITH {since: 2020, years_known: 4}]->(b)
```

### 4. Use Specific Relationship Types

```cypher
// Bad: generic relationship
(a)-[:RELATED_TO]->(b)

// Good: specific relationships
(user)-[:PURCHASED]->(product)
(user)-[:REVIEWED]->(product)
(user)-[:VIEWED]->(product)
```

## Troubleshooting

### Query is Slow

1. Add indexes on entry point properties
2. Limit traversal depth
3. Use `PROFILE` to see execution plan
4. Consider adding more specific relationship types

### Out of Memory

1. Use `LIMIT` to reduce result set
2. Process in batches
3. Increase heap size in neo4j.conf

### Connection Issues

```python
# Check Neo4j is running
docker ps | grep neo4j

# Verify connection
from neo4j import GraphDatabase
driver = GraphDatabase.driver(
    "bolt://localhost:7687",
    auth=("neo4j", "password")
)
driver.verify_connectivity()
```

## Tools and Resources

### Neo4j Browser

Web interface at `http://localhost:7474`:
- Visualize graphs
- Run Cypher queries
- Explore data interactively

### Neo4j Desktop

Desktop application with built-in tools and plugins.

### Awesome Procedures (APOC)

Library with 450+ procedures for common tasks:

```cypher
// Load JSON
CALL apoc.load.json("https://api.example.com/data")

// Generate random graph
CALL apoc.generate.ba(100, 2, 'User', 'FRIENDS_WITH')
```

### Documentation

- [Neo4j Cypher Manual](https://neo4j.com/docs/cypher-manual/)
- [Neo4j Python Driver](https://neo4j.com/docs/python-manual/)
- [Graph Data Modeling](https://neo4j.com/developer/data-modeling/)

## Summary

Graph databases excel at:
- Relationship-heavy queries
- Pattern matching
- Pathfinding
- Network analysis

Key takeaways:
1. Nodes and relationships are both first-class citizens
2. Traversal is O(1) per hop
3. Model your graph based on your queries
4. Use Cypher for intuitive pattern matching
5. Index your entry points

---

**Next Steps:**
- Experiment with different graph patterns
- Try more complex traversals (3+ hops)
- Build a recommendation system
- Explore shortest path algorithms