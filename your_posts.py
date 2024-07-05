import streamlit as st
from constants import IDEAS_TABLE
from supabase_client import SupabaseClient


def posts_page():
    supabase: SupabaseClient = st.session_state.supabase
    if "your_posts" not in st.session_state:
        st.session_state.your_posts = supabase.list_user_posts(st.session_state.user_id)

    if len(st.session_state.your_posts) == 0:
        st.write(
            "You have not posted any thoughts yet. Get started by clicking on the 'Your Ideas' tab above!"
        )
        return

    for post in st.session_state.your_posts:
        thought = post[IDEAS_TABLE]
        st.markdown(f"#### {thought['summary']}")
        st.markdown(f"*{thought['description']}*")
        st.markdown(f"*Created: {thought['created_at']}*")
        st.write(f":heart: {post['like_count']}")
        st.divider()
