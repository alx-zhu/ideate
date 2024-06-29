import streamlit as st
from your_ideas import ideation_page
from feed import feed_page


def home_page():
    [profile_page, ideas_page, posts_page, feed_page] = st.tabs(
        ["Profile", "Your Ideas", "Your Posts", "Feed"]
    )
    with profile_page:
        st.write("Profile")

    with ideas_page:
        ideation_page()

    with posts_page:
        st.write("Posts")

    with feed_page:
        feed_page()
