import streamlit as st
from constants import IDEAS_TABLE
from supabase_helpers import list_user_posts


def posts_page():
    if "your_posts" not in st.session_state:
        st.session_state.your_posts = list_user_posts(st.session_state.user_id)

    if len(st.session_state.your_posts) == 0:
        st.write("You have not posted any ideas yet. Get started by clicking on the 'Your Ideas' tab above!")
        return
    
    for post in st.session_state.your_posts:
        idea = post[IDEAS_TABLE]
        st.markdown(f"#### {idea["summary"]}")
        st.markdown(f"*{idea["description"]}*")
        st.markdown(f"*Created: {idea["created_at"]}*")
        st.write(f":heart: {post["like_count"]}")
        st.divider()
