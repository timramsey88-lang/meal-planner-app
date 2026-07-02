import streamlit as st
import pandas as pd
from PIL import Image

st.set_page_config(page_title="Meal Planner", layout="wide")
st.title("🍽️ Smart Meal Planner + Walmart")

recipes_db = {
    "chicken": [{"name": "Chicken Stir Fry", "ingredients": ["chicken breast", "broccoli", "carrots", "soy sauce", "rice"]}],
    "beef": [{"name": "Beef Tacos", "ingredients": ["ground beef", "taco shells", "lettuce", "cheese"]}],
    "steak": [{"name": "Steak & Veggies", "ingredients": ["steak", "potatoes", "asparagus"]}],
    "fish": [{"name": "Salmon Salad", "ingredients": ["salmon", "greens", "avocado"]}],
}

if 'selected' not in st.session_state:
    st.session_state.selected = []

st.header("Step 1: Main Ingredient")
uploaded = st.file_uploader("Upload photo of main ingredient", type=["jpg","png"])
if uploaded:
    st.image(Image.open(uploaded), use_container_width=True)

main_ing = st.selectbox("Main ingredient", ["chicken", "beef", "steak", "fish"])
pantry = st.text_input("Or type what you have", "chicken breast, steak")

if st.button("Get Recipe Suggestions"):
    suggestions = recipes_db.get(main_ing, [{"name": "Simple Meal", "ingredients": [main_ing]}])
    st.session_state.suggestions = suggestions
    st.rerun()

if 'suggestions' in st.session_state:
    st.subheader("Choose Recipes")
    for rec in st.session_state.suggestions:
        if st.checkbox(rec["name"], key=rec["name"] + "_check"):
            if rec not in st.session_state.selected:
                st.session_state.selected.append(rec)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Clear All Selections"):
            st.session_state.selected = []
            st.rerun()
    with col2:
        if st.button("Refresh Suggestions"):
            st.rerun()

    if st.session_state.selected:
        st.success(f"Selected {len(st.session_state.selected)} recipes!")

        st.header("🛒 Shopping List")
        shopping = {}
        for rec in st.session_state.selected:
            for ing in rec["ingredients"]:
                shopping[ing] = shopping.get(ing, 0) + 1
        st.dataframe(pd.DataFrame(list(shopping.items()), columns=["Item", "Qty"]), use_container_width=True)

        if st.button("🛍️ Search on Walmart for Delivery"):
            query = "+".join(shopping.keys())
            st.markdown(f"[➡️ Open Walmart →](https://www.walmart.com/search?q={query})")

st.caption("Your personal meal planner • Made with Grok")
