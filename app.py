import streamlit as st
from home import show_home
from charts import show_charts
from auth import authenticate_user, logout


# Initialize the application
st.set_page_config(page_title="Production Manager App", layout="wide")
st.title("Production Manager App")


# Initialize user session
if 'user' not in st.session_state:
    st.session_state.user = None


# Login Panel
if st.session_state.user is None:
    user = authenticate_user()
    if user:
        st.session_state.user = user
        st.sidebar.success(f"Logged in as {user['Username']}")
else:
    st.sidebar.write(f"Logged in as {st.session_state.user['Username']}")
    if st.sidebar.button("Logout"):
        logout()


# Sidebar Navigation
if st.session_state.user is not None:
    menu = st.sidebar.radio("Navigation", ["Home", "Production Charts"])

    if menu == "Home":
        show_home()
    elif menu == "Production Charts":
        show_charts()
