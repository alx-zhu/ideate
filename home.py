import streamlit as st
from supabase_helpers import get_user_info, list_ideas, list_user_posts
from your_ideas import ideation_page
from feed import feed_page
from your_posts import posts_page
from your_profile import profile_page


def home_page():
    initialize()

    st.title("Ideate")
    [your_profile_page, your_ideas_page, your_posts_page, your_feed_page] = st.tabs(
        ["Profile", "Your Ideas", "Your Posts", "Feed"]
    )
    with your_profile_page:
        profile_page()

    with your_ideas_page:
        ideation_page()

    with your_posts_page:
        posts_page()

    with your_feed_page:
        feed_page()


def initialize():
    if "ideas" not in st.session_state:
        st.session_state.ideas = list_ideas(st.session_state.user_id)
        for idea in st.session_state.ideas:
            idea["edit_mode"] = False
    if "your_posts" not in st.session_state:
        st.session_state.your_posts = list_user_posts(st.session_state.user_id)
    if "user_info" not in st.session_state:
        st.session_state.user_info = get_user_info(st.session_state.user_id)
