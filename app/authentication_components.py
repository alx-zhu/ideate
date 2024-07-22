import streamlit as st
from app.supabase_client import SupabaseClient


def login_component(key=""):
    supabase: SupabaseClient = st.session_state.supabase
    st.subheader("Login")
    with st.form(f"{key}_login_form", border=0):
        login_email = st.text_input("Email", key=f"{key}_login_email")
        login_password = st.text_input(
            "Password", type="password", key=f"{key}_login_password"
        )
        confirm_login = st.form_submit_button("Login")

    if confirm_login:
        if user := supabase.login_user(login_email, login_password):
            st.success(f"Successfully logged in.")
            st.session_state.user_id = user.id
            st.rerun()
        else:
            st.error(f"Login failed.")


def sign_up_component(key=""):
    supabase: SupabaseClient = st.session_state.supabase
    st.subheader("Sign Up")
    with st.form(f"{key}_signup_form", border=0):
        l, r = st.columns(2)
        with l:
            first_name = st.text_input("First Name", key=f"{key}_first_name")
        with r:
            last_name = st.text_input("Last Name", key=f"{key}_last_name")
        signup_email = st.text_input("Email", key=f"{key}_signup_email")
        signup_password = st.text_input(
            "Password", key=f"{key}_signup_password", type="password"
        )
        signup_password_confirm = st.text_input(
            "Confirm Password", key=f"{key}_signup_password_confirm", type="password"
        )
        confirm_signup = st.form_submit_button("Sign Up")

    if confirm_signup:
        if (
            not signup_email
            or not signup_password
            or not signup_password_confirm
            or not first_name
            or not last_name
        ):
            st.error("Please fill out all fields.")
        else:
            if signup_password == signup_password_confirm:
                if user := supabase.sign_up_user(
                    signup_email, signup_password, first_name, last_name
                ):
                    st.success(f"Successfully signed up.")
                    st.session_state.user_id = user.id

                    for thought in st.session_state.demo_thoughts:
                        supabase.add_thought(
                            thought["summary"], thought["description"], thought["type"]
                        )

                    st.rerun()
                else:
                    st.error("Sign Up Failed.")
            else:
                st.error("Passwords do not match.")
