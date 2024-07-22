import streamlit as st
from app.search import search_page
from app.suggestions import suggestions_page
from app.supabase_client import SupabaseClient
from app.your_thoughts import thought_page
from app.your_profile import profile_page
from app.chat_client import OpenAIChat
from app.constants import CONNECTIONS_TABLE


def home_page():
    # st.title("String Theories")
    initialize()

    if st.session_state.chat_open:
        st.session_state.chat.chat_page()
        with st.sidebar:
            if st.button(
                "Close Chat", key="close_chat_button", use_container_width=True
            ):
                st.session_state.chat_open = False
                st.rerun()
            st.divider()

    else:
        [
            your_search_page,
            your_thoughts_page,
            your_profile_page,
        ] = st.tabs(
            [
                "Search Thoughts",
                "All Thoughts",
                "Profile",
            ]
        )

        with your_search_page:
            search_page()

        with your_thoughts_page:
            thought_page()

        with your_profile_page:
            profile_page()

    with st.sidebar:
        st.link_button(
            "Give me feedback!",
            url="https://forms.gle/hYUzS95dmxY51nXN8",
            use_container_width=True,
            type="primary",
        )
        if st.button("Logout", key="logout_button", use_container_width=True):
            del st.session_state.user_id
            del st.session_state.your_posts
            del st.session_state.thoughts
            del st.session_state.user_info
            st.rerun()


def initialize():
    supabase: SupabaseClient = st.session_state.supabase
    if "thoughts" not in st.session_state:
        st.session_state.thoughts = supabase.list_thoughts(st.session_state.user_id)
        for thought in st.session_state.thoughts:
            thought[CONNECTIONS_TABLE] = supabase.list_connected_thoughts(thought["id"])
        st.session_state.thought_map = {
            thought["id"]: thought for thought in st.session_state.thoughts
        }
        st.session_state.display_thoughts = st.session_state.thoughts
    if "your_posts" not in st.session_state:
        st.session_state.your_posts = supabase.list_user_posts(st.session_state.user_id)
    if "user_info" not in st.session_state:
        st.session_state.user_info = supabase.get_user_info(st.session_state.user_id)
    if "topics" not in st.session_state:
        st.session_state.topics = supabase.list_user_topics(st.session_state.user_id)
        for topic in st.session_state.topics:
            topic["thoughts"] = supabase.list_thoughts_in_topic(topic["id"])

    if not "chat" in st.session_state:
        st.session_state.chat = OpenAIChat()

    if "chat_open" not in st.session_state:
        st.session_state.chat_open = False
