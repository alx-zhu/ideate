import streamlit as st
from app.supabase_client import SupabaseClient
from demo.demo import demo_page


def authentication_page():
    supabase: SupabaseClient = st.session_state.supabase
    # st.info(
    #     "Hi! Welcome to String Theories! This is my first prototype, so I'd love to hear your feedback. Please feel free to reach out to me at alexanderzhu07 [at] gmail [dot] com. Thanks for checking it out!\n\n I'd love to connect!\n - [LinkedIn](https://www.linkedin.com/in/zhu-alexander/),\n - [Github](https://github.com/alx-zhu),\n - Email: alexanderzhu07 [at] gmail [dot] com."
    # )
    st.warning(
        "Please note: thoughts created in the demo do not persist between sessions and are not saved to the database. Sign up to create your account and save your thoughts!"
    )
    [try_it, login, signup] = st.tabs(["Try it Out", "Login", "Sign Up"])

    with try_it:
        demo_page()

    with login:
        st.subheader("Login")
        with st.form("login_form", border=0):
            login_email = st.text_input("Email", key="login_email")
            login_password = st.text_input(
                "Password", type="password", key="login_password"
            )
            confirm_login = st.form_submit_button("Login")

        if confirm_login:
            if user := supabase.login_user(login_email, login_password):
                st.success(f"Successfully logged in.")
                st.session_state.user_id = user.id
                st.rerun()
            else:
                st.error(f"Login failed.")

    with signup:
        st.subheader("Sign Up")
        with st.form("signup_form", border=0):
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
                        st.rerun()
                    else:
                        st.error("Sign Up Failed.")
                else:
                    st.error("Passwords do not match.")
