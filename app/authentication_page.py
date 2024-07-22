import streamlit as st
from app.authentication_components import login_component, sign_up_component
from demo.demo import demo_page


def authentication_page():
    # st.info(
    #     "Hi! Welcome to String Theories! This is my first prototype, so I'd love to hear your feedback. Please feel free to reach out to me at alexanderzhu07 [at] gmail [dot] com. Thanks for checking it out!\n\n I'd love to connect!\n - [LinkedIn](https://www.linkedin.com/in/zhu-alexander/),\n - [Github](https://github.com/alx-zhu),\n - Email: alexanderzhu07 [at] gmail [dot] com."
    # )
    st.warning(
        "Please note: thoughts created in the demo do not persist between sessions and are not saved to the database. Sign up to create your account and save your thoughts!"
    )
    [try_it, login, signup] = st.tabs(["Try it Out", "Login", "Sign Up"])

    with try_it:
        demo_page()

    with login:
        login_component()

    with signup:
        sign_up_component()
