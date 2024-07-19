import streamlit as st
from chat_client import OpenAIChat
from your_thoughts import thought_component
from streamlit_extras.stoggle import stoggle


def handle_suggestion_click(query, prompt):
    chat: OpenAIChat = st.session_state.chat
    st.session_state.search_query = query
    st.session_state.search_results = chat.search_for_thoughts(prompt)


def search_page():
    chat: OpenAIChat = st.session_state.chat
    search = st.text_input(
        "Explore your thoughts:",
        key="search_text_input",
        placeholder="Show me thoughts about...",
    )
    if st.button("🔍 Search", key="search_button", use_container_width=True):
        if search:
            st.session_state.search_results = chat.search_for_thoughts(search)
            st.session_state.search_query = search
        else:
            st.error("Please enter a search query.")

    with st.container():
        [_, l, r, _] = st.columns((1, 10, 10, 1))
        with l:
            st.button(
                "Recommend ideas to explore.",
                key="recommend_button",
                use_container_width=True,
                on_click=handle_suggestion_click,
                args=(
                    "Recommend ideas to explore.",
                    "Recommend ideas for the user to explore that have high potential and can be expanded much deeper.",
                ),
            )
            st.button(
                "Find thoughts I haven't visited in a while.",
                key="revisit_button",
                use_container_width=True,
                on_click=handle_suggestion_click,
                args=(
                    "Find thoughts I haven't visited in a while.",
                    "Find thoughts the user haven't visited in a while, and have significant potential to be expanded and explored much more deeply.",
                ),
            )
        with r:
            st.button(
                "What have I been thinking recently?",
                key="frequent_button",
                use_container_width=True,
                on_click=handle_suggestion_click,
                args=(
                    "What have I been thinking recently?",
                    "Find thoughts that the user has been considering recently, and include thoughts that could potentially form unique connections/fit the current theme.",
                ),
            )
            st.button(
                "Which thoughts are unresolved?",
                key="unresolved_button",
                use_container_width=True,
                on_click=handle_suggestion_click,
                args=(
                    "Which thoughts are unresolved?",
                    "List questions and problems that have not been resolved in the user's thoughts and suggest new avenues to approach from.",
                ),
            )

    if "search_query" in st.session_state and st.session_state.search_query:
        st.divider()
        st.markdown(f"#### Search Results for _'{st.session_state.search_query}'_")
        for i, result in enumerate(st.session_state.search_results):
            thought_id = result["id"]
            suggestion = result["suggestion"]
            thought = st.session_state.thought_map[thought_id]
            thought_component(i, thought, key="search_results")
            _, text = st.columns((1, 15))
            with text:
                stoggle(
                    "Suggestion",
                    f"{suggestion}",
                )
            st.divider()
