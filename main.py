import streamlit as st
from home import home_page
from your_ideas import ideation_page
from authentication import authentication_page
from feed import feed_page

if __name__ == "__main__":
    if "user_id" in st.session_state and st.session_state.user_id:
        print(st.session_state.user_id)
        home_page()
        # if "feed" not in st.session_state:
        #     st.session_state.feed = False

        # if st.session_state.feed:
        #     feed_page()
        # else:
        #     ideation_page()
    else:
        authentication_page()
