import streamlit as st
from app.constants import DESCRIPTION_MAX, THOUGHTS_TABLE, SUMMARY_MAX
from app.supabase_client import SupabaseClient


@st.experimental_dialog("Edit Topic", width="large")
def edit_topic_dialog(topic):
    supabase: SupabaseClient = st.session_state.supabase
    with st.form(key="edit_topic_form"):
        summary = st.text_input(
            "Topic one-liner", topic["summary"], max_chars=SUMMARY_MAX
        )
        description = st.text_area(
            "Describe your topic:", topic["description"], max_chars=DESCRIPTION_MAX
        )
        submit_button = st.form_submit_button(label="Submit")

    if submit_button:
        if summary and description:
            if supabase.update_topic(topic["id"], summary, description):
                topic["summary"] = summary
                topic["description"] = description
                st.success("Your topic has been updated!")
                st.rerun()
            else:
                st.error("Error. Topic could not be updated.")
        else:
            st.error("Please make sure all fields are filled out.")


@st.experimental_dialog("Attach Topic", width="large")
def attach_topic_dialog(topic):
    supabase: SupabaseClient = st.session_state.supabase
    thought_ids_in_topic = set([thought["id"] for thought in topic[THOUGHTS_TABLE]])
    with st.form(key="attach_topic_form", border=0):
        to_remove = []
        with st.expander("Detach Thoughts from this Topic", expanded=True):
            for thought in topic[THOUGHTS_TABLE]:
                if not st.checkbox(
                    thought["summary"],
                    key=f"remove_thought{thought['id']}",
                    value=True,
                    help="Uncheck to detach this thought.",
                ):
                    to_remove.append(thought["id"])
        to_add_pairs = []
        with st.expander("Select thoughts to attach to this Topic", expanded=True):
            can_attach = [
                thought
                for thought in st.session_state.thoughts
                if thought["id"] not in thought_ids_in_topic
            ]
            for thought in can_attach:
                if st.checkbox(thought["summary"], key=f"thought{thought['id']}"):
                    to_add_pairs.append((thought["id"], thought))
        submit_button = st.form_submit_button(
            "Save",
            use_container_width=True,
        )

    if submit_button:
        if to_add_pairs:
            if supabase.add_many_thoughts_to_topic(
                topic["id"], [thought_id for (thought_id, _) in to_add_pairs]
            ):
                st.success("Thoughts attached successfully")
                for _, thought in to_add_pairs:
                    topic[THOUGHTS_TABLE].append(thought)
            else:
                st.error(
                    "Error. Thoughts could not be attached. Thought changes were not saved."
                )

        if to_remove:
            if supabase.remove_thoughts_from_topic(topic["id"], to_remove):
                st.success("Thoughts detached successfully")
                to_remove = set(to_remove)
                topic[THOUGHTS_TABLE] = [
                    thought
                    for thought in topic[THOUGHTS_TABLE]
                    if thought["id"] not in to_remove
                ]
            else:
                st.error("Error. Thoughts could not be detached.")
        st.rerun()


@st.experimental_dialog("Add New Topic", width="large")
def new_topic_dialog():
    supabase: SupabaseClient = st.session_state.supabase
    to_add_pairs = []
    with st.form(key="topic_form"):
        summary = st.text_input("Topic one-liner", max_chars=SUMMARY_MAX)
        description = st.text_area("Describe your topic:", max_chars=DESCRIPTION_MAX)
        with st.expander("Select thoughts to attach to this Topic", expanded=True):
            for thought in st.session_state.thoughts:
                if st.checkbox(thought["summary"], key=f"thought{thought['id']}"):
                    to_add_pairs.append((thought["id"], thought))
        submit_button = st.form_submit_button(label="Submit")

    # Add the new topic to the session state
    if submit_button:
        if summary and description:
            if topic := supabase.add_topic(summary, description):
                st.success("Your topic has been added!")
                st.session_state.topics = [topic] + st.session_state.topics
                if len(to_add_pairs) == 0:
                    topic[THOUGHTS_TABLE] = []
                elif supabase.add_many_thoughts_to_topic(
                    topic["id"], [thought_id for (thought_id, _) in to_add_pairs]
                ):
                    st.success("Thoughts attached successfully!")
                    topic[THOUGHTS_TABLE] = [thought for _, thought in to_add_pairs]
                else:
                    st.error("Error. Thoughts could not be attached.")
                st.rerun()
            else:
                st.error("Error. Topic could not be added.")
        else:
            st.error("Please make sure all fields are filled out.")


def topics_page():
    supabase: SupabaseClient = st.session_state.supabase
    if "topics" not in st.session_state:
        st.session_state.topics = supabase.list_user_topics(st.session_state.user_id)
        for topic in st.session_state.topics:
            topic[THOUGHTS_TABLE] = supabase.list_thoughts_in_topic(topic["id"])

    if st.button(
        "New Topic", key="new_topic_button", type="primary", use_container_width=True
    ):
        new_topic_dialog()

    for i, topic in enumerate(st.session_state.topics):
        l, r = st.columns((5, 1))
        with l:
            st.markdown(f"#### {topic['summary']}")
            st.markdown(f"*{topic['description']}*")

        with r:
            with st.expander("Options"):
                if st.button("Edit", key=f"edit_topic_{i}", use_container_width=True):
                    edit_topic_dialog(topic)
                # if st.button("Delete", key=f"delete_{i}", use_container_width=True):
                #     delete_dialog(i)
        for thought in topic[THOUGHTS_TABLE]:
            with st.expander(thought["summary"]):
                st.markdown(f"#### {thought['summary']}")
                st.markdown(f"*{thought['description']}*")
                st.markdown(f"*Created: {thought['created_at']}*")
        if st.button(
            "Attach/Detach Thoughts", key=f"attach_topic_{i}", use_container_width=True
        ):
            attach_topic_dialog(topic)

        st.divider()
