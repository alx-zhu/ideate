import streamlit as st
from constants import SUMMARY_MAX, DESCRIPTION_MAX
from supabase_client import SupabaseClient


def save_profile(info):
    supabase: SupabaseClient = st.session_state.supabase
    st.session_state.user_info = info
    if supabase.update_user_info(user_id=st.session_state.user_id, **info):
        st.success("Profile updated successfully")
    else:
        st.error("Profile update failed")
    st.rerun()


@st.experimental_dialog("Edit Profile", width="large")
def edit_profile_dialog(info):
    st.markdown("### Edit Profile")
    with st.form(key="profile_form"):
        l, r = st.columns(2)
        with l:
            info["first_name"] = st.text_input("First Name", info["first_name"])
        with r:
            info["last_name"] = st.text_input("Last Name", info["last_name"])
        info["email"] = st.text_input("Email", info["email"])
        info["tagline"] = st.text_input(
            "Tagline", info["tagline"], max_chars=SUMMARY_MAX
        )
        info["bio"] = st.text_area("Bio", info["bio"], max_chars=DESCRIPTION_MAX)
        submit_profile_edits = st.form_submit_button("Save")

    if submit_profile_edits:
        save_profile(info)


def profile_page():
    supabase: SupabaseClient = st.session_state.supabase
    if "user_id" not in st.session_state:
        st.error("User not logged in")
        return

    info = st.session_state.user_info
    total_likes = supabase.count_user_likes(st.session_state.user_id)
    # with st.container(border=True):
    l, r = st.columns((8, 1))
    with l:
        st.subheader(f"{info['first_name']} {info['last_name']} ({info['email']})")
    with r:
        if st.button("Edit", key="edit_profile_button"):
            edit_profile_dialog(info)
    st.markdown(
        f"#### *{info['tagline']}*" if info["tagline"] else "#### *No tagline yet*"
    )
    st.markdown(f"{info['bio']}" if info["bio"] else "*No bio yet*")

    st.divider()
    st.markdown(f"### Your Stats")
    row1 = st.columns(4)
    with row1[0]:
        with st.container(border=True):
            st.subheader(f"Streak")
            st.header(f"{info['streak']} :fire:")
    with row1[1]:
        with st.container(border=True):
            st.subheader(f"Ideas")
            st.header(
                f"{len(st.session_state.thoughts) if 'thoughts' in st.session_state else 0} :bulb:"
            )
    with row1[2]:
        with st.container(border=True):
            st.subheader(f"Posts")
            st.header(
                f"{len(st.session_state.your_posts) if 'your_posts' in st.session_state else 0} :pencil:"
            )
    with row1[3]:
        with st.container(border=True):
            st.subheader(f"Likes")
            st.header(f"{total_likes} :heart:")

    row2 = st.columns(4)
    with row2[0]:
        with st.container(border=True):
            st.subheader(f"Longest")
            st.header(f"{info['best_streak']} :fire:")
    with row2[1]:
        with st.container(border=True):
            st.subheader(f"Strings")
            st.header(
                f"{len(st.session_state.strings) if 'strings' in st.session_state else 0} :thread:"
            )
