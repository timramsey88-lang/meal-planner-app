import streamlit as st
import pandas as pd
from PIL import Image
import random

st.set_page_config(page_title="Meal Planner", layout="wide")
st.title("🍽️ Smart Meal Planner + Walmart")

# Bigger recipe database
recipes_db = {
    "chicken": [
        {"name": "Chicken Stir Fry", "ingredients": ["chicken breast", "broccoli", "carrots", "soy sauce", "rice"]},
        {"name": "Grilled Chicken Salad", "ingredients": ["chicken breast", "mixed greens", "tomatoes", "cucumber", "olive oil"]},
        {"name": "Chicken Tacos", "ingredients": ["chicken breast", "taco shells", "lettuce", "cheese", "salsa"]},
        {"name": "Chicken Curry", "ingredients": ["chicken breast", "coconut milk", "rice", "spinach"]},
    ],
    "beef": [
        {"name": "Beef Tacos", "ingredients": ["ground beef", "taco shells", "lettuce", "cheese", "salsa"]},
        {"name": "Beef Stir Fry", "ingredients": ["steak", "broccoli", "carrots", "soy sauce"]},
        {"name": "Cheeseburger Bowl", "ingredients": ["ground beef", "cheese", "lettuce", "tomato"]},
    ],
    "steak": [
        {"name": "Steak & Veggies", "ingredients": ["steak", "potatoes", "asparagus", "butter"]},
        {"name": "Steak Salad", "ingredients": ["steak", "mixed greens", "avocado", "tomatoes"]},
    ],
    "fish": [
        {"name": "Salmon Salad", "ingredients": ["salmon", "mixed greens", "avocado", "cucumber"]},
        {"name": "Grilled Fish", "ingredients": ["fish fillet", "lemon", "asparagus", "rice"]},
        {"name": "Fish Tacos", "ingredients": ["fish fillet", "taco shells", "cabbage", "salsa"]},
    ],
}

if 'selected' not in st.session_state:
    st.session_state.selected = []

st.header("Step 1: Main Ingredient")
uploaded = st.file_uploader("Upload photo", type=["jpg","png"])
if uploaded:
    st.image(Image.open(uploaded), use_container_width=True)

main_ing = st.selectbox("Main ingredient", ["chicken", "beef", "steak", "fish"])
pantry = st.text_input("What you have (optional)", "chicken breast")

if st.button("Get Recipe Suggestions"):
    suggestions = recipes_db.get(main_ing, [{"name": "Simple Meal", "ingredients": [main_ing]}])
    # Shuffle for variety
    random.shuffle(suggestions)
    st.session_state.suggestions = suggestions[:4]  # Show up to 4
    st.rerun()

if 'suggestions' in st.session_state:
    st.subheader("Choose Recipes (tap again for new ideas)")
    for rec in st.session_state.suggestions:
        if st.checkbox(rec["name"], key=rec["name"]):
            if rec not in st.session_state.selected:
                st.session_state.selected.append(rec)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Clear All"):
            st.session_state.selected = []
            st.rerun()
    with col2:
        if st.button("New Suggestions"):
            st.rerun()
    with col3:
        if st.button("Refresh"):
            st.rerun()

    if st.session_state.selected:
        st.success(f"{len(st.session_state.selected)} recipes selected!")

        st.header("🛒 Shopping List")
        shopping = {}
        for rec in st.session_state.selected:
            for ing in rec["ingredients"]:
                shopping[ing] = shopping.get(ing, 0) + 1
        st.dataframe(pd.DataFrame(list(shopping.items()), columns=["Item", "Qty"]), use_container_width=True)

        if st.button("🛍️ Search Walmart"):
            query = "+".join(shopping.keys())
            st.markdown(f"[Open Walmart for Delivery](https://www.walmart.com/search?q={query})")

st.caption("Made with Grok • Refresh for new recipes")
