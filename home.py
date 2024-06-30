import streamlit as st
from supabase_helpers import (
    get_user_info,
    list_ideas,
    list_ideas_in_string,
    list_user_posts,
    list_user_strings,
)
from your_ideas import ideation_page
from your_posts import posts_page
from your_profile import profile_page
from your_strings import strings_page
from supabase_helpers import get_current_user


def home_page():
    _, error = get_current_user()
    if error:
        st.error("An error occured or your session expired. Please log in again.")
        return
    initialize()
    st.title("String Theories")
    [
        your_profile_page,
        your_ideas_page,
        your_strings_page,
        your_posts_page,
    ] = st.tabs(["Profile", "Your Ideas", "Your Idea Strings", "Your Posts"])

    with your_profile_page:
        profile_page()

    with your_ideas_page:
        ideation_page()

    with your_strings_page:
        strings_page()

    with your_posts_page:
        posts_page()


def initialize():
    if "ideas" not in st.session_state:
        st.session_state.ideas = list_ideas(st.session_state.user_id)
        for idea in st.session_state.ideas:
            idea["edit_mode"] = False
    if "your_posts" not in st.session_state:
        st.session_state.your_posts = list_user_posts(st.session_state.user_id)
    if "user_info" not in st.session_state:
        st.session_state.user_info = get_user_info(st.session_state.user_id)
        print(st.session_state.user_info)
    if "strings" not in st.session_state:
        st.session_state.strings = list_user_strings(st.session_state.user_id)
        for string in st.session_state.strings:
            string["ideas"] = list_ideas_in_string(string["id"])
