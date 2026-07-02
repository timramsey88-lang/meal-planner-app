import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Meal Planner", layout="wide")
st.title("🍽️ Smart Meal Planner with Recipes & Walmart")

API_KEY = st.secrets.get("SPOONACULAR_API_KEY", "YOUR_API_KEY_HERE")

if 'selected_recipes' not in st.session_state:
    st.session_state.selected_recipes = {}

st.header("🔍 Search Recipes")
query = st.text_input("What do you want to cook?", "chicken breast")
if st.button("Search"):
    if API_KEY != "YOUR_API_KEY_HERE":
        url = "https://api.spoonacular.com/recipes/complexSearch"
        params = {"apiKey": API_KEY, "query": query, "number": 8, "addRecipeInformation": True}
        data = requests.get(url, params=params).json()
        st.session_state.search_results = data.get("results", [])
    else:
        st.error("Add your Spoonacular API Key in Secrets")

price_mode = st.radio("Preference", ["Cheapest (generic)", "Name Brand"], horizontal=True)

if 'search_results' in st.session_state:
    st.subheader("Select Recipes")
    for recipe in st.session_state.search_results:
        key = str(recipe["id"])
        checked = st.checkbox(recipe["title"], value=key in st.session_state.selected_recipes, key=key)
        
        if checked and key not in st.session_state.selected_recipes:
            # Fetch full details
            info = requests.get(f"https://api.spoonacular.com/recipes/{recipe['id']}/information", 
                              params={"apiKey": API_KEY}).json()
            ingredients = [{"amount": i.get("amount",0), "unit": i.get("unit",""), "name": i.get("name","")} 
                         for i in info.get("extendedIngredients", [])]
            st.session_state.selected_recipes[key] = {
                "title": recipe["title"],
                "ingredients": ingredients,
                "instructions": info.get("instructions", "Instructions not available."),
                "sourceUrl": recipe.get("sourceUrl")
            }
        elif not checked and key in st.session_state.selected_recipes:
            del st.session_state.selected_recipes[key]

# Show selected recipes with instructions
if st.session_state.selected_recipes:
    st.header("📋 Your Selected Recipes")
    for key, rec in list(st.session_state.selected_recipes.items()):
        with st.expander(f"🍲 {rec['title']}", expanded=True):
            st.markdown(f"[View Full Recipe Online]({rec.get('sourceUrl', '#')})")
            
            st.subheader("Ingredients")
            for ing in rec["ingredients"]:
                st.write(f"• {ing['amount']} {ing['unit']} {ing['name']}")
            
            st.subheader("Step-by-Step Instructions")
            st.markdown(rec["instructions"])

    # Shopping List
    st.header("🛒 Shopping List")
    shopping = {}
    for rec in st.session_state.selected_recipes.values():
        for ing in rec["ingredients"]:
            name = ing["name"].lower()
            shopping[name] = shopping.get(name, 0) + ing["amount"]
    
    df = pd.DataFrame([{"Item": k.title(), "Quantity": round(v,2)} for k,v in shopping.items()])
    st.dataframe(df, use_container_width=True)

    if st.button("🛍️ Add to Walmart Cart"):
        items = "+".join(shopping.keys())
        extra = "+generic" if "Cheapest" in price_mode else "+brand"
        url = f"https://www.walmart.com/search?q={items}{extra}"
        st.markdown(f"[➡️ Open Walmart with {price_mode} items →]({url})")
        st.info("Review cart on Walmart for delivery/pickup.")

    if st.button("Clear All"):
        st.session_state.selected_recipes = {}
        st.rerun()

st.caption("Real recipes • Quantities • Instructions • Walmart ready")