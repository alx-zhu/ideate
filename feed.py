import streamlit as st
from supabase_helpers import list_posts
from constants import IDEAS_TABLE, USERS_TABLE


def feed_page():
    st.title("Feed")

    with st.sidebar:
        if st.button("My Profile"):
            st.session_state.feed = False
            st.rerun()

    if "posts" not in st.session_state:
        st.session_state.posts = list_posts()

    st.divider()
    for post in st.session_state.posts:
        idea = post[IDEAS_TABLE]
        user = post[USERS_TABLE]
        st.markdown(f"#### {idea["summary"]}")
        st.markdown(f"*{idea["description"]}*")
        st.markdown(f"*Created: {idea["created_at"]}*")
        st.write(f"Idea by **{user["first_name"]} {user["last_name"]}** ({user["email"]})")
        st.divider()
    
