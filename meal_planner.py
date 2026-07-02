import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Meal Planner", layout="wide")
st.title("🍽️ Smart Meal Planner with Pictures & Walmart")

if 'selected_recipes' not in st.session_state:
    st.session_state.selected_recipes = {}

st.header("🔍 Broader Recipe Search")
query = st.text_input("Search (chicken, gluten free, dairy free, breakfast, vegetarian, etc.)", "")

# Quick broad categories
st.subheader("Or Quick Categories")
cols = st.columns(4)
with cols[0]:
    if st.button("Beef"):
        st.session_state.temp_query = "beef"
with cols[1]:
    if st.button("Chicken"):
        st.session_state.temp_query = "chicken"
with cols[2]:
    if st.button("Breakfast"):
        st.session_state.temp_query = "breakfast"
with cols[3]:
    if st.button("Vegetarian"):
        st.session_state.temp_query = "vegetarian"

if 'temp_query' in st.session_state:
    query = st.session_state.temp_query

num_recipes = st.slider("How many recipes to show?", 1, 12, 6)

if st.button("Search Recipes") and query:
    url = f"https://www.themealdb.com/api/json/v1/1/search.php?s={query}"
    data = requests.get(url).json()
    meals = data.get("meals", [])[:num_recipes]
    if not meals:
        # Fallback to broader filter
        url = f"https://www.themealdb.com/api/json/v1/1/filter.php?i={query}"
        data = requests.get(url).json()
        meals = data.get("meals", [])[:num_recipes]
    
    if meals:
        st.session_state.search_results = meals
        st.success(f"Found {len(meals)} recipes!")
    else:
        st.warning("No recipes found. Try 'beef', 'chicken', 'breakfast', 'vegetarian', or 'pasta'.")

price_mode = st.radio("Shopping preference", ["Cheapest (generic)", "Name Brand"], horizontal=True)

# The rest of your code for selecting recipes, shopping list, etc. (keep it the same as your current version)

st.caption("Broader search using TheMealDB")