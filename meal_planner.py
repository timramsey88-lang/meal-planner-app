import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Meal Planner", layout="wide")
st.title("🍽️ Smart Meal Planner with Pictures & Walmart")

if 'selected_recipes' not in st.session_state:
    st.session_state.selected_recipes = {}

st.header("🔍 Search Recipes")
query = st.text_input("Search anything (chicken, breakfast, vegetarian, tacos, pasta, flank steak, etc.)", "")

num_recipes = st.slider("How many recipes to show?", 1, 12, 6)

if st.button("Search Recipes") and query.strip():
    url = f"https://www.themealdb.com/api/json/v1/1/search.php?s={query.strip()}"
    data = requests.get(url).json()
    meals = data.get("meals") or []
    meals = meals[:num_recipes]
    if meals:
        st.session_state.search_results = meals
        st.success(f"Found {len(meals)} recipes!")
    else:
        st.error(f"No recipes found for '{query}'. Try broader terms like 'beef', 'chicken', 'breakfast', 'pasta', or 'steak'.")

price_mode = st.radio("Shopping preference", ["Cheapest (generic)", "Name Brand"], horizontal=True)

if 'search_results' in st.session_state:
    st.subheader("Select Recipes")
    for meal in st.session_state.search_results:
        meal_id = meal["idMeal"]
        col1, col2 = st.columns([1, 4])
        with col1:
            if meal.get("strMealThumb"):
                st.image(meal["strMealThumb"], width=100)
        with col2:
            checked = st.checkbox(meal["strMeal"], value=meal_id in st.session_state.selected_recipes, key=meal_id)
            
            if checked and meal_id not in st.session_state.selected_recipes:
                detail_url = f"https://www.themealdb.com/api/json/v1/1/lookup.php?i={meal_id}"
                detail = requests.get(detail_url).json().get("meals", [{}])[0]
                ingredients = []
                for i in range(1, 21):
                    ing = detail.get(f"strIngredient{i}")
                    meas = detail.get(f"strMeasure{i}")
                    if ing and ing.strip():
                        ingredients.append({"amount": meas or "some", "name": ing})
                
                st.session_state.selected_recipes[meal_id] = {
                    "title": meal["strMeal"],
                    "ingredients": ingredients,
                    "instructions": detail.get("strInstructions", "No instructions available."),
                    "image": meal.get("strMealThumb"),
                    "sourceUrl": detail.get("strSource") or "#"
                }
            elif not checked and meal_id in st.session_state.selected_recipes:
                del st.session_state.selected_recipes[meal_id]

if st.session_state.selected_recipes:
    st.header("📋 Selected Recipes")
    for meal_id, rec in list(st.session_state.selected_recipes.items()):
        with st.expander(f"🍲 {rec['title']}", expanded=True):
            if rec.get("image"):
                st.image(rec["image"], width=300)
            st.markdown(f"[View Full Recipe]({rec['sourceUrl']})")
            
            st.subheader("Ingredients")
            for ing in rec["ingredients"]:
                st.write(f"• {ing['amount']} {ing['name']}")
            
            st.subheader("Instructions")
            st.write(rec["instructions"])

    st.header("🛒 Shopping List")
    shopping = {}
    for rec in st.session_state.selected_recipes.values():
        for ing in rec["ingredients"]:
            name = ing["name"].lower()
            shopping[name] = shopping.get(name, 0) + 1
    
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

st.caption("TheMealDB • Flexible search")