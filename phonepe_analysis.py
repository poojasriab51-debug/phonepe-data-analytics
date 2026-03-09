# PhonePe Transaction Data Analysis
# Modified to run locally (not in Colab)

# First, run this in your terminal to clone the data:
# git clone https://github.com/PhonePe/pulse.git

import os
import pandas as pd
import json
import plotly.express as px

# Update this path to where you cloned the pulse repository
# If you cloned it in the same directory as this script, use:
pulse_path = os.path.join(os.path.dirname(__file__), "pulse", "data", "aggregated", "transaction", "country", "india", "state")

# Alternative: specify absolute path
# pulse_path = "/Users/poojasriab/Downloads/Phonepe-data analytics project/pulse/data/aggregated/transaction/country/india/state"

path = pulse_path
Agg_state_list = os.listdir(path)
print("States found:", Agg_state_list)

# This is to extract the data to create a dataframe
clm = {'State': [], 'Year': [], 'Quater': [], 'Transacion_type': [], 'Transacion_count': [], 'Transacion_amount': []}

for i in Agg_state_list:
    p_i = path + "/" + i + "/"
    Agg_yr = os.listdir(p_i)
    for j in Agg_yr:
        p_j = p_i + j + "/"
        Agg_yr_list = os.listdir(p_j)
        for k in Agg_yr_list:
            p_k = p_j + k
            with open(p_k, 'r') as Data:
                D = json.load(Data)
                for z in D['data']['transactionData']:
                    Name = z['name']
                    count = z['paymentInstruments'][0]['count']
                    amount = z['paymentInstruments'][0]['amount']
                    clm['Transacion_type'].append(Name)
                    clm['Transacion_count'].append(count)
                    clm['Transacion_amount'].append(amount)
                    clm['State'].append(i)
                    clm['Year'].append(j)
                    clm['Quater'].append(int(k.strip('.json')))

# Successfully created a dataframe
Agg_Trans = pd.DataFrame(clm)
print("Dataframe created successfully!")
print(Agg_Trans.head())

# Visualizations
fig = px.bar(
    Agg_Trans,
    x="Transacion_type",
    y="Transacion_amount",
    color="Transacion_type",
    title="Transaction Amount by Type"
)
fig.show()

year_data = Agg_Trans.groupby("Year")["Transacion_amount"].sum().reset_index()

fig = px.line(
    year_data,
    x="Year",
    y="Transacion_amount",
    title="Total Transaction Growth Over Years"
)
fig.show()

state_data = Agg_Trans.groupby("State")["Transacion_amount"].sum().reset_index()

fig = px.bar(
    state_data,
    x="State",
    y="Transacion_amount",
    title="State Wise Transaction Amount"
)
fig.show()

top_states = Agg_Trans.groupby("State")["Transacion_amount"].sum().reset_index()
top_states = top_states.sort_values(by="Transacion_amount", ascending=False).head(10)

fig = px.bar(
    top_states,
    x="State",
    y="Transacion_amount",
    title="Top 10 States by Transaction Amount"
)
fig.show()

print("Number of unique states:", len(Agg_Trans['State'].unique()))

state_trans = Agg_Trans.groupby("State")["Transacion_amount"].sum().reset_index()
state_trans["State"] = state_trans["State"].str.replace("-", " ")
state_trans["State"] = state_trans["State"].str.title()

fig = px.choropleth(
    state_trans,
    geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
    featureidkey="properties.ST_NM",
    locations="State",
    color="Transacion_amount",
    color_continuous_scale="greens",
    title="PhonePe Transaction Amount by State"
)

fig.update_geos(fitbounds="locations", visible=False)
fig.show()

# Save to CSV
Agg_Trans.to_csv("phonepe_transactions.csv", index=False)
print("Data saved to phonepe_transactions.csv")

