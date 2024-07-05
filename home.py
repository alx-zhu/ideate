import streamlit as st
from supabase_client import SupabaseClient
from your_thoughts import thought_page
from your_posts import posts_page
from your_profile import profile_page
from your_strings import strings_page
from your_graph import graph_page


def home_page():
    st.title("String Theories")
    [
        your_profile_page,
        your_thoughts_page,
        your_strings_page,
        your_graph_page,
    ] = st.tabs(["Profile", "Your Thoughts", "Your Strings", "Your Thought Graph"])

    initialize()
    with your_profile_page:
        profile_page()

    with your_thoughts_page:
        thought_page()

    with your_strings_page:
        strings_page()

    with your_graph_page:
        graph_page()

    # with your_posts_page:
    #     posts_page()


def initialize():
    supabase: SupabaseClient = st.session_state.supabase
    if "thoughts" not in st.session_state:
        st.session_state.thoughts = supabase.list_thoughts(st.session_state.user_id)
        for thought in st.session_state.thoughts:
            thought["edit_mode"] = False
    if "your_posts" not in st.session_state:
        st.session_state.your_posts = supabase.list_user_posts(st.session_state.user_id)
    if "user_info" not in st.session_state:
        st.session_state.user_info = supabase.get_user_info(st.session_state.user_id)
    if "strings" not in st.session_state:
        st.session_state.strings = supabase.list_user_strings(st.session_state.user_id)
        for string in st.session_state.strings:
            string["thoughts"] = supabase.list_thoughts_in_string(string["id"])
