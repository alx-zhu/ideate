import streamlit as st
from streamlit_mic_recorder import speech_to_text
from datetime import datetime
from streamlit_extras.add_vertical_space import add_vertical_space

from app.constants import (
    CONNECTIONS_TABLE,
    DESCRIPTION_MAX,
    SUMMARY_MAX,
    THOUGHT_TYPES,
    pick_type_icon,
)
from app.supabase_client import SupabaseClient
from demo.demo_chat import DemoChat
from demo.demo_components import demo_thought_component
from demo.demo_search import demo_search_page
from app.authentication_components import sign_up_component


@st.experimental_dialog("Add New Thought", width="large")
def demo_new_thought_dialog():
    with st.form(key="thought_form"):
        new_type = st.selectbox(
            "Type",
            THOUGHT_TYPES,
            index=0,
            key="new_type_select",
        )
        summary = st.text_input("Thought one-liner", max_chars=SUMMARY_MAX)
        description = st.text_area("Describe your thought:", max_chars=DESCRIPTION_MAX)
        submit_button = st.form_submit_button(label="Submit")

    # Add the new thought to the session state
    if submit_button:
        print(summary, description)
        if summary and description:
            thought = {
                "type": new_type,
                "summary": summary,
                "description": description,
                "id": len(st.session_state.demo_thoughts),
                "created_at": datetime.now().isoformat(),
            }
            st.session_state.demo_thoughts = [thought] + st.session_state.demo_thoughts
            st.session_state.demo_thought_map[thought["id"]] = thought
            print(thought)
            st.success("Your thought has been added!")
            st.rerun()
        else:
            st.error("Please make sure all fields are filled out.")


@st.experimental_dialog("Think Out Loud", width="large")
def demo_think_out_loud_dialog():
    st.markdown(
        "### Just write down or record your stream of consciousness, and we'll help you organize it into thoughts!"
    )
    transcribed = speech_to_text(
        language="en",
        start_prompt="🔴 Record Audio",
        stop_prompt="🛑 Stop Recording",
        just_once=False,
        use_container_width=False,
        callback=None,
        key="thought_recording",
    )
    with st.form(key="thought_form"):
        thought_text = st.text_area(
            "Your thoughts:", value=transcribed if transcribed else ""
        )
        submit_button = st.form_submit_button("Submit")
    if submit_button:
        if thought_text:
            st.session_state.demo_chat.summarize_thought(thought_text)
            st.success("Your thoughts have been organized!")
            st.rerun()
        else:
            st.error("Please make sure all fields are filled out.")


def authentication_dialog():
    with st.form("login_form", border=0):
        login_email = st.text_input("Email", key="login_email")
        login_password = st.text_input(
            "Password", type="password", key="login_password"
        )
        confirm_login = st.form_submit_button("Login")


def demo_page():
    supabase = st.session_state.supabase
    if not "chat_open" in st.session_state:
        st.session_state.chat_open = False

    if not "demo_chat" in st.session_state:
        st.session_state.demo_chat = DemoChat()

    if "demo_thoughts" not in st.session_state:
        st.session_state.demo_thoughts = []
        st.session_state.demo_thought_map = {}

    chat = st.session_state.demo_chat
    if st.session_state.chat_open:
        st.session_state.demo_chat.chat_page()
        with st.sidebar:
            if st.button(
                "Close Chat", key="close_chat_button", use_container_width=True
            ):
                st.session_state.chat_open = False
                st.rerun()
            add_vertical_space(2)
    else:
        with st.container(border=True):
            st.markdown(
                "##### 1. Add a thought manually, record your voice, or through conversation!"
            )

            button_l, button_r, button_edge = st.columns((5, 5, 1))

            with button_l:
                # Display all thoughts
                if st.button("Add a Thought", use_container_width=True, type="primary"):
                    demo_new_thought_dialog()

            with button_r:
                if st.button(
                    "Think Out Loud", use_container_width=True, type="primary"
                ):
                    demo_think_out_loud_dialog()

            with button_edge:
                if st.button(
                    "💬",
                    use_container_width=True,
                    type="primary",
                    help="Have an open-ended conversation with the AI.",
                ):
                    chat.initialize_general_chat()
                    chat.open_chat()

        add_vertical_space(2)
        with st.container(border=True):
            st.markdown(
                "##### 2. List your thoughts and challenge them through conversation."
            )
            print(st.session_state.demo_thoughts)
            if len(st.session_state.demo_thoughts) == 0:
                st.info("You haven't added any thoughts yet.")
            else:
                for i, thought in enumerate(st.session_state.demo_thoughts):
                    demo_thought_component(i, thought, key="demo")

        add_vertical_space(2)

        with st.container(border=True):
            st.markdown("##### 3. Search for thoughts using plain English.")
            demo_search_page()
        add_vertical_space(2)

        with st.container(border=True):
            st.markdown("##### 4. Sign up to save your thoughts.")
            sign_up_component(key="demo")
