import streamlit as st

from thought_graph import ThoughtGraph


def graph_page():
    if "thought_graph" not in st.session_state:
        st.session_state.thought_graph = ThoughtGraph(
            st.session_state.thoughts, st.session_state.topics
        )
    graph_container = st.container()
    st.session_state.plot = st.session_state.thought_graph.create_plot()

    with graph_container:
        st.plotly_chart(st.session_state.plot)

    if st.button("Refresh Graph"):
        st.session_state.thought_graph.refresh_graph(
            st.session_state.thoughts, st.session_state.topics
        )
        st.session_state.plot = st.session_state.thought_graph.create_plot()
