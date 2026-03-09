#!/usr/bin/env python3
"""
PhonePe Data Analytics - Comprehensive Analysis
================================================
This script analyzes PhonePe transaction and user data across Indian states.
Features:
- State-wise user analysis
- Transaction type analysis  
- Top performing states
- Quarter-wise growth trends
- Interactive visualizations
"""

import os
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

# Configuration
PULSE_PATH = os.path.join(os.path.dirname(__file__), "pulse", "data")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "analysis_output")

# Create output directory
os.makedirs(OUTPUT_DIR, exist_ok=True)

def load_transaction_data():
    """Load aggregated transaction data from pulse repository"""
    print("Loading transaction data...")
    
    path = os.path.join(PULSE_PATH, "aggregated", "transaction", "country", "india", "state")
    Agg_state_list = os.listdir(path)
    
    clm = {
        'State': [], 'Year': [], 'Quarter': [], 
        'Transaction_type': [], 'Transaction_count': [], 'Transaction_amount': []
    }
    
    for i in Agg_state_list:
        p_i = path + "/" + i + "/"
        if not os.path.isdir(p_i):
            continue
        Agg_yr = os.listdir(p_i)
        for j in Agg_yr:
            p_j = p_i + j + "/"
            if not os.path.isdir(p_j):
                continue
            Agg_yr_list = os.listdir(p_j)
            for k in Agg_yr_list:
                p_k = p_j + k
                try:
                    with open(p_k, 'r') as Data:
                        D = json.load(Data)
                        for z in D['data']['transactionData']:
                            Name = z['name']
                            count = z['paymentInstruments'][0]['count']
                            amount = z['paymentInstruments'][0]['amount']
                            clm['Transaction_type'].append(Name)
                            clm['Transaction_count'].append(count)
                            clm['Transaction_amount'].append(amount)
                            clm['State'].append(i)
                            clm['Year'].append(j)
                            clm['Quarter'].append(int(k.strip('.json')))
                except Exception as e:
                    continue
    
    df = pd.DataFrame(clm)
    print(f"  Loaded {len(df):,} transaction records")
    return df

def load_user_data():
    """Load user data from pulse repository"""
    print("Loading user data...")
    
    path = os.path.join(PULSE_PATH, "aggregated", "user", "country", "india", "state")
    states = os.listdir(path)
    
    clm = {'State': [], 'Year': [], 'Quarter': [], 'Registered_users': [], 'App_opens': []}
    
    for state in states:
        state_path = path + "/" + state
        if not os.path.isdir(state_path):
            continue
        years = os.listdir(state_path)
        for year in years:
            year_path = state_path + "/" + year
            if not os.path.isdir(year_path):
                continue
            quarters = os.listdir(year_path)
            for quarter in quarters:
                try:
                    quarter_file = year_path + "/" + quarter
                    with open(quarter_file, 'r') as f:
                        data = json.load(f)
                        users = data['data']['aggregated']['registeredUsers']
                        app_opens = data['data']['aggregated']['appOpens']
                        clm['State'].append(state)
                        clm['Year'].append(year)
                        clm['Quarter'].append(int(quarter.strip('.json')))
                        clm['Registered_users'].append(users)
                        clm['App_opens'].append(app_opens)
                except Exception as e:
                    continue
    
    df = pd.DataFrame(clm)
    print(f"  Loaded {len(df):,} user records")
    return df

def analyze_state_wise_users(user_df):
    """Analyze users state-wise"""
    print("\n" + "="*60)
    print("ANALYSIS 1: STATE-WISE USER ANALYSIS")
    print("="*60)
    
    # Latest quarter users by state
    latest = user_df.sort_values(['Year', 'Quarter']).groupby('State').last().reset_index()
    
    # Top 10 states by registered users
    top_states = latest.nlargest(10, 'Registered_users')[['State', 'Registered_users', 'App_opens', 'Year', 'Quarter']]
    top_states['Registered_users'] = top_states['Registered_users'].apply(lambda x: f"{x:,.0f}")
    top_states['App_opens'] = top_states['App_opens'].apply(lambda x: f"{x:,.0f}")
    
    print("\n📊 TOP 10 STATES BY REGISTERED USERS:")
    print("-" * 60)
    print(top_states.to_string(index=False))
    
    # Create visualization
    fig = px.bar(
        latest.nlargest(20, 'Registered_users'),
        x='State',
        y='Registered_users',
        title='Top 20 States by Registered PhonePe Users',
        labels={'Registered_users': 'Registered Users', 'State': 'State'},
        color='Registered_users',
        color_continuous_scale='viridis'
    )
    fig.update_layout(xaxis_tickangle=-45)
    fig.write_html(os.path.join(OUTPUT_DIR, "state_wise_users.html"))
    
    # Total users
    total_users = latest['Registered_users'].sum()
    print(f"\n📈 Total Registered Users (All States): {total_users:,.0f}")
    
    return latest

def analyze_transaction_types(transaction_df):
    """Analyze different transaction types"""
    print("\n" + "="*60)
    print("ANALYSIS 2: TRANSACTION TYPE ANALYSIS")
    print("="*60)
    
    # Transaction types summary
    type_summary = transaction_df.groupby('Transaction_type').agg({
        'Transaction_count': 'sum',
        'Transaction_amount': 'sum'
    }).reset_index()
    
    type_summary['Transaction_amount_in_crores'] = type_summary['Transaction_amount'] / 10000000
    type_summary = type_summary.sort_values('Transaction_amount', ascending=False)
    
    print("\n📊 TRANSACTION TYPES BREAKDOWN:")
    print("-" * 70)
    print(f"{'Transaction Type':<30} {'Count':>15} {'Amount (₹ Crores)':>20}")
    print("-" * 70)
    for _, row in type_summary.iterrows():
        print(f"{row['Transaction_type']:<30} {row['Transaction_count']:>15,.0f} {row['Transaction_amount_in_crores']:>20,.2f}")
    
    # Pie chart for transaction types
    fig = px.pie(
        type_summary,
        values='Transaction_amount',
        names='Transaction_type',
        title='Transaction Distribution by Type',
        hole=0.4
    )
    fig.write_html(os.path.join(OUTPUT_DIR, "transaction_types_pie.html"))
    
    # Bar chart for transaction types
    fig = px.bar(
        type_summary,
        x='Transaction_type',
        y='Transaction_amount_in_crores',
        title='Transaction Amount by Type (₹ Crores)',
        color='Transaction_type'
    )
    fig.update_layout(xaxis_tickangle=-45)
    fig.write_html(os.path.join(OUTPUT_DIR, "transaction_types_bar.html"))
    
    return type_summary

def analyze_top_states(transaction_df):
    """Analyze top performing states"""
    print("\n" + "="*60)
    print("ANALYSIS 3: TOP PERFORMING STATES")
    print("="*60)
    
    # Aggregate by state
    state_summary = transaction_df.groupby('State').agg({
        'Transaction_count': 'sum',
        'Transaction_amount': 'sum'
    }).reset_index()
    
    state_summary['Transaction_amount_in_crores'] = state_summary['Transaction_amount'] / 10000000
    state_summary = state_summary.sort_values('Transaction_amount', ascending=False)
    
    print("\n📊 TOP 10 STATES BY TRANSACTION AMOUNT:")
    print("-" * 70)
    print(f"{'Rank':<5} {'State':<35} {'Count':>15} {'Amount (₹ Crores)':>20}")
    print("-" * 70)
    for idx, (_, row) in enumerate(state_summary.head(10).iterrows(), 1):
        print(f"{idx:<5} {row['State']:<35} {row['Transaction_count']:>15,.0f} {row['Transaction_amount_in_crores']:>20,.2f}")
    
    # Visualization
    fig = px.bar(
        state_summary.head(15),
        x='State',
        y='Transaction_amount_in_crores',
        title='Top 15 States by Transaction Amount (₹ Crores)',
        color='Transaction_amount_in_crores',
        color_continuous_scale='greens'
    )
    fig.update_layout(xaxis_tickangle=-45)
    fig.write_html(os.path.join(OUTPUT_DIR, "top_states.html"))
    
    # Choropleth map
    state_summary['State_formatted'] = state_summary['State'].str.replace("-", " ").str.title()
    
    fig = px.choropleth(
        state_summary,
        geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
        featureidkey="properties.ST_NM",
        locations="State_formatted",
        color="Transaction_amount_in_crores",
        color_continuous_scale="greens",
        title="PhonePe Transaction Amount by State (₹ Crores)"
    )
    fig.update_geos(fitbounds="locations", visible=False)
    fig.write_html(os.path.join(OUTPUT_DIR, "india_map.html"))
    
    return state_summary

def analyze_quarterly_growth(transaction_df, user_df):
    """Analyze quarter-wise growth"""
    print("\n" + "="*60)
    print("ANALYSIS 4: QUARTER-WISE GROWTH ANALYSIS")
    print("="*60)
    
    # Create Year-Quarter combination
    transaction_df['Year_Quarter'] = transaction_df['Year'].astype(str) + '-Q' + transaction_df['Quarter'].astype(str)
    
    # Quarterly transaction growth
    quarterly_tx = transaction_df.groupby('Year_Quarter').agg({
        'Transaction_count': 'sum',
        'Transaction_amount': 'sum'
    }).reset_index()
    
    quarterly_tx['Transaction_amount_in_crores'] = quarterly_tx['Transaction_amount'] / 10000000
    quarterly_tx = quarterly_tx.sort_values('Year_Quarter')
    
    # Calculate growth rate
    quarterly_tx['Growth_Rate'] = quarterly_tx['Transaction_amount'].pct_change() * 100
    
    print("\n📊 QUARTERLY TRANSACTION GROWTH:")
    print("-" * 80)
    print(f"{'Quarter':<12} {'Count':>18} {'Amount (₹ Crores)':>20} {'Growth Rate':>15}")
    print("-" * 80)
    for _, row in quarterly_tx.iterrows():
        growth = f"{row['Growth_Rate']:.2f}%" if pd.notna(row['Growth_Rate']) else "N/A"
        print(f"{row['Year_Quarter']:<12} {row['Transaction_count']:>18,.0f} {row['Transaction_amount_in_crores']:>20,.2f} {growth:>15}")
    
    # Line chart for growth
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig.add_trace(
        go.Scatter(x=quarterly_tx['Year_Quarter'], y=quarterly_tx['Transaction_amount_in_crores'],
                   name="Amount (₹ Crores)", mode='lines+markers'),
        secondary_y=False
    )
    fig.add_trace(
        go.Scatter(x=quarterly_tx['Year_Quarter'], y=quarterly_tx['Transaction_count']/1e9,
                   name="Count (Billions)", mode='lines+markers', line=dict(dash='dash')),
        secondary_y=True
    )
    
    fig.update_layout(
        title='Quarter-wise Transaction Growth',
        xaxis_title='Quarter',
        hovermode="x unified"
    )
    fig.update_yaxes(title_text="Amount (₹ Crores)", secondary_y=False)
    fig.update_yaxes(title_text="Count (Billions)", secondary_y=True)
    fig.write_html(os.path.join(OUTPUT_DIR, "quarterly_growth.html"))
    
    # User growth analysis
    user_df['Year_Quarter'] = user_df['Year'].astype(str) + '-Q' + user_df['Quarter'].astype(str)
    quarterly_users = user_df.groupby('Year_Quarter').agg({
        'Registered_users': 'sum',
        'App_opens': 'sum'
    }).reset_index()
    quarterly_users = quarterly_users.sort_values('Year_Quarter')
    
    print("\n📊 QUARTERLY USER GROWTH:")
    print("-" * 60)
    print(f"{'Quarter':<12} {'Registered Users':>20} {'App Opens':>20}")
    print("-" * 60)
    for _, row in quarterly_users.iterrows():
        print(f"{row['Year_Quarter']:<12} {row['Registered_users']:>20,.0f} {row['App_opens']:>20,.0f}")
    
    # User growth chart
    fig = px.line(
        quarterly_users,
        x='Year_Quarter',
        y='Registered_users',
        title='Quarter-wise Registered Users Growth',
        markers=True
    )
    fig.write_html(os.path.join(OUTPUT_DIR, "user_growth.html"))
    
    return quarterly_tx, quarterly_users

def analyze_state_quarter_growth(transaction_df):
    """Analyze state-wise quarterly growth"""
    print("\n" + "="*60)
    print("ANALYSIS 5: STATE-WISE QUARTERLY GROWTH")
    print("="*60)
    
    # Get top 5 states
    top_states = transaction_df.groupby('State')['Transaction_amount'].sum().nlargest(5).index
    
    # Quarterly data for top states
    state_quarter = transaction_df[transaction_df['State'].isin(top_states)].groupby(
        ['State', 'Year', 'Quarter']
    )['Transaction_amount'].sum().reset_index()
    
    state_quarter['Transaction_amount_in_crores'] = state_quarter['Transaction_amount'] / 10000000
    state_quarter['Year_Quarter'] = state_quarter['Year'].astype(str) + '-Q' + state_quarter['Quarter'].astype(str)
    
    # Line chart for top states
    fig = px.line(
        state_quarter,
        x='Year_Quarter',
        y='Transaction_amount_in_crores',
        color='State',
        title='Quarterly Growth - Top 5 States (₹ Crores)',
        markers=True
    )
    fig.write_html(os.path.join(OUTPUT_DIR, "state_quarter_growth.html"))
    
    return state_quarter

def analyze_transaction_correlation(transaction_df, user_df):
    """Analyze correlation between users and transactions"""
    print("\n" + "="*60)
    print("ANALYSIS 6: USERS vs TRANSACTIONS CORRELATION")
    print("="*60)
    
    # Aggregate by state
    tx_by_state = transaction_df.groupby('State').agg({
        'Transaction_count': 'sum',
        'Transaction_amount': 'sum'
    }).reset_index()
    
    # Get latest user count by state
    latest_users = user_df.sort_values(['Year', 'Quarter']).groupby('State').last().reset_index()
    
    # Merge
    merged = pd.merge(tx_by_state, latest_users[['State', 'Registered_users']], on='State')
    merged['Transaction_amount_in_crores'] = merged['Transaction_amount'] / 10000000
    
    # Correlation
    correlation = merged['Registered_users'].corr(merged['Transaction_amount'])
    
    print(f"\n📊 Correlation between Registered Users and Transaction Amount: {correlation:.4f}")
    
    # Scatter plot
    fig = px.scatter(
        merged,
        x='Registered_users',
        y='Transaction_amount_in_crores',
        size='Transaction_count',
        color='State',
        title=f'Users vs Transactions by State (Correlation: {correlation:.2f})',
        hover_name='State'
    )
    fig.write_html(os.path.join(OUTPUT_DIR, "users_vs_transactions.html"))
    
    return merged, correlation

def generate_summary_report(transaction_df, user_df):
    """Generate summary statistics report"""
    print("\n" + "="*60)
    print("EXECUTIVE SUMMARY REPORT")
    print("="*60)
    
    # Total transactions
    total_tx = transaction_df['Transaction_count'].sum()
    total_amount = transaction_df['Transaction_amount'].sum()
    total_amount_crores = total_amount / 10000000
    
    # Total users
    latest_users = user_df.sort_values(['Year', 'Quarter']).groupby('State').last().reset_index()
    total_users = latest_users['Registered_users'].sum()
    
    # Years covered
    years = sorted(transaction_df['Year'].unique())
    quarters = sorted(transaction_df['Quarter'].unique())
    
    print(f"""
📈 PHONEPE ANALYTICS - KEY METRICS
{'='*50}

📊 TRANSACTION METRICS:
   • Total Transactions: {total_tx:,.0f}
   • Total Transaction Value: ₹{total_amount_crores:,.2f} Crores
   • Average Transaction Value: ₹{total_amount/total_tx:,.2f}

👥 USER METRICS:
   • Total Registered Users: {total_users:,.0f}
   • Total States/UTs Covered: {len(latest_users)}

📅 DATA COVERAGE:
   • Years: {', '.join(years)}
   • Quarters: Q1, Q2, Q3, Q4

🏆 TOP 5 STATES BY TRANSACTION:
""")
    
    top5 = transaction_df.groupby('State')['Transaction_amount'].sum().nlargest(5)
    for idx, (state, amount) in enumerate(top5.items(), 1):
        print(f"   {idx}. {state}: ₹{amount/10000000:,.2f} Crores")
    
    print(f"""
📊 TOP TRANSACTION TYPES:
""")
    
    top_types = transaction_df.groupby('Transaction_type')['Transaction_amount'].sum().nlargest(5)
    for idx, (tx_type, amount) in enumerate(top_types.items(), 1):
        print(f"   {idx}. {tx_type}: ₹{amount/10000000:,.2f} Crores")
    
    # Save summary to file
    summary_file = os.path.join(OUTPUT_DIR, "executive_summary.txt")
    with open(summary_file, 'w') as f:
        f.write("PHONEPE DATA ANALYTICS - EXECUTIVE SUMMARY\n")
        f.write("="*60 + "\n\n")
        f.write(f"Total Transactions: {total_tx:,.0f}\n")
        f.write(f"Total Transaction Value: ₹{total_amount_crores:,.2f} Crores\n")
        f.write(f"Total Registered Users: {total_users:,.0f}\n")
        f.write(f"States/UTs Covered: {len(latest_users)}\n")
        f.write(f"Years Covered: {', '.join(years)}\n")
    
    print(f"\n✅ Reports saved to: {OUTPUT_DIR}")

def main():
    """Main execution function"""
    print("\n" + "="*60)
    print("   PHONEPE DATA ANALYTICS PROJECT")
    print("   Analyzing Digital Payment Trends in India")
    print("="*60 + "\n")
    
    # Load data
    transaction_df = load_transaction_data()
    user_df = load_user_data()
    
    # Run analyses
    analyze_state_wise_users(user_df)
    analyze_transaction_types(transaction_df)
    analyze_top_states(transaction_df)
    analyze_quarterly_growth(transaction_df, user_df)
    analyze_state_quarter_growth(transaction_df)
    analyze_transaction_correlation(transaction_df, user_df)
    generate_summary_report(transaction_df, user_df)
    
    print("\n" + "="*60)
    print("   ANALYSIS COMPLETE!")
    print("="*60)
    print(f"\n📁 Output files saved to: {OUTPUT_DIR}")
    print("   - state_wise_users.html")
    print("   - transaction_types_pie.html")
    print("   - transaction_types_bar.html")
    print("   - top_states.html")
    print("   - india_map.html")
    print("   - quarterly_growth.html")
    print("   - user_growth.html")
    print("   - state_quarter_growth.html")
    print("   - users_vs_transactions.html")
    print("   - executive_summary.txt")

if __name__ == "__main__":
    main()

