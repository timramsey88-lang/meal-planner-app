import streamlit as st
import pandas as pd
import requests
from PIL import Image

st.set_page_config(page_title="Meal Planner + Walmart", layout="wide")
st.title("🍽️ Smart Meal Planner with Real Recipes + Walmart")

# ================== CONFIG ==================
API_KEY = st.secrets.get("SPOONACULAR_API_KEY") or "YOUR_API_KEY_HERE"  # Replace with your key for testing

if API_KEY == "YOUR_API_KEY_HERE":
    st.warning("⚠️ Please add your Spoonacular API key below")
    API_KEY = st.text_input("Paste your Spoonacular API Key", type="password")

# ===========================================

if 'selected_recipes' not in st.session_state:
    st.session_state.selected_recipes = []

st.header("🔍 Search Real Recipes")

query = st.text_input("What do you want to cook? (e.g. chicken breast, tacos, pasta)", "chicken breast")
number = st.slider("How many recipes?", 3, 12, 6)

if st.button("Search Recipes"):
    if API_KEY and API_KEY != "YOUR_API_KEY_HERE":
        url = f"https://api.spoonacular.com/recipes/complexSearch"
        params = {
            "apiKey": API_KEY,
            "query": query,
            "number": number,
            "addRecipeInformation": True
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            st.session_state.recipes = response.json()["results"]
            st.success(f"Found {len(st.session_state.recipes)} recipes!")
        else:
            st.error("API error. Check your key or try later.")
    else:
        st.error("Please enter a valid Spoonacular API Key")

# Display recipes
if 'recipes' in st.session_state:
    st.subheader("Choose Recipes")
    for recipe in st.session_state.recipes:
        col1, col2 = st.columns([1, 4])
        with col1:
            if recipe.get("image"):
                st.image(recipe["image"], width=100)
        with col2:
            if st.checkbox(recipe["title"], key=recipe["id"]):
                # Get full ingredients
                ing_url = f"https://api.spoonacular.com/recipes/{recipe['id']}/ingredientWidget.json"
                ing_resp = requests.get(ing_url, params={"apiKey": API_KEY})
                if ing_resp.status_code == 200:
                    ingredients = [item["name"] for item in ing_resp.json()["ingredients"]]
                    st.session_state.selected_recipes.append({
                        "title": recipe["title"],
                        "ingredients": ingredients
                    })
                    st.success("Added to list!")

# Shopping List
if st.session_state.selected_recipes:
    st.header("🛒 Your Shopping List")
    shopping = {}
    for rec in st.session_state.selected_recipes:
        for ing in rec["ingredients"]:
            shopping[ing] = shopping.get(ing, 0) + 1
    
    df = pd.DataFrame(list(shopping.items()), columns=["Item", "Quantity"])
    st.dataframe(df, use_container_width=True)

    if st.button("🛍️ Search on Walmart"):
        query_str = "+".join(shopping.keys())
        st.markdown(f"[Open Walmart for these items →](https://www.walmart.com/search?q={query_str})")

    if st.button("Clear All"):
        st.session_state.selected_recipes = []
        st.rerun()

st.caption("Powered by Spoonacular + Grok")
