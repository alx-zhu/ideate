from collections import defaultdict
import datetime
import streamlit as st
from app.constants import (
    CONNECTIONS_TABLE,
    SUMMARY_MAX,
    DESCRIPTION_MAX,
    THOUGHT_TYPES,
    pick_type_icon,
)
from app.supabase_client import SupabaseClient
from app.chat_client import OpenAIChat
from streamlit_mic_recorder import speech_to_text


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
        submit_button = st.form_submit_button(label="Submit")

    # Add the new thought to the session state
    if submit_button:
        if summary and description:
            if thought := supabase.add_thought(summary, description, new_type):
                st.session_state.thoughts = [thought] + st.session_state.thoughts
                st.session_state.thought_map[thought["id"]] = thought
                thought[CONNECTIONS_TABLE] = []
                st.success("Your thought has been added!")
                st.rerun()
            else:
                st.error("Error. Thought could not be added.")
        else:
            st.error("Please make sure all fields are filled out.")


@st.experimental_dialog("Edit Thoughts", width="large")
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
            # max_chars=DESCRIPTION_MAX,
            help="Describe your thought in a bit more detail, but not too much! Make sure to keep it concise.",
        )
        submit_button = st.form_submit_button(
            "Save",
            use_container_width=True,
        )

    if submit_button:
        if new_summary and new_description:
            if st.session_state.supabase.update_thought(
                thought,
                new_summary,
                new_description,
                new_type,
            ):
                thought["summary"] = new_summary
                thought["description"] = new_description
                thought["type"] = new_type
                thought["interactions"] += 1
                st.success("Your thought has been updated!")
                st.rerun()
            else:
                st.error("Error. Thoughts could not be updated.")
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


@st.experimental_dialog("Share Thoughts", width="large")
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


@st.experimental_dialog("Connect/Disconnect Thoughts", width="large")
def connect_thoughts_dialog(curr_thought):
    supabase: SupabaseClient = st.session_state.supabase
    connected_thoughts = curr_thought.get(CONNECTIONS_TABLE, [])
    st.markdown(f"#### _{curr_thought['summary']}_")
    with st.form(key="connect_thoughts_form", border=0):
        to_remove = []
        with st.expander("Disconnect thoughts"):
            if not connected_thoughts:
                st.markdown("_No connected thoughts._")
            for thought_id in connected_thoughts:
                info = st.session_state.thought_map[thought_id]
                if not st.checkbox(
                    info["summary"],
                    key=f"remove_thought{thought_id}",
                    value=True,
                    help="Uncheck to disconnect this thought.",
                ):
                    to_remove.append(thought_id)
        to_add = []
        with st.expander("Connect thoughts"):
            can_connect = [
                thought
                for thought in st.session_state.thoughts
                if thought["id"] != curr_thought["id"]
                and thought not in connected_thoughts
            ]
            if not can_connect:
                st.markdown("_No thoughts to connect._")
            for thought in can_connect:
                # if (
                #     thought["id"] != thought["id"]
                #     and thought["id"] not in connected_thoughts
                # ):
                if st.checkbox(
                    thought["summary"],
                    key=f"thought{thought['id']}",
                    help="Check to connect this thought.",
                ):
                    to_add.append(thought["id"])
        submit_button = st.form_submit_button("Save", use_container_width=True)
    if submit_button:
        if to_add:
            if supabase.connect_many_thoughts(curr_thought["id"], to_add):
                st.success("Thoughts connected successfully")
                curr_thought[CONNECTIONS_TABLE] += to_add
            else:
                st.error("Error. Thoughts could not be connected.")
        if to_remove:
            if supabase.disconnect_many_thoughts(curr_thought["id"], to_remove):
                st.success("Thoughts disconnected successfully")
                curr_thought[CONNECTIONS_TABLE] = [
                    thought_id
                    for thought_id in curr_thought.get(CONNECTIONS_TABLE, [])
                    if thought_id not in to_remove
                ]
            else:
                st.error("Error. Thoughts could not be disconnected.")
        st.rerun()


@st.experimental_dialog("Think Out Loud", width="large")
def think_out_loud_dialog():
    st.markdown(
        "### Just write down or record your stream of consciousness, and we'll help you organize it into thoughts!"
    )
    transcribed = speech_to_text(
        language="en",
        start_prompt="🔴 Record Audio",
        stop_prompt="🛑 Stop Recording",
        just_once=False,
        use_container_width=False,
        callback=None,
        key="thought_recording",
    )
    with st.form(key="thought_form"):
        thought_text = st.text_area(
            "Your thoughts:", value=transcribed if transcribed else ""
        )
        submit_button = st.form_submit_button("Submit")
    if submit_button:
        if thought_text:
            st.session_state.chat.summarize_thought(thought_text)
            st.success("Your thoughts have been organized!")
            st.rerun()
        else:
            st.error("Please make sure all fields are filled out.")


################################################################################
################################ IDEATION PAGE #################################
################################################################################


def extract_date(date_string):
    parsed_timestamp = datetime.datetime.fromisoformat(date_string)
    return parsed_timestamp.strftime("%B %d, %Y")


def sort_thoughts_by_date():
    thoughts_by_date = defaultdict(list)
    for thought in st.session_state.thoughts:
        date = datetime.datetime.fromisoformat((thought["created_at"])).date()
        thoughts_by_date[date].append(thought)

    return thoughts_by_date


def thought_page():
    supabase: SupabaseClient = st.session_state.supabase
    chat: OpenAIChat = st.session_state.chat

    # Initialize session state to store thoughts
    if "thoughts" not in st.session_state:
        st.session_state.thoughts = supabase.list_thoughts(st.session_state.user_id)

    button_l, button_r, button_edge = st.columns((5, 5, 1))

    with button_l:
        # Display all thoughts
        if st.button("Add a Thought", use_container_width=True, type="primary"):
            new_thought_dialog()

    with button_r:
        if st.button("Think Out Loud", use_container_width=True, type="primary"):
            think_out_loud_dialog()

    with button_edge:
        if st.button(
            "💬",
            use_container_width=True,
            type="primary",
            help="Have an open-ended conversation with the AI.",
        ):
            chat.initialize_general_chat()
            chat.open_chat()

    # st.divider()
    if st.session_state.thoughts:
        thoughts_by_date = sort_thoughts_by_date()
        count = 0
        for date in sorted(thoughts_by_date.keys(), reverse=True):
            st.header(date.strftime("%B %d, %Y"))
            for i, thought in enumerate(thoughts_by_date[date], start=count):
                thought_component(i, thought)

            count += len(thoughts_by_date[date])

    else:
        st.write("No thoughts yet. Start adding your thoughts!")


def thought_component(i, thought, key=""):
    chat: OpenAIChat = st.session_state.chat
    l, r = st.columns((10, 1))
    with l:
        with st.expander(f"{pick_type_icon(thought['type'])} {thought['summary']}"):
            l1, edit, delete = st.columns((5, 1, 1))
            with l1:
                st.markdown(f"#### **_[{extract_date(thought['created_at'])}]_**")
            with edit:
                if st.button(
                    "Edit",
                    key=f"{key}_edit_{i}",
                    use_container_width=True,
                ):
                    edit_thought_dialog(thought)
            with delete:
                if st.button(
                    "Delete",
                    key=f"{key}_delete_{i}",
                    use_container_width=True,
                ):
                    delete_dialog(i)
            st.markdown(f"{thought['description']}")

            # if st.button(
            #     "Connect to Other Thoughts",
            #     key=f"connect_{i}",
            #     use_container_width=True,
            # ):
            #     connect_thoughts_dialog(thought)
            # l, r = st.columns(2)
            # with l:
            #
            # with r:
    with r:
        if st.button(
            "💬",
            key=f"{key}_chat_{i}",
            use_container_width=True,
            help="Explore this thought in an AI chat!",
        ):
            chat.initialize_thought_chat(thought)
            chat.open_chat()
