import streamlit as st
from about import about_page
from constants import ABOUT_PAGE, FEED_PAGE, HOME_PAGE
from feed import feed_page
from home import home_page
from authentication import authentication_page
from supabase_client import SupabaseClient


if __name__ == "__main__":
    if "supabase" not in st.session_state:
        st.session_state.supabase = SupabaseClient()

    supabase: SupabaseClient = st.session_state.supabase
    if "page" not in st.session_state:
        st.session_state.page = "Login/Sign Up"
    if "user_id" in st.session_state and st.session_state.user_id:
        # home_page()

        with st.sidebar:
            st.selectbox(
                "Navigation",
                [HOME_PAGE, FEED_PAGE, ABOUT_PAGE],
                key="page",
            )

        if st.session_state.page == HOME_PAGE:
            home_page()
        elif st.session_state.page == FEED_PAGE:
            feed_page()
        elif st.session_state.page == ABOUT_PAGE:
            about_page()

        with st.sidebar:
            st.link_button(
                "Give me feedback!",
                url="https://forms.gle/hYUzS95dmxY51nXN8",
                use_container_width=True,
                type="primary",
            )
            if st.button("Logout", key="logout_button", use_container_width=True):
                st.session_state.user_id = None
                st.session_state.your_posts = None
                st.session_state.thoughts = None
                st.session_state.user_info = None
                st.rerun()

    else:
        with st.sidebar:
            st.selectbox(
                "Navigation",
                ["Login/Sign Up", ABOUT_PAGE],
                key="page",
                index=0,
            )
        if st.session_state.page == "Login/Sign Up":
            authentication_page()
        elif st.session_state.page == ABOUT_PAGE:
            about_page()
