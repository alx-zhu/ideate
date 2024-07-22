import streamlit as st
from app.about import about_page
from app.constants import ABOUT_PAGE
from app.home import home_page
from app.authentication import authentication_page
from app.supabase_client import SupabaseClient


def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


if __name__ == "__main__":

    local_css("style.css")

    if "supabase" not in st.session_state:
        st.session_state.supabase = SupabaseClient()

    supabase: SupabaseClient = st.session_state.supabase

    if "page" not in st.session_state:
        st.session_state.page = "Login/Sign Up"
    if "user_id" in st.session_state and st.session_state.user_id:
        home_page()

        # with st.sidebar:
        #     st.selectbox(
        #         "Navigation",
        #         [HOME_PAGE, FEED_PAGE, ABOUT_PAGE],
        #         key="page",
        #     )

        # if st.session_state.page == HOME_PAGE:
        #     home_page()
        # elif st.session_state.page == ABOUT_PAGE:
        #     about_page()

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
