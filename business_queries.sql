-- PhonePe Business Analysis SQL Queries

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
