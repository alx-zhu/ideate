import streamlit as st
from supabase_client import SupabaseClient
from your_thoughts import thought_page
from your_posts import posts_page
from your_profile import profile_page
from your_topics import topics_page
from your_graph import graph_page
from chat import chat_page
from constants import CHAT_WELCOME_MESSAGE


def home_page():
    st.title("String Theories")
    [
        your_profile_page,
        your_thoughts_page,
        your_chat_page,
    ] = st.tabs(["Profile", "Your Thoughts", "Chat"])

    initialize()
    with your_profile_page:
        profile_page()

    with your_thoughts_page:
        thought_page()

    with your_chat_page:
        chat_page(CHAT_WELCOME_MESSAGE)

    # with your_graph_page:
    #     graph_page()

    # with your_posts_page:
    #     posts_page()


def initialize():
    supabase: SupabaseClient = st.session_state.supabase
    if "thoughts" not in st.session_state:
        st.session_state.thoughts = supabase.list_thoughts(st.session_state.user_id)
        for thought in st.session_state.thoughts:
            thought["strings"] = supabase.list_connected_thoughts(thought["id"])
        st.session_state.thought_map = {
            thought["id"]: thought for thought in st.session_state.thoughts
        }
    if "your_posts" not in st.session_state:
        st.session_state.your_posts = supabase.list_user_posts(st.session_state.user_id)
    if "user_info" not in st.session_state:
        st.session_state.user_info = supabase.get_user_info(st.session_state.user_id)
    if "topics" not in st.session_state:
        st.session_state.topics = supabase.list_user_topics(st.session_state.user_id)
        for topic in st.session_state.topics:
            topic["thoughts"] = supabase.list_thoughts_in_topic(topic["id"])
