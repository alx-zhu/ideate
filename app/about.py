import streamlit as st


def about_page():
    st.title("About the Platform")
    st.image("images/string_theories_slide.png", use_column_width=True)
    st.divider()
    l, r = st.columns((1, 2))
    with l:
        st.image("images/profile.jpg", use_column_width=True)
    with r:
        st.markdown(
            "Hi! My name is Alex. As a part of Nights and Weekends by Buildspace, I'm building String Theories to provide aspiring builders like myself a central platform to **build a habit of writing ideas everyday**, and **organize their ideas into 'String Theories'**. \n\n Here, I want to emphasize a focus on generating ideas in volume (not just perfect ideas), connecting key ideas together for inspiration, and sharing ideas for feedback from others. Here are some of my thoughts when it comes to building the platform:"
        )

    with st.expander("Ideas can be anything, not just business ideas or apps."):
        st.markdown(
            "As a software engineer, I often fall into the trap of only writing down ideas that could be turned into an app. In reality, an app could be anything -- a book, a painting, a song, a recipe, a new way of thinking, etc. I want to encourage people to write down any idea that comes to mind, no matter how small or insignificant it may seem."
        )
    with st.expander("Idea quantity is important, not just quality."):
        st.markdown(
            'I want to reinforce the value of the quantity of ideas, not just the quality. For a long time, I was stuck on only trying to find "good" ideas, or ideas that could be turned into a successful business -- safe to say, I came up with very few ideas... \n\n My friend helped me build a habit of writing an idea every day, no matter how stupid it sounded or if someone had already created that idea. I found that this was pivotal in helping me find ideas I actually cared about. I want to bring this habit to more people on a similar journey.'
        )
    with st.expander(
        "Creativity starts at the individual level. Collaboration helps ideas expand."
    ):
        st.markdown(
            "Tons of research has shown that people are actually more creative in ideation when they are able to spend time thinking about ideas on their own before brainstorming with a group. String Theories is a place where ideas start with an individual, and can be shared with others for feedback and iteration."
        )
    with st.expander("Why is it called String Theories?"):
        st.markdown(
            "String Theory is an idea in theoretical physics in which the universe is made up of tiny strings, not particles (like atoms) -- you might've heard of it from the Big Bang Theory show. In my experience, I've found that some of my favorite ideas were directly inspired by a previous idea I wrote down. Sometimes, ideas came from connecting a bunch of previous ideas together. I thought it would be perfect to describe this in terms of 'strings'."
        )
