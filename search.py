import streamlit as st
from chat_client import OpenAIChat
from your_thoughts import thought_component


def search_page():
    chat: OpenAIChat = st.session_state.chat
    search = st.text_input(
        "Search for thoughts using plain English:",
        key="search_text_input",
        placeholder="Show me thoughts about...",
    )
    if st.button("🔍 Search", key="search_button", use_container_width=True):
        if search:
            st.session_state.search_results = chat.search_for_thoughts(search)
            st.session_state.search_query = search
        else:
            st.error("Please enter a search query.")
    st.divider()

    if "search_query" in st.session_state and st.session_state.search_query:
        st.markdown(f"#### Search Results for _'{st.session_state.search_query}'_")
        for i, thought_id in enumerate(st.session_state.search_results):
            thought = st.session_state.thought_map[thought_id]
            thought_component(i, thought, key="search_results")
