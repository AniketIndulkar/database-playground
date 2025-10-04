import streamlit as st
import requests
import pandas as pd

# API Base URL
API_BASE = "http://127.0.0.1:8000"

st.set_page_config(page_title="Database Playground", layout="wide")

st.title("🗄️ Database Playground")
st.markdown("Compare different database types and understand when to use each one")

# Sidebar for database selection
db_type = st.sidebar.selectbox(
    "Select Database Type",
    ["Overview", "Object Storage", "Vector Database", "Graph Database", "Columnar Database"]
)

if db_type == "Overview":
    st.header("Database Types Comparison")
    
    comparison_data = {
        "Database": ["Object Storage", "Vector DB", "Graph DB", "Columnar DB"],
        "Best For": [
            "Files, images, videos",
            "Similarity search, AI/ML",
            "Relationships, networks",
            "Analytics, aggregations"
        ],
        "Query Complexity": ["Simple", "Medium", "High", "Medium"],
        "Performance": ["Good", "Excellent", "Excellent", "Excellent"]
    }
    
    st.dataframe(pd.DataFrame(comparison_data), use_container_width=True)
    
    st.subheader("When to Choose Which Database?")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Object Storage")
        st.write("✅ Storing files (PDFs, images, videos)")
        st.write("✅ Backup and archival")
        st.write("✅ Static content delivery")
        st.write("❌ Complex queries")
        st.write("❌ Transactional data")
        
        st.markdown("### Vector Database")
        st.write("✅ Semantic search")
        st.write("✅ Recommendation systems")
        st.write("✅ AI/ML applications")
        st.write("❌ Exact match queries")
        st.write("❌ Relational data")
    
    with col2:
        st.markdown("### Graph Database")
        st.write("✅ Social networks")
        st.write("✅ Fraud detection")
        st.write("✅ Recommendation engines")
        st.write("❌ Simple lookups")
        st.write("❌ Large aggregations")
        
        st.markdown("### Columnar Database")
        st.write("✅ Analytics and reporting")
        st.write("✅ Data warehousing")
        st.write("✅ Business intelligence")
        st.write("❌ Row-by-row updates")
        st.write("❌ OLTP workloads")

elif db_type == "Object Storage":
    st.header("📦 Object Storage (MinIO)")
    
    st.subheader("Upload File")
    uploaded_file = st.file_uploader("Choose a file")
    
    if uploaded_file and st.button("Upload"):
        files = {"file": uploaded_file}
        response = requests.post(f"{API_BASE}/object-storage/upload", files=files)
        if response.status_code == 200:
            st.success(f"✅ File uploaded: {response.json()['object_name']}")
        else:
            st.error("Upload failed")
    
    st.subheader("Stored Files")
    if st.button("Refresh File List"):
        response = requests.get(f"{API_BASE}/object-storage/files")
        if response.status_code == 200:
            files = response.json()['files']
            if files:
                df = pd.DataFrame(files)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No files stored yet")

elif db_type == "Vector Database":
    st.header("🔍 Vector Database (ChromaDB)")
    
    st.subheader("Add Document")
    doc_id = st.text_input("Document ID")
    doc_text = st.text_area("Document Text")
    
    if st.button("Add Document") and doc_id and doc_text:
        response = requests.post(
            f"{API_BASE}/vector-db/add-document",
            json={"doc_id": doc_id, "text": doc_text, "metadata": {}}
        )
        if response.status_code == 200:
            st.success("✅ Document added")
    
    st.subheader("Search Similar Documents")
    search_query = st.text_input("Search Query")
    
    if st.button("Search") and search_query:
        response = requests.post(
            f"{API_BASE}/vector-db/search",
            json={"query": search_query, "top_k": 3}
        )
        if response.status_code == 200:
            results = response.json()
            st.write("**Results:**")
            for i, (doc, dist) in enumerate(zip(results['documents'], results['distances'])):
                st.write(f"{i+1}. {doc} (Distance: {dist:.4f})")

elif db_type == "Graph Database":
    st.header("🕸️ Graph Database (Neo4j)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Create User")
        user_id = st.text_input("User ID")
        name = st.text_input("Name")
        age = st.number_input("Age", min_value=1, max_value=120, value=25)
        
        if st.button("Create User") and user_id and name:
            response = requests.post(
                f"{API_BASE}/graph-db/create-user",
                json={"user_id": user_id, "name": name, "age": age}
            )
            if response.status_code == 200:
                st.success(f"✅ User {name} created")
    
    with col2:
        st.subheader("Create Friendship")
        user1 = st.text_input("User 1 ID")
        user2 = st.text_input("User 2 ID")
        
        if st.button("Create Friendship") and user1 and user2:
            response = requests.post(
                f"{API_BASE}/graph-db/create-friendship",
                json={"user1_id": user1, "user2_id": user2}
            )
            if response.status_code == 200:
                st.success("✅ Friendship created")
    
    st.subheader("Find Friends")
    find_user_id = st.text_input("Enter User ID to find friends")
    
    if st.button("Find Friends") and find_user_id:
        response = requests.get(f"{API_BASE}/graph-db/friends/{find_user_id}")
        if response.status_code == 200:
            friends = response.json()['friends']
            if friends:
                st.write("**Direct Friends:**")
                for friend in friends:
                    st.write(f"- {friend['name']} (ID: {friend['id']})")
            else:
                st.info("No friends found")
    
    if st.button("Find Friends of Friends") and find_user_id:
        response = requests.get(f"{API_BASE}/graph-db/friends-of-friends/{find_user_id}")
        if response.status_code == 200:
            fofs = response.json()['friends_of_friends']
            if fofs:
                st.write("**Friends of Friends (People you might know):**")
                for fof in fofs:
                    st.write(f"- {fof['name']} (ID: {fof['id']})")
            else:
                st.info("No friends of friends found")

elif db_type == "Columnar Database":
    st.header("📊 Columnar Database (DuckDB)")
    
    if st.button("Initialize Sample Data"):
        response = requests.post(f"{API_BASE}/columnar-db/init-sample-data")
        if response.status_code == 200:
            st.success("✅ Sample sales data initialized")
    
    st.subheader("Run Analytics")
    query_type = st.selectbox(
        "Select Analytics Query",
        ["total_by_category", "total_by_region", "top_products"]
    )
    
    if st.button("Run Query"):
        response = requests.get(f"{API_BASE}/columnar-db/analytics/{query_type}")
        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)
            
            # Visualize
            if query_type == "total_by_category":
                st.bar_chart(df.set_index('category')['total_revenue'])
            elif query_type == "total_by_region":
                st.bar_chart(df.set_index('region')['total_revenue'])