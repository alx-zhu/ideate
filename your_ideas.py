import streamlit as st
from supabase_helpers import list_ideas, add_idea, add_post, update_idea
from constants import SUMMARY_MAX, DESCRIPTION_MAX

################################################################################
################################# EDIT HELPERS #################################
################################################################################

# Function to enable edit mode
def enable_edit_mode(index):
    st.session_state.ideas[index]["edit_mode"] = True


# Function to disable edit mode
def disable_edit_mode(index):
    st.session_state.ideas[index]["edit_mode"] = False


# Function to save the edited idea
def save_idea(index, new_summary, new_description):
    if update_idea(st.session_state.ideas[index]["id"], new_summary, new_description):
        st.session_state.ideas[index]["summary"] = new_summary
        st.session_state.ideas[index]["description"] = new_description
        disable_edit_mode(index)
        st.success(f"Idea {index + 1} has been updated!")
    else:
        st.error(f"Idea {index + 1} failed to be updated.")

################################################################################
################################### DIALOGS ####################################
################################################################################

@st.experimental_dialog("Are you sure you want to delete this idea?")
def delete_dialog(index):
    st.markdown(f'### "{st.session_state.ideas[index]["summary"]}"')
    if st.button("Confirm", key=f"confirm_delete_{index}", use_container_width=True, type="primary"):
        del st.session_state.ideas[index]
        st.rerun()
    if st.button("Cancel", key=f"cancel_delete_{index}", use_container_width=True):
        st.rerun()


@st.experimental_dialog("Add New Idea")
def new_idea_dialog():
    with st.form(key="idea_form", clear_on_submit=True):
        summary = st.text_input("Idea one-liner", max_chars=SUMMARY_MAX)
        description = st.text_area("Describe your idea:", max_chars=DESCRIPTION_MAX)
        submit_button = st.form_submit_button(label="Submit")

    # Add the new idea to the session state
    if submit_button:
        if summary and description:
            if idea := add_idea(summary, description):
                idea["edit_mode"] = False
                st.session_state.ideas = [idea] + st.session_state.ideas
                st.success("Your idea has been added!")
                st.rerun()
            else:
                st.error("Error. Idea could not be added.")
        else:
            st.error("Please make sure all fields are filled out.")

@st.experimental_dialog("Share Idea")
def share_idea_dialog(idea):
    st.markdown(f"#### {idea["summary"]}")
    st.markdown(f"*{idea["description"]}*")
    st.divider()
    if st.button("Posted" if idea["is_posted"] else "Confirm", key="confirm_share", use_container_width=True, type="primary", disabled=idea["is_posted"]):
        if add_post(idea["id"]):
            idea["is_posted"] = True
            st.success("Post shared!")
            st.rerun()
        else:
            st.error("Failed to share post.")
    if st.button("Cancel", key="cancel_share", use_container_width=True):
        st.rerun()

################################################################################
################################ IDEATION PAGE #################################
################################################################################

def ideation_page():
    # Initialize session state to store ideas
    if "ideas" not in st.session_state:
        st.session_state.ideas = list_ideas(st.session_state.user_id)
        for idea in st.session_state.ideas:
            idea["edit_mode"] = False

    with st.sidebar:
        if st.button("Logout"):
            st.session_state.user_id = ""
            st.rerun()
        if st.button("Feed"):
            st.session_state.feed = True
            st.rerun()
    
    # Display all ideas
    st.header("Your Ideas")
    if st.button("Add Idea", use_container_width=True, type="primary"):
        new_idea_dialog()

    st.divider()
    if st.session_state.ideas:
        for i, idea in enumerate(st.session_state.ideas):
            if idea["edit_mode"]:
                new_summary = st.text_input(f"Edit summary", value=idea["summary"], key=f"edit_{i}_sum", max_chars=SUMMARY_MAX)
                new_description = st.text_area(f"Edit description", value=idea["description"], key=f"edit_{i}_desc", max_chars=DESCRIPTION_MAX)
                l, r = st.columns(2)
                with l:
                    st.button("Save", on_click=save_idea, args=(i, new_summary, new_description), key=f"save_{i}", use_container_width=True, type="primary")
                with r:
                    st.button(
                        "Cancel", on_click=disable_edit_mode, args=(i,), key=f"cancel_{i}", use_container_width=True
                    )
            else:
                l, r = st.columns((5, 1))
                with l:
                    st.markdown(f"#### {idea["summary"]}")
                    st.markdown(f"*{idea["description"]}*")
                    st.markdown(f"*Created: {idea["created_at"]}*")
                with r:
                    if st.button("Shared!" if idea["is_posted"] else "Share", key=f"share_{i}", use_container_width=True, disabled=idea["is_posted"]):
                            share_idea_dialog(idea)
                    with st.expander("Options"):
                        st.button("Edit", on_click=enable_edit_mode, args=(i,), key=f"edit_{i}", use_container_width=True)
                        # if st.button("Delete", key=f"delete_{i}", use_container_width=True):
                        #     delete_dialog(i)
            st.divider()                          
                            
    else:
        st.write("No ideas yet. Start adding your ideas!")
