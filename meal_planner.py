import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Meal Planner", layout="wide")
st.title("🍽️ Simple Meal Planner + Walmart")

if 'selected_recipes' not in st.session_state:
    st.session_state.selected_recipes = {}

st.header("🔍 Search Recipes")
query = st.text_input("Search (chicken, beef, breakfast, pasta, etc.)", "")

if st.button("Search") and query:
    url = f"https://www.themealdb.com/api/json/v1/1/search.php?s={query}"
    data = requests.get(url).json()
    meals = data.get("meals", [])
    if meals:
        st.session_state.search_results = meals[:8]
        st.success(f"Found {len(meals)} recipes!")
    else:
        st.error("No recipes found. Try 'chicken' or 'beef'.")

if 'search_results' in st.session_state:
    st.subheader("Select Recipes")
    for meal in st.session_state.search_results:
        if st.checkbox(meal["strMeal"], key=meal["idMeal"]):
            if meal["idMeal"] not in st.session_state.selected_recipes:
                detail = requests.get(f"https://www.themealdb.com/api/json/v1/1/lookup.php?i={meal['idMeal']}").json()["meals"][0]
                ingredients = []
                for i in range(1, 21):
                    ing = detail.get(f"strIngredient{i}")
                    meas = detail.get(f"strMeasure{i}")
                    if ing and ing.strip():
                        ingredients.append(f"{meas or ''} {ing}")
                st.session_state.selected_recipes[meal["idMeal"]] = {
                    "title": meal["strMeal"],
                    "ingredients": ingredients,
                    "instructions": detail.get("strInstructions", "No instructions."),
                    "image": meal.get("strMealThumb")
                }

if st.session_state.selected_recipes:
    st.header("Selected Recipes")
    for key, rec in list(st.session_state.selected_recipes.items()):
        with st.expander(rec["title"], expanded=True):
            if rec.get("image"):
                st.image(rec["image"], width=250)
            st.subheader("Ingredients")
            for ing in rec["ingredients"]:
                st.write(f"• {ing}")
            st.subheader("Instructions")
            st.write(rec["instructions"])

    st.header("🛒 Shopping List")
    shopping = {}
    for rec in st.session_state.selected_recipes.values():
        for ing in rec["ingredients"]:
            name = ing.split()[-1].lower() if ing else "item"
            shopping[name] = shopping.get(name, 0) + 1
    df = pd.DataFrame([{"Item": k.title(), "Quantity": v} for k,v in shopping.items()])
    st.dataframe(df, use_container_width=True)

    if st.button("🛍️ Search Walmart"):
        items = "+".join(shopping.keys())
        st.markdown(f"[Open Walmart](https://www.walmart.com/search?q={items})")

    if st.button("Clear All"):
        st.session_state.selected_recipes = {}
        st.rerun()

st.caption("Simple version • TheMealDB")