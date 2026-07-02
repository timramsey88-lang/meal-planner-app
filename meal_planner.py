import streamlit as st
import pandas as pd
import requests
from PIL import Image

st.set_page_config(page_title="Meal Planner + Walmart", layout="wide")
st.title("🍽️ Smart Meal Planner with Real Recipes + Walmart")

# ================== CONFIG ==================
API_KEY = st.secrets.get("SPOONACULAR_API_KEY", "YOUR_API_KEY_HERE")

if API_KEY == "YOUR_API_KEY_HERE":
    st.warning("Please add your Spoonacular API Key in Settings → Secrets")
    API_KEY = st.text_input("Spoonacular API Key", type="password")

# ================== SESSION STATE ==================
if 'selected_recipes' not in st.session_state:
    st.session_state.selected_recipes = []

# ================== UI ==================
st.header("🔍 Search Real Recipes")

col1, col2 = st.columns([3, 1])
with col1:
    query = st.text_input("What do you want to cook?", "chicken breast tacos")
with col2:
    number = st.slider("Recipes to show", 3, 10, 6)

price_mode = st.radio(
    "Shopping preference",
    ["Cheapest (generic/store brand)", "Name Brand"],
    horizontal=True
)

if st.button("Search Recipes"):
    if API_KEY and API_KEY != "YOUR_API_KEY_HERE":
        url = "https://api.spoonacular.com/recipes/complexSearch"
        params = {
            "apiKey": API_KEY,
            "query": query,
            "number": number,
            "addRecipeInformation": True
        }
        resp = requests.get(url, params=params)
        if resp.status_code == 200:
            st.session_state.recipes = resp.json().get("results", [])
            st.success(f"Found {len(st.session_state.recipes)} recipes!")
        else:
            st.error("Error fetching recipes. Check your API key.")
    else:
        st.error("Please enter a valid Spoonacular API Key")

# ================== DISPLAY RECIPES ==================
if 'recipes' in st.session_state and st.session_state.recipes:
    st.subheader("Select Recipes (click to add with quantities)")

    for recipe in st.session_state.recipes:
        col_img, col_info = st.columns([1, 4])
        with col_img:
            if recipe.get("image"):
                st.image(recipe["image"], width=90)

        with col_info:
            if st.checkbox(recipe["title"], key=recipe["id"]):
                # Fetch full recipe details with quantities
                info_url = f"https://api.spoonacular.com/recipes/{recipe['id']}/information"
                info_resp = requests.get(info_url, params={"apiKey": API_KEY})
                
                if info_resp.status_code == 200:
                    info = info_resp.json()
                    ingredients = []
                    for ing in info.get("extendedIngredients", []):
                        amount = ing.get("amount", 0)
                        unit = ing.get("unit", "")
                        name = ing.get("name", "")
                        ingredients.append({
                            "amount": amount,
                            "unit": unit,
                            "name": name,
                            "original": ing.get("original", f"{amount} {unit} {name}")
                        })
                    
                    st.session_state.selected_recipes.append({
                        "title": recipe["title"],
                        "ingredients": ingredients,
                        "price_mode": price_mode
                    })
                    st.success(f"Added: {recipe['title']}")

# ================== SHOPPING LIST ==================
if st.session_state.selected_recipes:
    st.header("🛒 Your Shopping List (with quantities)")

    # Combine ingredients
    combined = {}
    for rec in st.session_state.selected_recipes:
        for ing in rec["ingredients"]:
            key = ing["name"].lower()
            if key not in combined:
                combined[key] = {"amount": 0, "unit": ing["unit"], "originals": []}
            combined[key]["amount"] += ing["amount"]
            combined[key]["originals"].append(ing["original"])

    # Display list
    shopping_data = []
    for name, data in combined.items():
        shopping_data.append({
            "Item": name.title(),
            "Quantity": f"{round(data['amount'], 1)} {data['unit']}",
            "Details": ", ".join(data["originals"][:2])  # show first couple originals
        })

    df = pd.DataFrame(shopping_data)
    st.dataframe(df, use_container_width=True)

    # Walmart button with preference
    if st.button("🛍️ Search Walmart"):
        query_items = "+".join(combined.keys())
        if "Cheapest" in price_mode:
            query_items += "+generic+store+brand"
        else:
            query_items += "+name+brand"
        
        walmart_url = f"https://www.walmart.com/search?q={query_items}"
        st.markdown(f"[➡️ Open Walmart Search ({price_mode})]({walmart_url})")

    if st.button("Clear All Recipes"):
        st.session_state.selected_recipes = []
        st.rerun()

st.caption("Powered by Spoonacular • Your recipes, your quantities, your budget preference")