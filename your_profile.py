import streamlit as st
from supabase_helpers import count_user_likes, update_user_info
from constants import SUMMARY_MAX, DESCRIPTION_MAX

def save_profile(info):
    st.session_state.user_info = info
    if update_user_info(user_id=st.session_state.user_id, **info):
        st.success("Profile updated successfully")
    else:
        st.error("Profile update failed")
    st.rerun()

@st.experimental_dialog("Edit Profile")
def edit_profile_dialog(info):
    st.markdown("### Edit Profile")
    with st.form("profile_form"):
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
        submit_profile = st.form_submit_button("Save")
    if submit_profile:
        save_profile(info)


def profile_page():
    if "user_id" not in st.session_state:
        st.error("User not logged in")
        return

    info = st.session_state.user_info
    total_likes = count_user_likes(st.session_state.user_id)
    # with st.container(border=True):
    l, r = st.columns((8, 1))
    with l:
        st.subheader(f"{info['first_name']} {info['last_name']} ({info['email']})")
    with r:
        st.button("Edit", on_click=edit_profile_dialog, args=(info,), key="edit_profile_button")
    st.markdown(f"#### *{info["tagline"]}*" if info["tagline"] else "#### *No tagline yet*")
    st.markdown(f"{info['bio']}" if info["bio"] else "*No bio yet*")
    

    st.divider()
    st.markdown(f"### Your Stats")
    row1 = st.columns(4)
    with row1[0]:
        with st.container(border=True):
            st.subheader(f"Streak")
            st.title(f"{info['streak']} :fire:")
    with row1[1]:
        with st.container(border=True):
            st.subheader(f"Ideas")
            st.title(f"{len(st.session_state.ideas) if 'ideas' in st.session_state else 0} :bulb:")
    with row1[2]:
        with st.container(border=True):
            st.subheader(f"Posts")
            st.title(f"{len(st.session_state.your_posts) if 'your_posts' in st.session_state else 0} :pencil:")
    with row1[3]:
        with st.container(border=True):
            st.subheader(f"Likes")
            st.title(f"{total_likes} :heart:")
