import streamlit as st
from your_ideas import ideation_page
from feed import feed_page
from your_posts import posts_page


def home_page():
    st.title("Ideate")
    [your_profile_page, your_ideas_page, your_posts_page, your_feed_page] = st.tabs(
        ["Profile", "Your Ideas", "Your Posts", "Feed"]
    )
    with your_profile_page:
        st.write("Profile")

    with your_ideas_page:
        ideation_page()

    with your_posts_page:
        posts_page()

    with your_feed_page:
        feed_page()
