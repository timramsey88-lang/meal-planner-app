import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Meal Planner", layout="wide")
st.title("🍽️ American-Style Meal Planner + Walmart")

if 'selected_recipes' not in st.session_state:
    st.session_state.selected_recipes = {}

st.header("🔍 Search Recipes (American Focus)")
query = st.text_input("Search (burger, steak, chicken, breakfast, tacos, mac and cheese, etc.)", "")

# Quick American-style buttons
st.subheader("Quick American Meals")
cols = st.columns(4)
with cols[0]:
    if st.button("Burgers"):
        st.session_state.temp_query = "burger"
with cols[1]:
    if st.button("Steak"):
        st.session_state.temp_query = "steak"
with cols[2]:
    if st.button("Chicken"):
        st.session_state.temp_query = "chicken"
with cols[3]:
    if st.button("Breakfast"):
        st.session_state.temp_query = "breakfast"

if 'temp_query' in st.session_state:
    query = st.session_state.temp_query

if st.button("Search Recipes") and query:
    url = f"https://www.themealdb.com/api/json/v1/1/search.php?s={query}"
    data = requests.get(url).json()
    meals = data.get("meals", [])
    if meals:
        st.session_state.search_results = meals[:10]
        st.success(f"Found {len(meals)} recipes!")
    else:
        st.warning("Try 'burger', 'steak', 'mac and cheese', 'pancakes', 'tacos', or 'fried chicken'.")

# Rest of your code for selecting, shopping list, Walmart (keep the same as your current version)

st.caption("Focused on American-style foods")