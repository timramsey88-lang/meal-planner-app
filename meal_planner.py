import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Meal Planner", layout="wide")
st.title("🍽️ Simple Meal Planner with Pictures + Walmart")

if 'selected_recipes' not in st.session_state:
    st.session_state.selected_recipes = {}

st.header("🔍 Search Recipes")
query = st.text_input("Search (chicken, beef, breakfast, pasta, etc.)", "")

if st.button("Search") and query:
    url = f"https://www.themealdb.com/api/json/v1/1/search.php?s={query}"
    data = requests.get(url).json()
    meals = data.get("meals", [])
    if meals:
        st.session_state.search_results = meals[:8]
        st.success(f"Found {len(meals)} recipes!")
    else:
        st.error("No recipes found. Try 'chicken', 'beef', 'breakfast', or 'pasta'.")

if 'search_results' in st.session_state:
    st.subheader("Select Recipes")
    for meal in st.session_state.search_results:
        col1, col2 = st.columns