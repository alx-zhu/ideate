import streamlit as st

from app.chat_client import OpenAIChat
from app.constants import CONNECTIONS_TABLE, SUMMARY_MAX, THOUGHT_TYPES
from app.supabase_client import SupabaseClient
from app.your_thoughts import (
    thought_component,
)


@st.experimental_dialog("Save Suggestion", width="large")
def save_suggestion_dialog(suggestion, source_id):
    supabase: SupabaseClient = st.session_state.supabase
    with st.form(key="thought_form"):
        new_type = st.selectbox(
            "Type",
            THOUGHT_TYPES,
            index=0,
            key="new_type_select",
        )
        summary = st.text_input("Thought one-liner", max_chars=SUMMARY_MAX)
        description = st.text_area("Describe your thought", value=suggestion)
        submit_button = st.form_submit_button(label="Submit")

    # Add the new thought to the session state
    if submit_button:
        if summary and description:
            if thought := supabase.add_thought(summary, description, new_type):
                st.session_state.thoughts = [thought] + st.session_state.thoughts
                st.session_state.thought_map[thought["id"]] = thought
                supabase.connect_thought(source_id, thought["id"])
                thought[CONNECTIONS_TABLE] = [source_id]
                st.success("Your thought has been added!")
                st.rerun()
            else:
                st.error("Error. Thought could not be added.")
        else:
            st.error("Please make sure all fields are filled out.")


def show_suggestions():
    categories = [
        "Recent and Frequent",
        "Thoughts to Revisit",
        "Unresolved Questions/Problems",
    ]

    for category_name in categories:
        category = st.session_state.suggestions[category_name]
        st.markdown(f"#### {category_name}")
        for i, thought_obj in enumerate(category):
            thought = st.session_state.thought_map[thought_obj["id"]]
            thought_component(i, thought, key=category_name)
            with st.container():
                text, btn, _ = st.columns((10, 1, 1))
                with text:
                    st.markdown(f"_{thought_obj['suggestion']}_")
                with btn:
                    if st.button(
                        "💾",
                        key=f"save_suggestion_{i}_{category_name}",
                        help="Save this as a thought!",
                    ):
                        save_suggestion_dialog(thought_obj["suggestion"], thought["id"])
        st.divider()


def suggestions_page():
    st.header("Suggested Thoughts")

    # new_problem = st.text_area(
    #     "What is one problem you came across today?", key="new_problem"
    # )

    # st.divider()
    if st.button("Give me suggestions"):
        chat: OpenAIChat = st.session_state.chat
        st.session_state.suggestions = chat.suggest_thoughts()

    if "suggestions" in st.session_state:
        show_suggestions()
