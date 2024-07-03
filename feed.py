import streamlit as st
from constants import IDEAS_TABLE, USERS_TABLE
from supabase_client import SupabaseClient


def like_post(i, post):
    supabase: SupabaseClient = st.session_state.supabase
    supabase.user_likes_post(st.session_state.user_id, post["id"])
    st.session_state.posts[i]["like_count"] += 1
    st.session_state.posts[i]["has_liked"] = True


def unlike_post(i, post):
    supabase: SupabaseClient = st.session_state.supabase
    supabase.user_unlikes_post(st.session_state.user_id, post["id"])
    st.session_state.posts[i]["like_count"] -= 1
    st.session_state.posts[i]["has_liked"] = False


def feed_page():
    supabase: SupabaseClient = st.session_state.supabase
    st.title("Feed")
    st.divider()
    st.session_state.posts = supabase.list_posts()
    for post in st.session_state.posts:
        post["has_liked"] = supabase.check_if_user_likes_post(
            st.session_state.user_id, post["id"]
        )

    for i, post in enumerate(st.session_state.posts):
        idea = post[IDEAS_TABLE]
        user = post[USERS_TABLE]
        st.markdown(f"#### {idea['summary']}")
        st.markdown(f"*{idea['description']}*")
        st.markdown(f"*Created: {idea['created_at']}*")
        st.write(f"Idea by **{user['first_name']} {user['last_name']}**")
        if post["has_liked"]:
            st.button(
                f":heart: {post['like_count']}",
                key=f"unlike_{i}",
                type="primary",
                on_click=unlike_post,
                args=(i, post),
            )
        else:
            st.button(
                f":heart: {post['like_count']}",
                key=f"like_{i}",
                on_click=like_post,
                args=(i, post),
            )
        st.divider()
