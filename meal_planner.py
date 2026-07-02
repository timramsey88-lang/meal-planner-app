import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Meal Planner", layout="wide")
st.title("🍽️ Smart Meal Planner with Pictures & Walmart")

if 'selected_recipes' not in st.session_state:
    st.session_state.selected_recipes = {}

st.header("🔍 Search Recipes")
query = st.text_input("Search anything (chicken, gluten free, dairy free, breakfast, etc.)", "")

if st.button("Search"):
    # Try TheMealDB first
    url = f"https://www.themealdb.com/api/json/v1/1/search.php?s={query}"
    data = requests.get(url).json()
    meals = data.get("meals", [])
    if meals:
        st.session_state.search_results = meals[:8]
        st.success("Found recipes from TheMealDB!")
    else:
        st.info("No exact matches. Try Google for more options.")
        google_url = f"https://www.google.com/search?q={query}+recipe+gluten+free+OR+dairy+free"
        st.markdown(f"[🔎 Open Google for more recipes]({google_url})")

# Rest of your code (select, shopping list, Walmart) stays the same...

st.caption("TheMealDB + Google fallback • No hard search limits")