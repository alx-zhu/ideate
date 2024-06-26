import streamlit as st
from datetime import date
from supabase_helpers import list_ideas, add_idea

SUMMARY_MAX = 75
DESCRIPTION_MAX = 500

# Function to enable edit mode
def enable_edit_mode(index):
    st.session_state.edit_mode[index] = True


# Function to disable edit mode
def disable_edit_mode(index):
    st.session_state.edit_mode[index] = False

# Function to save the edited idea
def save_idea(index, new_summary, new_description):
    st.session_state.ideas[index]["summary"] = new_summary
    st.session_state.ideas[index]["description"] = new_description
    st.session_state.edit_mode[index] = False
    st.success(f"Idea {index + 1} has been updated!")

@st.experimental_dialog("Are you sure you want to delete this idea?")
def delete_dialog(index):
    st.markdown(f'### "{st.session_state.ideas[index]["summary"]}"')
    if st.button("Confirm", key=f"confirm_delete_{index}", use_container_width=True, type="primary"):
        del st.session_state.ideas[index]
        st.rerun()
    if st.button("Cancel", key=f"cancel_delete_{index}", use_container_width=True):
        st.rerun()


def ideation_page():
    # Initialize session state to store ideas
    if "ideas" not in st.session_state:
        st.session_state.ideas = list_ideas(st.session_state.user_id)

    if "edit_mode" not in st.session_state:
        st.session_state.edit_mode = [False] * len(st.session_state.ideas)

    with st.sidebar:
        if st.button("Logout"):
            del st.session_state.user_id
            st.rerun()

    # Page title
    st.title("IDEATE")

    # Input form for new ideas
    st.header("Add a New Idea")
    with st.form(key="idea_form", clear_on_submit=True):
        summary = st.text_input("Idea one-liner", max_chars=SUMMARY_MAX)
        description = st.text_area("Describe your idea:", max_chars=DESCRIPTION_MAX)
        submit_button = st.form_submit_button(label="Submit")

    # Add the new idea to the session state
    if submit_button:
        if summary and description:
            if idea := add_idea(summary, description):
                st.session_state.ideas.append(idea)
                st.session_state.edit_mode.append(False)
                st.success("Your idea has been added!")
            else:
                st.error("Error. Idea could not be added.")
        else:
            st.error("Please make sure all fields are filled out.")

    
    # Display all ideas with edit options
    st.header("Your Ideas")
    if st.session_state.ideas:
        for i, idea in enumerate(st.session_state.ideas):
            with st.container(border=True):
                if st.session_state.edit_mode[i]:
                    new_summary = st.text_input(f"Edit summary", value=idea["summary"], key=f"edit_{i}_sum", max_chars=SUMMARY_MAX)
                    new_description = st.text_area(f"Edit description", value=idea["description"], key=f"edit_{i}_desc", max_chars=DESCRIPTION_MAX)
                    l, r = st.columns(2)
                    with l:
                        st.button("Save", on_click=save_idea, args=(i, new_summary, new_description), key=f"save_{i}", use_container_width=True)
                    with r:
                        st.button(
                            "Cancel", on_click=disable_edit_mode, args=(i,), key=f"cancel_{i}", use_container_width=True
                        )
                else:
                    l, r = st.columns((6, 1))
                    with l:
                        st.subheader(f"{idea["summary"]}")
                        st.markdown(f"###### {idea["description"]}")
                        st.markdown(f"*Created: {idea["created_at"]}*")
                    with r:
                        st.button("Edit", on_click=enable_edit_mode, args=(i,), key=f"edit_{i}", use_container_width=True)
                        if st.button("Delete", key=f"delete_{i}", use_container_width=True):
                            delete_dialog(i)                                
                            
    else:
        st.write("No ideas yet. Start adding your ideas!")
