import streamlit as st
from app.constants import pick_type_icon
from app.your_thoughts import extract_date
from demo.demo_chat import DemoChat


def demo_thought_component(i, thought, key=""):
    chat: DemoChat = st.session_state.demo_chat
    l, r = st.columns((10, 1))
    with l:
        with st.expander(f"{pick_type_icon(thought['type'])} {thought['summary']}"):
            st.markdown(f"#### **_[{extract_date(thought['created_at'])}]_**")
            st.markdown(f"{thought['description']}")
    with r:
        if st.button(
            "💬",
            key=f"{key}_chat_{i}",
            use_container_width=True,
            help="Explore this thought in an AI chat!",
        ):
            chat.initialize_thought_chat(thought)
            chat.open_chat()
