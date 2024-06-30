import streamlit as st
from about import about_page
from feed import feed_page
from home import home_page
from authentication import authentication_page
from supabase_helpers import get_current_user

if __name__ == "__main__":
    user, error = get_current_user()
    if user:
        if "page" not in st.session_state or st.session_state.page == "Login/Sign Up":
            st.session_state.page = "About"

        if st.session_state.page == "About":
            about_page()
        elif st.session_state.page == "Your Ideas":
            home_page()
        elif st.session_state.page == "Feed":
            feed_page()

        with st.sidebar:
            st.selectbox(
                "Navigation",
                ["About", "Your Ideas", "Feed"],
                key="page",
                index=0,
            )
            st.link_button(
                "Give me feedback!",
                url="https://forms.gle/hYUzS95dmxY51nXN8",
                use_container_width=True,
                type="primary",
            )
            if st.button("Logout", key="logout_button", use_container_width=True):
                st.session_state.user_id = None
                st.session_state.your_posts = None
                st.session_state.ideas = None
                st.session_state.user_info = None
                st.rerun()

    else:
        if error:
            st.error("An error occured or your session expired. Please log in again.")
        with st.sidebar:
            st.selectbox(
                "Navigation",
                ["Login/Sign Up", "About"],
                key="page",
                index=0,
            )
        if st.session_state.page == "Login/Sign Up":
            authentication_page()
        elif st.session_state.page == "About":
            about_page()
