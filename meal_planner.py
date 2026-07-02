import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Meal Planner + Walmart", layout="wide")
st.title("🍽️ Smart Meal Planner with Recipes & Walmart")

if 'selected_recipes' not in st.session_state:
    st.session_state.selected_recipes = {}

st.header("🔍 Search Recipes")
query = st.text_input("What do you want to cook? (e.g. chicken, beef, pasta)", "chicken")

if st.button("Search Recipes"):
    url = f"https://www.themealdb.com/api/json/v1/1/search.php?s={query}"
    data = requests.get(url).json()
    meals = data.get("meals", [])
    if meals:
        st.session_state.search_results = meals
        st.success(f"Found {len(meals)} recipes!")
    else:
        st.warning("No recipes found. Try different keywords.")

price_mode = st.radio("Shopping preference", ["Cheapest (generic)", "Name Brand"], horizontal=True)

if 'search_results' in st.session_state:
    st.subheader("Select Recipes")
    for meal in st.session_state.search_results:
        meal_id = meal["idMeal"]
        checked = st.checkbox(meal["strMeal"], value=meal_id in st.session_state.selected_recipes, key=meal_id)
        
        if checked and meal_id not in st.session_state.selected_recipes:
            # Fetch full details
            detail_url = f"https://www.themealdb.com/api/json/v1/1/lookup.php?i={meal_id}"
            detail = requests.get(detail_url).json()["meals"][0]
            
            # Extract ingredients (TheMealDB format)
            ingredients = []
            for i in range(1, 21):
                ing = detail.get(f"strIngredient{i}")
                meas = detail.get(f"strMeasure{i}")
                if ing and ing.strip():
                    ingredients.append({"amount": meas or "1", "name": ing})
            
            st.session_state.selected_recipes[meal_id] = {
                "title": meal["strMeal"],
                "ingredients": ingredients,
                "instructions": detail.get("strInstructions", "Instructions not available."),
                "sourceUrl": detail.get("strSource") or "#"
            }
        elif not checked and meal_id in st.session_state.selected_recipes:
            del st.session_state.selected_recipes[meal_id]

# Selected recipes section
if st.session_state.selected_recipes:
    st.header("📋 Your Selected Recipes")
    for meal_id, rec in list(st.session_state.selected_recipes.items()):
        with st.expander(f"🍲 {rec['title']}", expanded=True):
            st.markdown(f"[View Original Recipe]({rec['sourceUrl']})")
            
            st.subheader("Ingredients")
            for ing in rec["ingredients"]:
                st.write(f"• {ing['amount']} {ing['name']}")
            
            st.subheader("Instructions")
            st.write(rec["instructions"])
    
    # Shopping List
    st.header("🛒 Shopping List")
    shopping = {}
    for rec in st.session_state.selected_recipes.values():
        for ing in rec["ingredients"]:
            name = ing["name"].lower()
            shopping[name] = shopping.get(name, 0) + 1  # simple count for now
    
    df = pd.DataFrame([{"Item": k.title(), "Quantity": v} for k,v in shopping.items()])
    st.dataframe(df, use_container_width=True)

    if st.button("🛍️ Search Walmart"):
        items = "+".join(shopping.keys())
        extra = "+generic" if "Cheapest" in price_mode else "+brand"
        url = f"https://www.walmart.com/search?q={items}{extra}"
        st.markdown(f"[➡️ Open Walmart ({price_mode}) →]({url})")

    if st.button("Clear All"):
        st.session_state.selected_recipes = {}
        st.rerun()

st.caption("Powered by TheMealDB • Unlimited free recipe search")