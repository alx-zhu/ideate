import streamlit as st

from constants import DESCRIPTION_MAX, IDEAS_TABLE, SUMMARY_MAX


@st.experimental_dialog("Edit String", width="large")
def edit_string_dialog(string):
    supabase = st.session_state.supabase
    with st.form(key="edit_string_form"):
        summary = st.text_input(
            "String one-liner", string["summary"], max_chars=SUMMARY_MAX
        )
        description = st.text_area(
            "Describe your string:", string["description"], max_chars=DESCRIPTION_MAX
        )
        submit_button = st.form_submit_button(label="Submit")

    if submit_button:
        if summary and description:
            if supabase.update_string(string["id"], summary, description):
                string["summary"] = summary
                string["description"] = description
                st.success("Your string has been updated!")
                st.rerun()
            else:
                st.error("Error. String could not be updated.")
        else:
            st.error("Please make sure all fields are filled out.")


@st.experimental_dialog("Attach String", width="large")
def attach_string_dialog(string):
    supabase = st.session_state.supabase
    idea_ids_in_string = set([idea["id"] for idea in string[IDEAS_TABLE]])
    with st.form(key="attach_string_form", border=0):
        to_remove = []
        with st.expander("Detach Ideas from this String"):
            for idea in string[IDEAS_TABLE]:
                if not st.checkbox(
                    idea["summary"],
                    key=f"remove_idea{idea['id']}",
                    value=True,
                    help="Uncheck to detach this idea.",
                ):
                    to_remove.append(idea["id"])
        to_add_pairs = []
        with st.expander("Select ideas to attach to this String"):
            can_attach = [
                idea
                for idea in st.session_state.ideas
                if idea["id"] not in idea_ids_in_string
            ]
            for idea in can_attach:
                if st.checkbox(idea["summary"], key=f"idea{idea['id']}"):
                    to_add_pairs.append((idea["id"], idea))
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
        if to_add_pairs:
            if supabase.add_ideas_to_string(
                string["id"], [idea_id for (idea_id, _) in to_add_pairs]
            ):
                st.success("Ideas attached successfully")
                for _, idea in to_add_pairs:
                    string[IDEAS_TABLE].append(idea)
            else:
                st.error(
                    "Error. Ideas could not be attached. Idea changes were not saved."
                )

        if to_remove:
            if supabase.remove_ideas_from_string(string["id"], to_remove):
                st.success("Ideas detached successfully")
                to_remove = set(to_remove)
                string[IDEAS_TABLE] = [
                    idea for idea in string[IDEAS_TABLE] if idea["id"] not in to_remove
                ]
            else:
                st.error("Error. Ideas could not be detached.")
        st.rerun()


@st.experimental_dialog("Add New String", width="large")
def new_string_dialog():
    supabase = st.session_state.supabase
    to_add_pairs = []
    with st.form(key="string_form"):
        summary = st.text_input("String one-liner", max_chars=SUMMARY_MAX)
        description = st.text_area("Describe your string:", max_chars=DESCRIPTION_MAX)
        with st.expander("Select ideas to attach to this String"):
            for idea in st.session_state.ideas:
                if st.checkbox(idea["summary"], key=f"idea{idea['id']}"):
                    to_add_pairs.append((idea["id"], idea))
        submit_button = st.form_submit_button(label="Submit")

    # Add the new string to the session state
    if submit_button:
        if summary and description:
            if string := supabase.add_string(summary, description):
                st.success("Your string has been added!")
                st.session_state.strings = [string] + st.session_state.strings
                if supabase.add_ideas_to_string(
                    string["id"], [idea_id for (idea_id, _) in to_add_pairs]
                ):
                    st.success("Ideas attached successfully!")
                    string[IDEAS_TABLE] = [idea for _, idea in to_add_pairs]
                else:
                    st.error("Error. Ideas could not be attached.")
                st.rerun()
            else:
                st.error("Error. String could not be added.")
        else:
            st.error("Please make sure all fields are filled out.")


def strings_page():
    supabase = st.session_state.supabase
    if "strings" not in st.session_state:
        st.session_state.strings = supabase.list_user_strings(st.session_state.user_id)
        for string in st.session_state.strings:
            string[IDEAS_TABLE] = supabase.list_ideas_in_string(string["id"])

    if st.button(
        "New String", key="new_string_button", type="primary", use_container_width=True
    ):
        new_string_dialog()

    for i, string in enumerate(st.session_state.strings):
        l, r = st.columns((5, 1))
        with l:
            st.markdown(f"#### {string['summary']}")
            st.markdown(f"*{string['description']}*")

        with r:
            with st.expander("Options"):
                if st.button("Edit", key=f"edit_string_{i}", use_container_width=True):
                    edit_string_dialog(string)
                # if st.button("Delete", key=f"delete_{i}", use_container_width=True):
                #     delete_dialog(i)
        for idea in string[IDEAS_TABLE]:
            with st.expander(idea["summary"]):
                st.markdown(f"#### {idea['summary']}")
                st.markdown(f"*{idea['description']}*")
                st.markdown(f"*Created: {idea['created_at']}*")
        if st.button(
            "Attach/Detach Ideas", key=f"attach_string_{i}", use_container_width=True
        ):
            attach_string_dialog(string)

        st.divider()
