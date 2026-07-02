import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Meal Planner", layout="wide")
st.title("🍽️ Meal Planner")

if 'selected' not in st.session_state:
    st.session_state.selected = []

st.header("Search Recipes")
query = st.text_input("What do you want to eat? (chicken, burger, breakfast, pasta, etc.)", "")

if st.button("Search"):
    url = f"https://www.themealdb.com/api/json/v1/1/search.php?s={query}"
    data = requests.get(url).json()
    meals = data.get("meals", [])[:10]
    if meals:
        st.session_state.results = meals
        st.success(f"Found {len(meals)} recipes!")
    else:
        st.warning("Try 'chicken', 'beef', 'burger', 'breakfast', 'pasta'")

if 'results' in st.session_state:
    st.subheader("Select Recipes")
    for meal in st.session_state.results:
        col1, col2 = st.columns([1,4])
        with col1:
            if meal.get("strMealThumb"):
                st.image(meal["strMealThumb"], width=100)
        with col2:
            if st.checkbox(meal["strMeal"], key=meal["idMeal"]):
                if meal["idMeal"] not in [r.get("id") for r in st.session_state.selected]:
                    detail = requests.get(f"https://www.themealdb.com/api/json/v1/1/lookup.php?i={meal['idMeal']}").json()["meals"][0]
                    ingredients = []
                    for i in range(1, 21):
                        ing = detail.get(f"strIngredient{i}")
                        meas = detail.get(f"strMeasure{i}")
                        if ing and ing.strip():
                            ingredients.append(f"{meas or ''} {ing}")
                    st.session_state.selected.append({
                        "id": meal["idMeal"],
                        "title": meal["strMeal"],
                        "ingredients": ingredients,
                        "instructions": detail.get("strInstructions", "No instructions available."),
                        "image": meal.get("strMealThumb")
                    })

if st.session_state.selected:
    st.header("Your Recipes")
    for rec in st.session_state.selected:
        with st.expander(rec["title"], expanded=True):
            if rec.get("image"):
                st.image(rec["image"], width=300)
            st.subheader("Ingredients")
            for ing in rec["ingredients"]:
                st.write(f"• {ing}")
            st.subheader("Instructions")
            st.write(rec["instructions"])

    if st.button("Clear All Recipes"):
        st.session_state.selected = []
        st.rerun()

st.caption("Focus on recipes")