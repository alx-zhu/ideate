import streamlit as st
from your_ideas import ideation_page
from your_posts import posts_page
from your_profile import profile_page
from your_strings import strings_page


def home_page():
    st.title("String Theories")
    [
        your_profile_page,
        your_ideas_page,
        your_strings_page,
        your_posts_page,
    ] = st.tabs(["Profile", "Your Ideas", "Your Strings", "Your Posts"])

    initialize()
    with your_profile_page:
        profile_page()

    with your_ideas_page:
        ideation_page()

    with your_strings_page:
        strings_page()

    with your_posts_page:
        posts_page()


def initialize():
    supabase = st.session_state.supabase
    if "ideas" not in st.session_state:
        st.session_state.ideas = supabase.list_ideas(st.session_state.user_id)
        for idea in st.session_state.ideas:
            idea["edit_mode"] = False
    if "your_posts" not in st.session_state:
        st.session_state.your_posts = supabase.list_user_posts(st.session_state.user_id)
    if "user_info" not in st.session_state:
        st.session_state.user_info = supabase.get_user_info(st.session_state.user_id)
    if "strings" not in st.session_state:
        st.session_state.strings = supabase.list_user_strings(st.session_state.user_id)
        for string in st.session_state.strings:
            string["ideas"] = supabase.list_ideas_in_string(string["id"])
