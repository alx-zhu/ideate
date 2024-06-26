import streamlit as st
from ideate import ideation_page
from authentication import authentication_page

if __name__ == "__main__":
    if "user_id" in st.session_state and st.session_state.user_id:
        print(st.session_state.user_id)
        ideation_page()
    else:
        authentication_page()
