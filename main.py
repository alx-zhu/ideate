import streamlit as st
from home import home_page
from authentication import authentication_page
from supabase_helpers import login_user

if __name__ == "__main__":
    # FOR TESTING
    # user = login_user(st.secrets["EMAIL"], st.secrets["PW"])
    # st.session_state.user_id = user.user.id
    if "user_id" in st.session_state and st.session_state.user_id:
        home_page()
    else:
        authentication_page()
