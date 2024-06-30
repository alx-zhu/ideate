import streamlit as st
from constants import SUMMARY_MAX, DESCRIPTION_MAX


################################################################################
################################### DIALOGS ####################################
################################################################################


@st.experimental_dialog("Edit Idea", width="large")
def edit_idea_dialog(idea):
    with st.form(key="edit_idea_form"):
        new_summary = st.text_input(
            "Idea one-liner", idea["summary"], max_chars=SUMMARY_MAX
        )
        new_description = st.text_area(
            "Describe your idea:", idea["description"], max_chars=DESCRIPTION_MAX
        )
        l, r = st.columns(2)
        with l:
            submit_button = st.form_submit_button(
                "Save",
                use_container_width=True,
                type="primary",
            )
        with r:
            if st.button(
                "Cancel",
                key=f"cancel_idea_edit",
                use_container_width=True,
            ):
                st.rerun()

    if submit_button:
        if new_summary and new_description:
            if st.session_state.supabase.update_idea(
                idea["id"], new_summary, new_description
            ):
                idea["summary"] = new_summary
                idea["description"] = new_description
                st.success("Your idea has been updated!")
                st.rerun()
            else:
                st.error("Error. Idea could not be updated.")
        else:
            st.error("Please make sure all fields are filled out.")


@st.experimental_dialog("Are you sure you want to delete this idea?", width="large")
def delete_dialog(index):
    st.markdown(f'### "{st.session_state.ideas[index]["summary"]}"')
    if st.button(
        "Confirm",
        key=f"confirm_delete_{index}",
        use_container_width=True,
        type="primary",
    ):
        del st.session_state.ideas[index]
        st.rerun()
    if st.button("Cancel", key=f"cancel_delete_{index}", use_container_width=True):
        st.rerun()


@st.experimental_dialog("Add New Idea", width="large")
def new_idea_dialog():
    supabase = st.session_state.supabase
    with st.form(key="idea_form"):
        summary = st.text_input("Idea one-liner", max_chars=SUMMARY_MAX)
        description = st.text_area("Describe your idea:", max_chars=DESCRIPTION_MAX)
        submit_button = st.form_submit_button(label="Submit")

    # Add the new idea to the session state
    if submit_button:
        if summary and description:
            if idea := supabase.add_idea(summary, description):
                idea["edit_mode"] = False
                st.session_state.ideas = [idea] + st.session_state.ideas
                st.success("Your idea has been added!")
                st.rerun()
            else:
                st.error("Error. Idea could not be added.")
        else:
            st.error("Please make sure all fields are filled out.")


@st.experimental_dialog("Share Idea", width="large")
def share_idea_dialog(idea):
    supabase = st.session_state.supabase
    st.divider()
    st.markdown(f"## **Tagline**: {idea['summary']}")
    st.markdown(f"#### **Description**: *{idea['description']}*")
    st.divider()
    l, r = st.columns(2)
    with l:
        if st.button(
            "Posted" if idea["is_posted"] else "Confirm",
            key="confirm_share",
            use_container_width=True,
            type="primary",
            disabled=idea["is_posted"],
        ):
            if supabase.add_post(idea["id"]):
                idea["is_posted"] = True
                st.success("Post shared!")
                st.rerun()
            else:
                st.error("Failed to share post.")
    with r:
        if st.button("Cancel", key="cancel_share", use_container_width=True):
            st.rerun()


################################################################################
################################ IDEATION PAGE #################################
################################################################################


def ideation_page():
    supabase = st.session_state.supabase

    # Initialize session state to store ideas
    if "ideas" not in st.session_state:
        st.session_state.ideas = supabase.list_ideas(st.session_state.user_id)
        for idea in st.session_state.ideas:
            idea["edit_mode"] = False

    # Display all ideas
    if st.button("Add Idea", use_container_width=True, type="primary"):
        new_idea_dialog()

    # st.divider()
    if st.session_state.ideas:
        for i, idea in enumerate(st.session_state.ideas):
            l, r = st.columns((5, 1))
            with l:
                st.markdown(f"#### {idea['summary']}")
                st.markdown(f"*{idea['description']}*")
                st.markdown(f"*Created: {idea['created_at']}*")
            with r:
                if st.button(
                    "Shared!" if idea["is_posted"] else "Share",
                    key=f"share_{i}",
                    use_container_width=True,
                    disabled=idea["is_posted"],
                ):
                    share_idea_dialog(idea)
                with st.expander("Options"):
                    if st.button(
                        "Edit",
                        key=f"edit_{i}",
                        use_container_width=True,
                    ):
                        edit_idea_dialog(idea)
                    # if st.button("Delete", key=f"delete_{i}", use_container_width=True):
                    #     delete_dialog(i)
            st.divider()

    else:
        st.write("No ideas yet. Start adding your ideas!")
