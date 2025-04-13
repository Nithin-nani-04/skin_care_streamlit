

import streamlit as st
import pandas as pd
import json
import os

# ---------- CONFIG ---------- 
DATA_FILE = 'MP-Skin Care Product Recommendation System3.csv'
USER_DB = 'user_data.json'

# ---------- HELPER FUNCTIONS ----------

def load_products():
    return pd.read_csv(DATA_FILE)

def load_user_db():
    if not os.path.exists(USER_DB):
        with open(USER_DB, 'w') as f:
            json.dump({"users": {}}, f)
    with open(USER_DB, 'r') as f:
        return json.load(f)

def save_user_db(db):
    with open(USER_DB, 'w') as f:
        json.dump(db, f, indent=4)

def recommend_product(pigmentation, hydration, oily):
    if pigmentation == 'High' and hydration == 'Low' and oily == 'High':
        return 'Oily, Pigmented'
    elif pigmentation == 'High' and hydration == 'High' and oily == 'Low':
        return 'Dry, Pigmented'
    elif pigmentation == 'Low' and hydration == 'High' and oily == 'Low':
        return 'Dry, Sensitive'
    elif pigmentation == 'Low' and hydration == 'Medium' and oily == 'Medium':
        return 'Combination, Sensitive'
    elif pigmentation == 'Low' and hydration == 'High' and oily == 'Medium':
        return 'Combination, Sensitive'
    elif pigmentation == 'Medium' and hydration == 'Medium' and oily == 'Low':
        return 'Normal, Balanced'
    elif pigmentation == 'Medium' and hydration == 'High' and oily == 'Medium':
        return 'Combination, Balanced'
    elif pigmentation == 'Medium' and hydration == 'Medium' and oily == 'High':
        return 'Oily, Balanced'
    else:
        return 'Normal'

def map_to_existing_skin_types(detected_skin_type):
    # Mapping detected skin types to existing product skin types
    existing_skin_types = {
        'Oily, Pigmented': 'Oily',
        'Dry, Pigmented': 'Dry',
        'Dry, Sensitive': 'Dry, Sensitive',
        'Combination, Sensitive': 'Combination, Sensitive',
        'Normal, Balanced': 'Normal, Dry, Combination',
        'Combination, Balanced': 'Normal, Dry, Oily, Combination, Sensitive',
        'Oily, Balanced': 'Oily, Combination, Sensitive',
        'Normal': 'Normal, Dry'  # Example: mapping Normal to Normal, Dry
    }
    
    return existing_skin_types.get(detected_skin_type, 'Normal')

def detect_skin_type(pigmentation, hydration, oily):
    if pigmentation == 'High' and hydration == 'Low' and oily == 'High':
        detected_skin_type = 'Oily, Pigmented'
    elif pigmentation == 'High' and hydration == 'High' and oily == 'Low':
        detected_skin_type = 'Dry, Pigmented'
    elif pigmentation == 'Low' and hydration == 'High' and oily == 'Low':
        detected_skin_type = 'Dry, Sensitive'
    elif pigmentation == 'Low' and hydration == 'Medium' and oily == 'Medium':
        detected_skin_type = 'Combination, Sensitive'
    elif pigmentation == 'Low' and hydration == 'High' and oily == 'Medium':
        detected_skin_type = 'Combination, Sensitive'
    elif pigmentation == 'Medium' and hydration == 'Medium' and oily == 'Low':
        detected_skin_type = 'Normal, Balanced'
    elif pigmentation == 'Medium' and hydration == 'High' and oily == 'Medium':
        detected_skin_type = 'Combination, Balanced'
    elif pigmentation == 'Medium' and hydration == 'Medium' and oily == 'High':
        detected_skin_type = 'Oily, Balanced'
    else:
        detected_skin_type = 'Normal'
    
    # Map to existing skin types
    return map_to_existing_skin_types(detected_skin_type)

# ---------- LOGIN & REGISTRATION ----------

def login_section(user_db):
    st.title("🔐 Login or Register")
    action = st.selectbox("Choose Action", ["Login", "Register"])
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button(action):
        if action == "Login":
            if username in user_db['users'] and user_db['users'][username]['password'] == password:
                st.success("Logged in successfully!")
                st.session_state['user'] = username
                st.session_state['feedback_stage'] = False  # Set the feedback stage to False on login
            else:
                st.error("Invalid credentials.")
        else:  # Register
            if username in user_db['users']:
                st.error("User already exists.")
            else:
                user_db['users'][username] = {"password": password, "history": [], "feedback": []}
                save_user_db(user_db)
                st.success("Registered successfully! Please login.")

# ---------- MAIN APPLICATION ----------

def main_app(user_db, username):
    st.sidebar.title(f"👋 Welcome, {username}")

    # Add a sidebar with a menu
    menu = ["Find Page", "Feedback", "Logout"]
    choice = st.sidebar.radio("Menu", menu)

    if choice == "Logout":
        del st.session_state['user']
        st.session_state['feedback_stage'] = False  # Reset feedback stage on logout
        st.rerun()

    elif choice == "Find Page":
        df_products = load_products()

        st.title("🌿 Skin Care Product Recommender")

        st.header("🧖‍♀️ Your Skin Condition")
        pigmentation = st.selectbox("Pigmentation Level", ['Low', 'Medium', 'High'])
        hydration = st.selectbox("Hydration Level", ['Low', 'Medium', 'High'])
        oily = st.selectbox("Oily Level", ['Low', 'Medium', 'High'])

        if st.button("🔍 Get Recommendations"):
            recommended_type = recommend_product(pigmentation, hydration, oily)
            user_skin_type = detect_skin_type(pigmentation, hydration, oily)

            st.subheader(f"🎯 Recommended Product Type: **{recommended_type}**")
            st.markdown(f"🧬 Detected Skin Type: **{user_skin_type}**")

            matching_products = df_products[
                df_products['skintype'].str.contains(user_skin_type, case=False, na=False)
            ]

            # Show 20 products per page
            page_size = 20
            total_pages = len(matching_products) // page_size + (1 if len(matching_products) % page_size != 0 else 0)
            page = st.selectbox("Select Page", range(1, total_pages + 1))

            start_idx = (page - 1) * page_size
            end_idx = min(page * page_size, len(matching_products))

            st.markdown("### 🛍️ Recommended Products:")
            for _, row in matching_products.iloc[start_idx:end_idx].iterrows():
                st.image(row['picture_src'], width=200)
                st.markdown(f"**Product:** {row['product_name']}")
                st.markdown(f"**Brand:** {row['brand']}")
                st.markdown(f"**Price:** {row['price']}")
                st.markdown(f"**Effects:** {row['notable_effects']}")
                st.markdown(f"**Description:** {row['description']}")
                st.markdown(f"[🔗 View Product]({row['product_href']})")
                st.markdown("---")

            history_entry = {
                "inputs": {
                    "pigmentation": pigmentation,
                    "hydration": hydration,
                    "oily": oily
                },
                "detected_skin_type": user_skin_type,
                "recommendation": recommended_type
            }
            user_db['users'][username]['history'].append(history_entry)
            save_user_db(user_db)

            if st.button("Give Feedback"):
                st.session_state['feedback_stage'] = True  # Set the feedback stage to True
                st.experimental_rerun()

    elif choice == "Feedback":
        feedback_page(user_db, username)

# ---------- FEEDBACK PAGE ----------

def feedback_page(user_db, username):
    st.title("📝 Feedback")

    # Collecting the feedback text
    feedback_text = st.text_area("Let us know what you think!", "")
    
    # Additional inputs for gathering more information
    product_rating = st.slider("Rate the product (1-5)", 1, 5, 3)
    product_improvement = st.text_area("How can we improve the product?", "")
    would_recommend = st.radio("Would you recommend this product?", ('Yes', 'No'))

    if st.button("📨 Submit Feedback"):
        if feedback_text.strip():
            # Create a feedback entry
            feedback_entry = {
                'feedback': feedback_text.strip(),
                'product_rating': product_rating,
                'product_improvement': product_improvement.strip(),
                'would_recommend': would_recommend
            }
            
            # Add feedback entry to user history
            user_db['users'][username]['feedback'].append(feedback_entry)
            save_user_db(user_db)
            
            # Provide feedback success message
            st.success("Thanks for your feedback!")
            
            # Reset the feedback stage and rerun the app to show updated data
            st.session_state['feedback_stage'] = False
            st.rerun()  # Re-run the app to reflect changes
        else:
            st.warning("Feedback cannot be empty.")


# ---------- MAIN ----------

def main():
    user_db = load_user_db()

    if 'user' not in st.session_state:
        login_section(user_db)
    elif 'feedback_stage' in st.session_state and st.session_state['feedback_stage']:
        feedback_page(user_db, st.session_state['user'])
    else:
        main_app(user_db, st.session_state['user'])

if __name__ == "__main__":
    main()
