import streamlit as st
from constants import SUMMARY_MAX, DESCRIPTION_MAX, THOUGHT_TYPES, pick_type_icon
from supabase_client import SupabaseClient


################################################################################
################################### DIALOGS ####################################
################################################################################

@st.experimental_dialog("Add New Thought", width="large")
def new_thought_dialog():
    supabase: SupabaseClient = st.session_state.supabase
    with st.form(key="thought_form"):
        new_type = st.selectbox(
            "Type",
            THOUGHT_TYPES,
            index=0,
            key="new_type_select",
        )
        summary = st.text_input("Thought one-liner", max_chars=SUMMARY_MAX)
        description = st.text_area("Describe your thought:", max_chars=DESCRIPTION_MAX)
        to_attach = []
        with st.expander("Attach to a String", expanded=True):
            for string in st.session_state.strings:
                if st.checkbox(string["summary"]):
                    to_attach.append(string["id"])
        submit_button = st.form_submit_button(label="Submit")

    # Add the new thought to the session state
    if submit_button:
        if summary and description:
            if thought := supabase.add_thought(summary, description, new_type):
                thought["edit_mode"] = False
                st.session_state.thoughts = [thought] + st.session_state.thoughts
                st.success("Your thought has been added!")
                if to_attach:
                    if supabase.add_thought_to_many_strings(thought["id"], to_attach):
                        st.success("Idea attached to Strings.")
                    else:
                        st.error("Error. Idea could not be attached.")
                st.rerun()
            else:
                st.error("Error. Idea could not be added.")
        else:
            st.error("Please make sure all fields are filled out.")

@st.experimental_dialog("Edit Idea", width="large")
def edit_thought_dialog(thought):
    with st.form(key="edit_thought_form"):
        new_type = st.selectbox(
            "Type",
            THOUGHT_TYPES,
            index=THOUGHT_TYPES.index(thought["type"]),
        )
        new_summary = st.text_input(
            "Give your thought a one-line introduction:",
            thought["summary"],
            max_chars=SUMMARY_MAX,
            help="The thought one-liner should help someone immediately understand what your thought is about without too much detail!",
        )
        new_description = st.text_area(
            "Describe some details about your thought:",
            thought["description"],
            max_chars=DESCRIPTION_MAX,
            help="Describe your thought in a bit more detail, but not too much! Make sure to keep it concise.",
        )
        submit_button = st.form_submit_button(
            "Save",
            use_container_width=True,
        )

    if submit_button:
        if new_summary and new_description:
            if st.session_state.supabase.update_thought(
                thought["id"], new_summary, new_description, new_type
            ):
                thought["summary"] = new_summary
                thought["description"] = new_description
                thought["type"] = new_type
                st.success("Your thought has been updated!")
                st.rerun()
            else:
                st.error("Error. Idea could not be updated.")
        else:
            st.error("Please make sure all fields are filled out.")


@st.experimental_dialog("Are you sure you want to delete this thought?", width="large")
def delete_dialog(index):
    st.markdown(f'### "{st.session_state.thoughts[index]["summary"]}"')
    if st.button(
        "Confirm",
        key=f"confirm_delete_{index}",
        use_container_width=True,
        type="primary",
    ):
        del st.session_state.thoughts[index]
        st.rerun()
    if st.button("Cancel", key=f"cancel_delete_{index}", use_container_width=True):
        st.rerun()


@st.experimental_dialog("Share Idea", width="large")
def share_thought_dialog(thought):
    supabase: SupabaseClient = st.session_state.supabase
    st.divider()
    st.markdown(f"## **Tagline**: {thought['summary']}")
    st.markdown(f"#### **Description**: *{thought['description']}*")
    st.divider()
    l, r = st.columns(2)
    with l:
        if st.button(
            "Posted" if thought["is_posted"] else "Confirm",
            key="confirm_share",
            use_container_width=True,
            type="primary",
            disabled=thought["is_posted"],
        ):
            if supabase.add_post(thought["id"]):
                thought["is_posted"] = True
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


def thought_page():
    supabase: SupabaseClient = st.session_state.supabase

    # Initialize session state to store thoughts
    if "thoughts" not in st.session_state:
        st.session_state.thoughts = supabase.list_thoughts(st.session_state.user_id)
        for thought in st.session_state.thoughts:
            thought["edit_mode"] = False

    # Display all thoughts
    if st.button("Add Idea", use_container_width=True, type="primary"):
        new_thought_dialog()

    # st.divider()
    if st.session_state.thoughts:
        for i, thought in enumerate(st.session_state.thoughts):
            l, r = st.columns((5, 1))
            with l:
                st.markdown(f"#### {pick_type_icon(thought["type"])} {thought['summary']}")
                st.markdown(f"*{thought['description']}*")
                st.markdown(f"*Created: {thought['created_at']}*")
            with r:
                if st.button(
                    "Shared!" if thought["is_posted"] else "Share",
                    key=f"share_{i}",
                    use_container_width=True,
                    disabled=thought["is_posted"],
                ):
                    share_thought_dialog(thought)
                with st.expander("Options"):
                    if st.button(
                        "Edit",
                        key=f"edit_{i}",
                        use_container_width=True,
                    ):
                        edit_thought_dialog(thought)
                    # if st.button("Delete", key=f"delete_{i}", use_container_width=True):
                    #     delete_dialog(i)
            st.divider()

    else:
        st.write("No thoughts yet. Start adding your thoughts!")
