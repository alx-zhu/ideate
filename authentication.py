import streamlit as st
from supabase_client import SupabaseClient


def authentication_page():
    supabase: SupabaseClient = st.session_state.supabase
    tabs = st.tabs(["Login", "Sign Up"])

    with tabs[0]:
        st.subheader("Login")
        login_email = st.text_input("Email", key="login_email")
        login_password = st.text_input(
            "Password", type="password", key="login_password"
        )

        if st.button("Login"):
            if user := supabase.login_user(login_email, login_password):
                st.success(f"Successfully logged in.")
                st.session_state.user_id = user.id
                st.rerun()
            else:
                st.error(f"Login failed.")

    with tabs[1]:
        st.subheader("Sign Up")
        l, r = st.columns(2)
        with l:
            first_name = st.text_input("First Name", key="first_name")
        with r:
            last_name = st.text_input("Last Name", key="last_name")
        signup_email = st.text_input("Email", key="signup_email")
        signup_password = st.text_input(
            "Password", key="signup_password", type="password"
        )
        signup_password_confirm = st.text_input(
            "Confirm Password", key="signup_password_confirm", type="password"
        )

        if st.button("Sign Up"):
            if signup_password == signup_password_confirm:
                if user := supabase.sign_up_user(
                    signup_email, signup_password, first_name, last_name
                ):
                    st.success(f"Successfully signed up.")
                    st.session_state.user_id = user.id
                    st.rerun()
                else:
                    st.error("Sign Up Failed.")
            else:
                st.error("Passwords do not match.")
