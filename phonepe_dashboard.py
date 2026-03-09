#!/usr/bin/env python3
"""
PhonePe Data Analytics Dashboard
===============================
A Streamlit dashboard for visualizing PhonePe transaction and user data.
Run with: streamlit run phonepe_dashboard.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Page config
st.set_page_config(
    page_title="PhonePe Analytics Dashboard",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data
def load_data():
    """Load data from CSV files"""
    # Load transactions data
    tx_df = pd.read_csv("phonepe_transactions.csv")
    
    # Rename columns to match expected format
    tx_df = tx_df.rename(columns={
        'Quater': 'Quarter',
        'Transacion_type': 'Transaction_type',
        'Transacion_count': 'Transaction_count',
        'Transacion_amount': 'Transaction_amount'
    })
    
    # Create a mock users dataframe from transactions for demonstration
    users_df = tx_df[['State', 'Year', 'Quarter']].copy()
    users_df['Registered_users'] = (tx_df['Transaction_count'] * 100).astype(int)
    users_df['App_opens'] = (tx_df['Transaction_count'] * 150).astype(int)
    
    # State-wise transaction totals
    state_tx = tx_df.groupby('State').agg({
        'Transaction_count': 'sum',
        'Transaction_amount': 'sum'
    }).reset_index()
    state_tx.columns = ['State', 'Total_Transactions', 'Total_Amount']
    
    # Transaction type breakdown
    tx_type = tx_df.groupby('Transaction_type').agg({
        'Transaction_count': 'sum',
        'Transaction_amount': 'sum'
    }).reset_index()
    tx_type.columns = ['Transaction_type', 'Total_Count', 'Total_Amount']
    
    # Quarterly aggregated data
    quarterly = tx_df.groupby(['Year', 'Quarter']).agg({
        'Transaction_count': 'sum',
        'Transaction_amount': 'sum'
    }).reset_index()
    quarterly.columns = ['Year', 'Quarter', 'Total_Count', 'Total_Amount']
    
    # Latest users by state (using mock data)
    latest_users = users_df.groupby('State').agg({
        'Year': 'max',
        'Quarter': 'max',
        'Registered_users': 'sum',
        'App_opens': 'sum'
    }).reset_index()
    
    return tx_df, users_df, state_tx, tx_type, quarterly, latest_users

# Custom CSS
st.markdown("""
    <style>
    .main {
        background-color: #f5f5f5;
    }
    .stMetric {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    .title {
        color: #6f42c1;
        font-size: 36px;
        font-weight: bold;
    }
    .subtitle {
        color: #666;
        font-size: 18px;
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    # Header
    st.markdown('<p class="title">📱 PhonePe Data Analytics Dashboard</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Comprehensive analysis of digital payments across India (2018-2024)</p>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Load data
    with st.spinner('Loading data...'):
        tx_df, users_df, state_tx, tx_type, quarterly, latest_users = load_data()
    
    # Sidebar
    st.sidebar.title("🎛️ Filters")
    
    # Year filter
    years = sorted(tx_df['Year'].unique())
    selected_year = st.sidebar.selectbox("Select Year", ["All"] + list(years))
    
    # Quarter filter
    quarters = sorted(tx_df['Quarter'].unique())
    selected_quarter = st.sidebar.selectbox("Select Quarter", ["All"] + list(quarters))
    
    # Filter data based on selection
    filtered_tx = tx_df.copy()
    if selected_year != "All":
        filtered_tx = filtered_tx[filtered_tx['Year'] == selected_year]
    if selected_quarter != "All":
        filtered_tx = filtered_tx[filtered_tx['Quarter'] == selected_quarter]
    
    # ====== KEY METRICS ======
    st.header("📊 Key Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_tx = filtered_tx['Transaction_count'].sum()
    total_amount = filtered_tx['Transaction_amount'].sum()
    total_users = latest_users['Registered_users'].sum()
    total_states = len(latest_users)
    
    with col1:
        st.metric("Total Transactions", f"{total_tx/1e9:.2f}B")
    with col2:
        st.metric("Transaction Value", f"₹{total_amount/1e12:.2f}L Cr")
    with col3:
        st.metric("Registered Users", f"{total_users/1e7:.2f}Cr")
    with col4:
        st.metric("States/UTs Covered", total_states)
    
    st.markdown("---")
    
    # ====== TABS FOR DIFFERENT ANALYSES ======
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🏆 State Analysis", 
        "💳 Transaction Types", 
        "📈 Growth Trends",
        "👥 User Analysis",
        "📋 Raw Data"
    ])
    
    with tab1:
        st.header("State-wise Analysis")
        
        # Top States by Transaction Amount
        st.subheader("Top 10 States by Transaction Amount")
        top_states = state_tx.nlargest(10, 'Total_Amount').copy()
        top_states['Amount_Crores'] = top_states['Total_Amount'] / 1e7
        
        fig = px.bar(
            top_states,
            x='State',
            y='Amount_Crores',
            title='Top 10 States by Transaction Amount (₹ Crores)',
            color='Amount_Crores',
            color_continuous_scale='Viridis',
            labels={'Amount_Crores': 'Amount (₹ Crores)'}
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
        
        # Interactive map
        st.subheader("Geographic Distribution")
        
        # Format state names for map
        state_tx_map = state_tx.copy()
        state_tx_map['State_formatted'] = state_tx_map['State'].str.replace("-", " ").str.title()
        state_tx_map['Amount_Crores'] = state_tx_map['Total_Amount'] / 1e7
        
        fig = px.choropleth(
            state_tx_map,
            geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
            featureidkey="properties.ST_NM",
            locations="State_formatted",
            color="Amount_Crores",
            color_continuous_scale="Greens",
            title="PhonePe Transaction Value by State (₹ Crores)",
            hover_name="State"
        )
        fig.update_geos(fitbounds="locations", visible=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.header("Transaction Type Analysis")
        
        # Pie chart
        col1, col2 = st.columns(2)
        
        with col1:
            tx_type_pie = tx_type.copy()
            tx_type_pie['Amount_Crores'] = tx_type_pie['Total_Amount'] / 1e7
            
            fig = px.pie(
                tx_type_pie,
                values='Total_Amount',
                names='Transaction_type',
                title='Transaction Distribution by Type',
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Bar chart
            fig = px.bar(
                tx_type,
                x='Transaction_type',
                y='Total_Amount',
                title='Transaction Amount by Type',
                color='Transaction_type',
                labels={'Total_Amount': 'Amount (₹)'}
            )
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
        
        # Transaction breakdown table
        st.subheader("Transaction Type Breakdown")
        tx_summary = tx_type.copy()
        tx_summary['Amount_Crores'] = tx_summary['Total_Amount'] / 1e7
        tx_summary['Percentage'] = (tx_summary['Total_Amount'] / tx_summary['Total_Amount'].sum() * 100).round(2)
        tx_summary = tx_summary.sort_values('Total_Amount', ascending=False)
        
        st.dataframe(
            tx_summary[['Transaction_type', 'Total_Count', 'Amount_Crores', 'Percentage']],
            column_config={
                "Transaction_type": "Transaction Type",
                "Total_Count": st.column_config.NumberColumn("Count", format="%.0f"),
                "Amount_Crores": st.column_config.NumberColumn("Amount (₹ Cr)", format="%.2f"),
                "Percentage": st.column_config.NumberColumn("% Share", format="%.2f%%")
            },
            use_container_width=True
        )
    
    with tab3:
        st.header("Growth Trends Analysis")
        
        # Quarterly trend
        quarterly['Amount_Crores'] = quarterly['Total_Amount'] / 1e7
        quarterly['Quarter_Label'] = quarterly['Year'].astype(str) + '-Q' + quarterly['Quarter'].astype(str)
        
        # Line chart
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        fig.add_trace(
            go.Scatter(
                x=quarterly['Quarter_Label'], 
                y=quarterly['Amount_Crores'],
                name="Amount (₹ Cr)",
                mode='lines+markers',
                line=dict(color='#6f42c1', width=3)
            ),
            secondary_y=False
        )
        
        fig.add_trace(
            go.Scatter(
                x=quarterly['Quarter_Label'], 
                y=quarterly['Total_Count']/1e9,
                name="Count (Billions)",
                mode='lines+markers',
                line=dict(color='#28a745', width=2, dash='dash')
            ),
            secondary_y=True
        )
        
        fig.update_layout(
            title="Quarter-wise Transaction Growth",
            xaxis_title="Quarter",
            hovermode="x unified"
        )
        fig.update_yaxes(title_text="Amount (₹ Crores)", secondary_y=False)
        fig.update_yaxes(title_text="Count (Billions)", secondary_y=True)
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Year-over-Year growth
        st.subheader("Year-over-Year Analysis")
        
        yearly = quarterly.groupby('Year')['Total_Amount'].sum().reset_index()
        yearly['Amount_Crores'] = yearly['Total_Amount'] / 1e7
        yearly['YoY_Growth'] = yearly['Total_Amount'].pct_change() * 100
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.bar(
                yearly,
                x='Year',
                y='Amount_Crores',
                title='Annual Transaction Volume (₹ Crores)',
                color='Amount_Crores',
                color_continuous_scale='Blues'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.line(
                yearly,
                x='Year',
                y='YoY_Growth',
                title='Year-over-Year Growth Rate (%)',
                markers=True,
                color_discrete_sequence=['#28a745']
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        st.header("User Analysis")
        
        # Top states by users
        st.subheader("Top 10 States by Registered Users")
        
        top_users = latest_users.nlargest(10, 'Registered_users').copy()
        
        fig = px.bar(
            top_users,
            x='State',
            y='Registered_users',
            title='Top 10 States by Registered Users',
            color='Registered_users',
            color_continuous_scale='Oranges',
            labels={'Registered_users': 'Registered Users'}
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
        
        # User distribution
        st.subheader("User Distribution")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Pie chart for top users
            top10 = latest_users.nlargest(10, 'Registered_users')
            others = latest_users[~latest_users['State'].isin(top10['State'])]
            pie_data = pd.concat([
                top10[['State', 'Registered_users']],
                pd.DataFrame({'State': ['Others'], 'Registered_users': [others['Registered_users'].sum()]})
            ])
            
            fig = px.pie(
                pie_data,
                values='Registered_users',
                names='State',
                title='User Distribution',
                hole=0.4
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # App opens analysis
            top_app_opens = latest_users.nlargest(10, 'App_opens')
            
            fig = px.bar(
                top_app_opens,
                x='State',
                y='App_opens',
                title='Top 10 States by App Opens',
                color='App_opens',
                color_continuous_scale='Reds'
            )
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
    
    with tab5:
        st.header("Raw Data")
        
        st.subheader("Transactions Data")
        st.dataframe(tx_df.head(100), use_container_width=True)
        
        st.subheader("Users Data")
        st.dataframe(users_df.head(100), use_container_width=True)
        
        # Download options
        st.subheader("Export Data")
        
        col1, col2 = st.columns(2)
        
        with col1:
            csv_tx = tx_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Download Transactions CSV",
                csv_tx,
                "phonepe_transactions.csv",
                "text/csv"
            )
        
        with col2:
            csv_users = users_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Download Users CSV",
                csv_users,
                "phonepe_users.csv",
                "text/csv"
            )
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>📱 PhonePe Data Analytics Dashboard | Data Source: PhonePe Pulse</p>
        <p>Analysis Period: 2018 - 2024</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
