import streamlit as st
import pandas as pd
from PIL import Image

st.set_page_config(page_title="Meal Planner & Walmart", layout="wide")
st.title("🍽️ Smart Meal Planner + Walmart Delivery")

# Recipes database
recipes_db = {
    "chicken": [
        {"name": "Chicken Stir Fry", "ingredients": ["chicken breast", "broccoli", "carrots", "soy sauce", "rice"], "servings": 4},
        {"name": "Grilled Chicken Salad", "ingredients": ["chicken breast", "mixed greens", "tomatoes", "cucumber", "olive oil"], "servings": 2},
        {"name": "Chicken Tacos", "ingredients": ["chicken breast", "taco shells", "lettuce", "cheese", "salsa"], "servings": 4},
    ],
    "beef": [
        {"name": "Beef Tacos", "ingredients": ["ground beef", "taco shells", "lettuce", "cheese", "salsa"], "servings": 4},
    ],
    "steak": [
        {"name": "Steak & Veggies", "ingredients": ["steak", "potatoes", "asparagus"], "servings": 2},
    ],
    "fish": [
        {"name": "Salmon Salad", "ingredients": ["salmon", "mixed greens", "avocado", "cucumber"], "servings": 2},
    ],
}

st.header("📸 Step 1: Main Ingredient")

col1, col2 = st.columns(2)
with col1:
    uploaded_file = st.file_uploader("Upload photo of main ingredient", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded", use_container_width=True)
    detected = st.selectbox("Main ingredient", ["chicken", "beef", "steak", "fish", "other"])

with col2:
    pantry_input = st.text_input("Or type what you have (comma separated)", "chicken breast, steak")
    pantry_items = [item.strip().lower() for item in pantry_input.split(",") if item.strip()]

if st.button("Get Recipe Suggestions"):
    suggestions = []
    for item in pantry_items:
        if item in recipes_db:
            suggestions.extend(recipes_db[item])
        else:
            suggestions.append({"name": f"Simple {item.title()} Meal", "ingredients": [item, "vegetables", "rice"], "servings": 4})
    
    st.subheader("Choose Recipes")
    selected = []
    for rec in suggestions[:6]:
        if st.checkbox(rec["name"]):
            selected.append(rec)
    if selected:
        st.session_state.selected = selected
        st.success("Recipes selected!")

if 'selected' in st.session_state and st.session_state.selected:
    st.header("🛒 Shopping List")
    shopping = {}
    for rec in st.session_state.selected:
        for ing in rec["ingredients"]:
            shopping[ing] = shopping.get(ing, 0) + 1
    st.dataframe(pd.DataFrame(list(shopping.items()), columns=["Item", "Qty"]))
    
    if st.button("🛍️ Search on Walmart"):
        query = "+".join(shopping.keys())
        url = f"https://www.walmart.com/search?q={query}"
        st.markdown(f"[➡️ Open Walmart for Delivery/Pickup]({url})")

st.caption("Your personal meal planner • Made with Grok")
