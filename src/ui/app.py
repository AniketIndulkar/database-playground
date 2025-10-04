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
    ["Overview", "Object Storage", "Vector Database", "Graph Database", "Columnar Database", "Performance Benchmarks", "E-commerce Scenario"]
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
    
    st.divider()
    st.subheader("🔄 Advanced: File Versioning")
    
    versioned_file = st.file_uploader("Upload with versioning", key="versioned")
    if versioned_file and st.button("Upload Versioned"):
        files = {"file": versioned_file}
        response = requests.post(f"{API_BASE}/object-storage/upload-versioned", files=files)
        if response.status_code == 200:
            st.success(f"✅ Versioned file uploaded: {response.json()['object_name']}")
    
    version_filename = st.text_input("Check versions for file:")
    if st.button("List Versions") and version_filename:
        response = requests.get(f"{API_BASE}/object-storage/versions/{version_filename}")
        if response.status_code == 200:
            versions = response.json()['versions']
            if versions:
                df = pd.DataFrame(versions)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No versions found")

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
    
    st.divider()
    st.subheader("🎯 Advanced: Search with Metadata Filter")
    
    filter_search = st.text_input("Search query with filter")
    filter_category = st.text_input("Filter by category (optional)")
    
    if st.button("Search with Filter") and filter_search:
        payload = {"query": filter_search, "top_k": 3}
        if filter_category:
            payload["metadata_filter"] = {"category": filter_category}
        
        response = requests.post(f"{API_BASE}/vector-db/search", json=payload)
        if response.status_code == 200:
            results = response.json()
            for i, (doc, dist, meta) in enumerate(zip(
                results['documents'], 
                results['distances'],
                results['metadatas']
            )):
                st.write(f"{i+1}. {doc}")
                st.write(f"   Category: {meta.get('category', 'N/A')} | Distance: {dist:.4f}")

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
    
    st.divider()
    st.subheader("🛣️ Advanced: Shortest Path")
    
    col1, col2 = st.columns(2)
    with col1:
        path_user1 = st.text_input("From User ID", key="path1")
    with col2:
        path_user2 = st.text_input("To User ID", key="path2")
    
    if st.button("Find Shortest Path") and path_user1 and path_user2:
        response = requests.get(f"{API_BASE}/graph-db/shortest-path/{path_user1}/{path_user2}")
        if response.status_code == 200:
            result = response.json()
            st.write(f"**Path:** {' → '.join(result['path'])}")
            st.write(f"**Degrees of Separation:** {result['degrees_of_separation']}")
        else:
            st.error("No path found between these users")

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
    
    st.divider()
    st.subheader("📈 Advanced: Running Totals (Window Function)")
    
    if st.button("Calculate Running Totals"):
        response = requests.get(f"{API_BASE}/columnar-db/analytics/running-total")
        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)
            
            # Visualize running totals by region
            for region in df['region'].unique():
                region_data = df[df['region'] == region]
                st.line_chart(region_data.set_index('order_date')['running_total'])
                st.caption(f"{region} - Running Total")

elif db_type == "E-commerce Scenario":
    st.header("🛒 E-commerce: All Databases Working Together")
    
    st.markdown("""
    This scenario demonstrates how all 4 database types work together in a real e-commerce system:
    
    - **Object Storage** → Product images
    - **Vector Database** → Product recommendations (find similar products)
    - **Graph Database** → Customer social network (follows, connections)
    - **Columnar Database** → Sales analytics and business intelligence
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🚀 Initialize System"):
            response = requests.post(f"{API_BASE}/scenarios/ecommerce/initialize")
            if response.status_code == 200:
                st.success("✅ E-commerce system initialized")
    
    with col2:
        if st.button("▶️ Run Complete Demo"):
            with st.spinner("Running demo workflow..."):
                response = requests.post(f"{API_BASE}/scenarios/ecommerce/run-demo")
                if response.status_code == 200:
                    st.success("✅ Demo completed! Check other tabs to see the data")
    
    st.divider()
    
    # Product Search
    st.subheader("🔍 Find Similar Products (Vector DB)")
    search_product = st.text_input("Describe a product you're looking for:")
    
    if st.button("Search") and search_product:
        response = requests.post(
            f"{API_BASE}/scenarios/ecommerce/find-similar",
            params={"query": search_product, "top_k": 3}
        )
        if response.status_code == 200:
            products = response.json()['products']
            st.write("**Recommended Products:**")
            for product in products:
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.write(f"**{product['name']}**")
                with col2:
                    st.write(f"${product['price']}")
                with col3:
                    st.write(f"Match: {product['similarity_score']}")
    
    st.divider()
    
    # Analytics
    st.subheader("📊 Sales Analytics (Columnar DB)")
    
    if st.button("Get Analytics Report"):
        response = requests.get(f"{API_BASE}/scenarios/ecommerce/analytics")
        if response.status_code == 200:
            analytics = response.json()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Revenue by Category**")
                df_cat = pd.DataFrame(analytics['by_category'])
                st.dataframe(df_cat, use_container_width=True)
                if not df_cat.empty:
                    st.bar_chart(df_cat.set_index('category')['total_revenue'])
            
            with col2:
                st.write("**Revenue by Region**")
                df_reg = pd.DataFrame(analytics['by_region'])
                st.dataframe(df_reg, use_container_width=True)
                if not df_reg.empty:
                    st.bar_chart(df_reg.set_index('region')['total_revenue'])
            
            st.write("**Top Products**")
            df_top = pd.DataFrame(analytics['top_products'])
            st.dataframe(df_top, use_container_width=True)

elif db_type == "Performance Benchmarks":
    st.header("⚡ Performance Benchmarks")
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if st.button("Clear Metrics"):
            requests.delete(f"{API_BASE}/benchmarks/clear")
            st.success("Metrics cleared")
        
        if st.button("Refresh Data"):
            st.rerun()
    
    # Get summary data
    response = requests.get(f"{API_BASE}/benchmarks/summary")
    
    if response.status_code == 200:
        summary = response.json()
        
        if not summary:
            st.info("No benchmark data yet. Use the databases to generate metrics!")
        else:
            # Convert to DataFrame
            df = pd.DataFrame(summary)
            
            st.subheader("Summary Statistics")
            st.dataframe(df[['db_type', 'operation', 'count', 'avg_ms', 'min_ms', 'max_ms']], use_container_width=True)
            
            # Visualizations
            st.subheader("Average Response Times by Database")
            
            # Group by database type
            db_avg = df.groupby('db_type')['avg_ms'].mean().sort_values(ascending=False)
            st.bar_chart(db_avg)
            
            st.subheader("Operation Performance Comparison")
            
            # Create pivot for operations
            pivot_data = df.pivot_table(
                values='avg_ms',
                index='operation',
                columns='db_type',
                fill_value=0
            )
            
            st.bar_chart(pivot_data)
            
            # Detailed metrics table
            st.subheader("Detailed Metrics")
            
            # Get all metrics
            all_metrics_response = requests.get(f"{API_BASE}/benchmarks/metrics")
            if all_metrics_response.status_code == 200:
                all_metrics = all_metrics_response.json()
                
                if all_metrics:
                    metrics_df = pd.DataFrame(all_metrics)
                    metrics_df['timestamp'] = pd.to_datetime(metrics_df['timestamp'])
                    
                    # Show last 20 operations
                    st.dataframe(
                        metrics_df[['timestamp', 'db_type', 'operation', 'duration_ms']].tail(20),
                        use_container_width=True
                    )
                    
                    # Performance over time
                    st.subheader("Performance Over Time")
                    
                    # Line chart showing duration trends
                    time_chart_data = metrics_df.set_index('timestamp')[['db_type', 'operation', 'duration_ms']]
                    
                    for db in metrics_df['db_type'].unique():
                        db_data = metrics_df[metrics_df['db_type'] == db]
                        if len(db_data) > 1:
                            st.line_chart(
                                db_data.set_index('timestamp')['duration_ms'],
                                use_container_width=True
                            )
                            st.caption(f"{db} performance trend")