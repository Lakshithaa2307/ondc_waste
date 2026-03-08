import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from matching_engine import match_orders

st.set_page_config(layout="wide")
st.title("🌾 Smart AgriMatch – Real-Time Farm to Order Optimizer")

# Session state storage
if "farms" not in st.session_state:
    st.session_state.farms = pd.DataFrame(
        columns=["farm_id", "crop", "quantity", "latitude", "longitude"]
    )

if "orders" not in st.session_state:
    st.session_state.orders = pd.DataFrame(
        columns=["order_id", "crop", "latitude", "longitude"]
    )

# Sidebar - Add Farm
st.sidebar.header("Add Farming Area")

farm_id = st.sidebar.text_input("Farm ID")
crop = st.sidebar.selectbox("Crop Type", ["Tomato", "Potato", "Onion"])
quantity = st.sidebar.number_input("Available Quantity", min_value=1)
farm_lat = st.sidebar.number_input("Farm Latitude", value=12.97)
farm_lon = st.sidebar.number_input("Farm Longitude", value=77.59)

if st.sidebar.button("Register Farm"):
    new_farm = pd.DataFrame([{
        "farm_id": farm_id,
        "crop": crop,
        "quantity": quantity,
        "latitude": farm_lat,
        "longitude": farm_lon
    }])
    st.session_state.farms = pd.concat(
        [st.session_state.farms, new_farm], ignore_index=True
    )

# Sidebar - Add Order
st.sidebar.header("Create Order")

order_id = st.sidebar.text_input("Order ID")
order_crop = st.sidebar.selectbox("Required Crop", ["Tomato", "Potato", "Onion"])
order_lat = st.sidebar.number_input("Order Latitude", value=12.96)
order_lon = st.sidebar.number_input("Order Longitude", value=77.60)

if st.sidebar.button("Place Order"):
    new_order = pd.DataFrame([{
        "order_id": order_id,
        "crop": order_crop,
        "latitude": order_lat,
        "longitude": order_lon
    }])
    st.session_state.orders = pd.concat(
        [st.session_state.orders, new_order], ignore_index=True
    )

# Matching logic
matches = match_orders(st.session_state.farms, st.session_state.orders)

# Live Map
st.subheader("📍 Live Smart Matching Map")

m = folium.Map(location=[12.97, 77.59], zoom_start=12)

# Farms (Green)
for _, farm in st.session_state.farms.iterrows():
    folium.Marker(
        [farm["latitude"], farm["longitude"]],
        popup=f"Farm: {farm['farm_id']} ({farm['crop']})",
        icon=folium.Icon(color="green")
    ).add_to(m)

# Orders (Red)
for _, order in st.session_state.orders.iterrows():
    folium.Marker(
        [order["latitude"], order["longitude"]],
        popup=f"Order: {order['order_id']} ({order['crop']})",
        icon=folium.Icon(color="red")
    ).add_to(m)

# Draw Matches
total_distance = 0

for _, match in matches.iterrows():
    total_distance += match["distance_km"]

    folium.PolyLine(
        [
            [match["farm_lat"], match["farm_lon"]],
            [match["order_lat"], match["order_lon"]],
        ],
        color="blue",
        weight=3
    ).add_to(m)

st_folium(m, width=1200, height=600)

# Metrics Section
st.subheader("📊 Smart Metrics")

col1, col2 = st.columns(2)

col1.metric("Total Matches", len(matches))
col2.metric("Total Distance (km)", round(total_distance, 2))
