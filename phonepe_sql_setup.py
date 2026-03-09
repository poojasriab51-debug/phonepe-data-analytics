#!/usr/bin/env python3
"""
PhonePe Data Analytics - SQL Database Setup
Creates SQLite database with PhonePe transaction and user data
and performs business analysis queries.
"""

import sqlite3
import os
import json

DB_PATH = os.path.join(os.path.dirname(__file__), "phonepe_analysis.db")
PULSE_PATH = os.path.join(os.path.dirname(__file__), "pulse", "data")

def create_database():
    """Create SQLite database and tables"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            State TEXT,
            Year INTEGER,
            Quarter INTEGER,
            Transaction_type TEXT,
            Transaction_count INTEGER,
            Transaction_amount REAL
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            State TEXT,
            Year INTEGER,
            Quarter INTEGER,
            Registered_users INTEGER,
            App_opens INTEGER
        )
    """)
    
    conn.commit()
    return conn

def load_transaction_data(conn):
    """Load transaction data into database"""
    print("Loading transaction data into SQL...")
    cursor = conn.cursor()
    path = os.path.join(PULSE_PATH, "aggregated", "transaction", "country", "india", "state")
    
    if not os.path.exists(path):
        print(f"Path not found: {path}")
        return
    
    states = os.listdir(path)
    count = 0
    
    for state in states:
        state_path = os.path.join(path, state)
        if not os.path.isdir(state_path):
            continue
        years = os.listdir(state_path)
        for year in years:
            year_path = os.path.join(state_path, year)
            if not os.path.isdir(year_path):
                continue
            quarters = os.listdir(year_path)
            for quarter in quarters:
                try:
                    quarter_file = os.path.join(year_path, quarter)
                    with open(quarter_file, 'r') as f:
                        data = json.load(f)
                        for tx in data['data']['transactionData']:
                            name = tx['name']
                            count_val = tx['paymentInstruments'][0]['count']
                            amount = tx['paymentInstruments'][0]['amount']
                            cursor.execute("""
                                INSERT INTO transactions (State, Year, Quarter, Transaction_type, Transaction_count, Transaction_amount)
                                VALUES (?, ?, ?, ?, ?, ?)
                            """, (state, int(year), int(quarter.strip('.json')), name, count_val, amount))
                            count += 1
                except Exception as e:
                    continue
    
    conn.commit()
    print(f"  Loaded {count:,} transaction records")

def load_user_data(conn):
    """Load user data into database"""
    print("Loading user data into SQL...")
    cursor = conn.cursor()
    path = os.path.join(PULSE_PATH, "aggregated", "user", "country", "india", "state")
    
    if not os.path.exists(path):
        print(f"Path not found: {path}")
        return
    
    states = os.listdir(path)
    count = 0
    
    for state in states:
        state_path = os.path.join(path, state)
        if not os.path.isdir(state_path):
            continue
        years = os.listdir(state_path)
        for year in years:
            year_path = os.path.join(state_path, year)
            if not os.path.isdir(year_path):
                continue
            quarters = os.listdir(year_path)
            for quarter in quarters:
                try:
                    quarter_file = os.path.join(year_path, quarter)
                    with open(quarter_file, 'r') as f:
                        data = json.load(f)
                        users = data['data']['aggregated']['registeredUsers']
                        app_opens = data['data']['aggregated']['appOpens']
                        cursor.execute("""
                            INSERT INTO users (State, Year, Quarter, Registered_users, App_opens)
                            VALUES (?, ?, ?, ?, ?)
                        """, (state, int(year), int(quarter.strip('.json')), users, app_opens))
                        count += 1
                except Exception as e:
                    continue
    
    conn.commit()
    print(f"  Loaded {count:,} user records")

def business_analysis_queries(conn):
    """Execute business analysis SQL queries"""
    print("\n" + "="*70)
    print("BUSINESS ANALYSIS SQL QUERIES")
    print("="*70)
    
    cursor = conn.cursor()
    
    # Query 1
    print("\n QUERY 1: Total Transaction Value by State (All Time)")
    print("-" * 70)
    cursor.execute("""
        SELECT State, SUM(Transaction_count) as Total_Transactions,
               ROUND(SUM(Transaction_amount)/10000000, 2) as Amount_Crores
        FROM transactions GROUP BY State ORDER BY Amount_Crores DESC LIMIT 10
    """)
    results = cursor.fetchall()
    print(f"{'State':<35} {'Total Transactions':>20} {'Amount (₹Cr)':>15}")
    print("-" * 70)
    for row in results:
        print(f"{row[0]:<35} {row[1]:>20,} {row[2]:>15,}")
    
    # Query 2
    print("\n QUERY 2: Transaction Breakdown by Type")
    print("-" * 70)
    cursor.execute("""
        SELECT Transaction_type, SUM(Transaction_count) as Total_Count,
               ROUND(SUM(Transaction_amount)/10000000, 2) as Amount_Crores
        FROM transactions GROUP BY Transaction_type ORDER BY Amount_Crores DESC
    """)
    results = cursor.fetchall()
    for row in results:
        print(f"{row[0]:<30} Count: {row[1]:>15,}  Amount: ₹{row[2]:>12,} Cr")
    
    # Query 3
    print("\n QUERY 3: Quarter-over-Quarter Growth Analysis")
    cursor.execute("""
        SELECT Year || '-Q' || Quarter as Quarter,
               ROUND(SUM(Transaction_amount)/10000000, 2) as Amount_Crores
        FROM transactions GROUP BY Year, Quarter ORDER BY Year, Quarter
    """)
    results = cursor.fetchall()
    print(f"{'Quarter':<12} {'Amount (₹Crores)':>18}")
    for row in results:
        print(f"{row[0]:<12} {row[1]:>18,}")
    
    # Query 4 - Fixed
    print("\n QUERY 4: Top States by Registered Users")
    cursor.execute("""
        SELECT u.State, u.Year, u.Quarter, u.Registered_users, u.App_opens
        FROM users u
        INNER JOIN (SELECT State, MAX(Year * 4 + Quarter) as max_period FROM users GROUP BY State) m
        ON u.State = m.State AND (u.Year * 4 + u.Quarter) = m.max_period
        ORDER BY u.Registered_users DESC LIMIT 10
    """)
    results = cursor.fetchall()
    print(f"{'State':<30} {'Users':>15} {'App Opens':>18}")
    for row in results:
        print(f"{row[0]:<30} {row[3]:>15,} {row[4]:>18,}")
    
    # Query 5
    print("\n QUERY 5: Year-over-Year Growth")
    cursor.execute("""
        SELECT Year, ROUND(SUM(Transaction_amount)/10000000, 2) as Amount_Crores
        FROM transactions GROUP BY Year ORDER BY Year
    """)
    results = cursor.fetchall()
    print(f"{'Year':<8} {'Amount (₹Crores)':>20}")
    for row in results:
        print(f"{row[0]:<8} {row[1]:>20,}")
    
    return conn

def export_sql_queries():
    """Export SQL queries to file"""
    sql_content = """-- PhonePe Business Analysis SQL Queries

-- Query 1: Total Transaction Value by State
SELECT State, SUM(Transaction_count) as Total_Transactions,
       ROUND(SUM(Transaction_amount)/10000000, 2) as Amount_Crores
FROM transactions GROUP BY State ORDER BY Amount_Crores DESC LIMIT 10;

-- Query 2: Transaction Breakdown by Type
SELECT Transaction_type, SUM(Transaction_count) as Total_Count,
       ROUND(SUM(Transaction_amount)/10000000, 2) as Amount_Crores
FROM transactions GROUP BY Transaction_type ORDER BY Amount_Crores DESC;

-- Query 3: Quarterly Growth
SELECT Year || '-Q' || Quarter as Quarter,
       ROUND(SUM(Transaction_amount)/10000000, 2) as Amount_Crores
FROM transactions GROUP BY Year, Quarter ORDER BY Year, Quarter;

-- Query 4: Top States by Users
SELECT u.State, u.Registered_users, u.App_opens
FROM users u
INNER JOIN (SELECT State, MAX(Year * 4 + Quarter) as max_period FROM users GROUP BY State) m
ON u.State = m.State AND (u.Year * 4 + u.Quarter) = m.max_period
ORDER BY u.Registered_users DESC LIMIT 10;

-- Query 5: Year-over-Year Growth
SELECT Year, ROUND(SUM(Transaction_amount)/10000000, 2) as Amount_Crores
FROM transactions GROUP BY Year ORDER BY Year;

-- Query 6: User Engagement
SELECT su.State, su.Registered_users, st.Total_Tx,
       ROUND(1.0 * st.Total_Tx / su.Registered_users, 2) as Tx_Per_User
FROM (SELECT State, MAX(Registered_users) as Registered_users FROM users GROUP BY State) su
JOIN (SELECT State, SUM(Transaction_count) as Total_Tx FROM transactions GROUP BY State) st
ON su.State = st.State ORDER BY Tx_Per_User DESC LIMIT 10;

-- Query 7: Top Transaction Type per State
SELECT t.State, t.Transaction_type, ROUND(SUM(t.Transaction_amount)/10000000, 2) as Amount
FROM transactions t
JOIN (SELECT State, MAX(SUM(Transaction_amount)) as max_amt FROM transactions GROUP BY State) m
ON t.State = m.State GROUP BY t.State, t.Transaction_type
HAVING SUM(t.Transaction_amount) = m.max_amt ORDER BY Amount DESC;
"""
    with open("business_queries.sql", 'w') as f:
        f.write(sql_content)
    print("\n SQL queries saved to: business_queries.sql")

def main():
    print("\n" + "="*70)
    print("PHONEPE SQL DATABASE SETUP & BUSINESS ANALYSIS")
    print("="*70)
    
    conn = create_database()
    load_transaction_data(conn)
    load_user_data(conn)
    business_analysis_queries(conn)
    export_sql_queries()
    conn.close()
    
    print("\n" + "="*70)
    print("SQL DATABASE SETUP COMPLETE!")
    print(f"Database: {DB_PATH}")
    print("="*70)

if __name__ == "__main__":
    main()

