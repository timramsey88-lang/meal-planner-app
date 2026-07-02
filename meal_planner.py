import streamlit as st
import pandas as pd
import requests
from PIL import Image

st.set_page_config(page_title="Meal Planner + Walmart", layout="wide")
st.title("🍽️ Smart Meal Planner with Recipes & Instructions")

API_KEY = st.secrets.get("SPOONACULAR_API_KEY", "YOUR_API_KEY_HERE")

if API_KEY == "YOUR_API_KEY_HERE":
    st.warning("Add your Spoonacular API Key in Settings → Secrets")
    API_KEY = st.text_input("Spoonacular API Key", type="password")

if 'selected_recipes' not in st.session_state:
    st.session_state.selected_recipes = []

st.header("🔍 Search Recipes")

query = st.text_input("Search for recipes", "chicken breast")
number = st.slider("Number of results", 3, 10, 6)

price_mode = st.radio("Shopping preference", ["Cheapest", "Name Brand"], horizontal=True)

if st.button("Search Recipes"):
    if API_KEY and API_KEY != "YOUR_API_KEY_HERE":
        url = "https://api.spoonacular.com/recipes/complexSearch"
        params = {"apiKey": API_KEY, "query": query, "number": number, "addRecipeInformation": True}
        resp = requests.get(url, params=params)
        if resp.status_code == 200:
            st.session_state.recipes = resp.json().get("results", [])
        else:
            st.error("API error - check key")
    else:
        st.error("Please add API key")

if 'recipes' in st.session_state:
    st.subheader("Select Recipes")
    for recipe in st.session_state.recipes:
        col1, col2 = st.columns([1,4])
        with col1:
            if recipe.get("image"):
                st.image(recipe["image"], width=100)
        with col2:
            if st.checkbox(recipe["title"], key=recipe["id"]):
                # Get full details
                info_url = f"https://api.spoonacular.com/recipes/{recipe['id']}/information"
                info = requests.get(info_url, params={"apiKey": API_KEY}).json()
                
                ingredients = []
                for ing in info.get("extendedIngredients", []):
                    ingredients.append({
                        "amount": ing.get("amount", 0),
                        "unit": ing.get("unit", ""),
                        "name": ing.get("name", "")
                    })
                
                st.session_state.selected_recipes.append({
                    "title": recipe["title"],
                    "ingredients": ingredients,
                    "instructions": info.get("instructions", "No instructions available."),
                    "sourceUrl": recipe.get("sourceUrl", "#")
                })
                st.success(f"Added {recipe['title']}")

# Show selected recipes with instructions
if st.session_state.selected_recipes:
    st.header("📋 Selected Recipes & Instructions")
    
    for i, rec in enumerate(st.session_state.selected_recipes):
        with st.expander(f"🍲 {rec['title']}", expanded=True):
            st.markdown(f"**Source:** [View Original Recipe]({rec.get('sourceUrl', '#')})")
            
            st.subheader("Ingredients")
            for ing in rec["ingredients"]:
                st.write(f"• {ing['amount']} {ing['unit']} {ing['name']}")
            
            st.subheader("Instructions")
            st.markdown(rec["instructions"])
    
    # Shopping list
    st.header("🛒 Shopping List")
    shopping = {}
    for rec in st.session_state.selected_recipes:
        for ing in rec["ingredients"]:
            key = ing["name"].lower()
            shopping[key] = shopping.get(key, 0) + ing["amount"]
    
    df = pd.DataFrame([{"Item": k.title(), "Approx Quantity": v} for k,v in shopping.items()])
    st.dataframe(df, use_container_width=True)

    if st.button("🛍️ Search Walmart"):
        items = "+".join(shopping.keys())
        mode = "generic" if price_mode == "Cheapest" else "brand"
        url = f"https://www.walmart.com/search?q={items}+{mode}"
        st.markdown(f"[Open Walmart →]({url})")

    if st.button("Clear Everything"):
        st.session_state.selected_recipes = []
        st.rerun()

st.caption("Recipe data from Spoonacular • Your app, your rules")