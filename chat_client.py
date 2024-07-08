import json
import time
import streamlit as st
from openai import OpenAI
from constants import OPENAI_INITIAL_CONVERSATION
from supabase_client import SupabaseClient
from constants import DESCRIPTION_MAX, SUMMARY_MAX, THOUGHT_TYPES, CHAT_WELCOME_MESSAGE


@st.cache_resource()
def get_cached_open_ai_client():
    return OpenAI(api_key=st.secrets["OPENAI_API_KEY"])


class OpenAIChat(object):
    def __init__(self, thought=None):
        self.open_ai = get_cached_open_ai_client()
        self.gpt_conversation = []
        self.display_conversation = []
        self.message_count = 0
        if thought:
            self.initialize_thought_chat(thought)
        else:
            self.initialize_general_chat()

    def initialize_general_chat(self):
        self.thought = None
        self.gpt_conversation = OPENAI_INITIAL_CONVERSATION
        self.display_conversation = []
        self.gpt_conversation.append(
            {"role": "assistant", "content": CHAT_WELCOME_MESSAGE}
        )
        self.display_conversation.append(
            {"role": "assistant", "content": CHAT_WELCOME_MESSAGE}
        )

    def initialize_thought_chat(self, thought):
        self.thought = thought
        self.gpt_conversation = OPENAI_INITIAL_CONVERSATION
        self.display_conversation = []
        initial_prompt = f"Great! Let's have a conversation about your {thought['type']}:\n*{thought['summary']}*\n\n How would you like to start?"
        additional_info = f"The user wants to discuss the following {thought['type']}: \n\n Summary: {thought['summary']} \n\n Description: {thought['description']}"
        self.gpt_conversation.append(
            {
                "role": "system",
                "content": additional_info,
            }
        )

        self.gpt_conversation.append(
            {
                "role": "assistant",
                "content": initial_prompt,
            }
        )
        self.display_conversation.append(
            {"role": "assistant", "content": initial_prompt}
        )

    def open_chat(self):
        st.session_state.chat_open = True
        st.rerun()

    @st.experimental_dialog("Save as Thought", width="large")
    def save_thought_dialog(self, chat_message):
        supabase: SupabaseClient = st.session_state.supabase
        # with st.expander("Message to Save"):
        #     st.chat_message(chat_message["role"]).markdown(chat_message["content"])
        # st.divider()
        with st.form(key="thought_form"):
            new_type = st.selectbox(
                "Type",
                THOUGHT_TYPES,
                index=0,
                key="new_type_select",
            )
            summary = st.text_input("Thought one-liner", max_chars=SUMMARY_MAX)
            description = st.text_area(
                "Describe your thought:",
                # max_chars=DESCRIPTION_MAX,
                value=chat_message["content"],
            )
            submit_button = st.form_submit_button(label="Submit")

        # Add the new thought to the session state
        if submit_button:
            if summary and description:
                if thought := supabase.add_thought(summary, description, new_type):
                    st.session_state.thoughts = [thought] + st.session_state.thoughts
                    st.session_state.thought_map[thought["id"]] = thought
                    st.success("Your thought has been added!")
                    if self.thought:
                        if supabase.connect_thought(self.thought["id"], thought["id"]):
                            st.success("Connected thought to parent thought.")
                        else:
                            st.error("Error. Thought could not be connected.")
                    st.rerun()
                else:
                    st.error("Error. Thought could not be added.")
            else:
                st.error("Please make sure all fields are filled out.")

    def save_thought_with_ai(self, chat_message):
        supabase = st.session_state.supabase
        completion = self.open_ai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "Give me a 100 character length title of this thought designed to give as much information as possible as a title on a sticky note. The user should understand exactly what the text is about from reading only the title. It must be 100 characters or less. Don't add quotation marks.",
                },
                {
                    "role": "user",
                    "content": chat_message["content"],
                },
            ],
        )

        summary = completion.choices[0].message.content
        if thought := supabase.add_thought(
            summary, chat_message["content"], "undefined"
        ):
            st.session_state.thoughts = [thought] + st.session_state.thoughts
            st.session_state.thought_map[thought["id"]] = thought
            st.success("Your thought has been added!")
        else:
            st.error("Error. Thought could not be added.")

    def chat_page(self):
        if not self.gpt_conversation or not self.display_conversation:
            st.error("Chat not initialized.")
            return

        for i, message in enumerate(self.display_conversation):
            l, r = st.columns((10, 1))
            with l:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
            with r:
                if st.button(
                    "💾", key=f"save_{i}", help="Save this message as a thought!"
                ):
                    self.save_thought_dialog(message)

        l, r = st.columns((10, 1))
        with l:
            user_placeholder = st.empty()
        with r:
            user_save_button_placeholder = st.empty()

        l1, r1 = st.columns((10, 1))
        with l1:
            assistant_placeholder = st.empty()
        with r1:
            assistant_save_button_placeholder = st.empty()

        # React to user input
        if self.message_count > 10:
            st.warning(
                "You have passed your limit of 10 messages. In order to keep this service free, there is a 10 message limit per user. Please contact alexanderzhu07@gmail.com with any questions."
            )

        else:
            if prompt := st.chat_input(f"Prompt!", max_chars=500, key=f"chat_input"):
                self.message_count += 1

                with user_placeholder:
                    st.chat_message("user").markdown(prompt)

                self.display_conversation.append({"role": "user", "content": prompt})
                self.gpt_conversation.append({"role": "user", "content": prompt})

                with assistant_placeholder:
                    with st.chat_message("assistant"):
                        with st.spinner("Thinking..."):
                            # Send message to Open AI
                            completion = self.open_ai.chat.completions.create(
                                model="gpt-3.5-turbo",
                                messages=self.gpt_conversation,
                            )

                            response = completion.choices[0].message.content
                            message = response

                # Add assistant response to chat history
                self.display_conversation.append(
                    {"role": "assistant", "content": message}
                )
                self.gpt_conversation.append({"role": "assistant", "content": response})

                with l:
                    with user_save_button_placeholder:
                        if st.button(
                            "💾",
                            key=f"user_save_button",
                            help="Save this message as a thought!",
                        ):
                            self.save_thought_dialog(prompt)
                with r:
                    with assistant_save_button_placeholder:
                        if st.button(
                            "💾",
                            key=f"assistant_save_button",
                            help="Save this message as a thought!",
                        ):
                            self.save_thought_dialog(message)

                # Display assistant response in chat message container
                full_msg = ""
                with assistant_placeholder:
                    for word in message.split(" "):
                        full_msg += word + " "
                        time.sleep(0.025)
                        st.chat_message("assistant").markdown(full_msg)
