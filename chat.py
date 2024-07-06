import json
import time
import streamlit as st
from openai import OpenAI
from constants import OPENAI_INITIAL_CONVERSATION
from supabase_client import SupabaseClient
from constants import DESCRIPTION_MAX, SUMMARY_MAX, THOUGHT_TYPES


@st.cache_resource()
def get_cached_openai_service():
    return OpenAI(api_key=st.secrets["OPENAI_API_KEY"])


@st.experimental_dialog("Save as Thought", width="large")
def save_thought_dialog(chat_message):
    supabase: SupabaseClient = st.session_state.supabase
    with st.expander("Message to Save"):
        st.chat_message(chat_message["role"]).markdown(chat_message["content"])
    st.divider()
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
                thought["edit_mode"] = False
                st.session_state.thoughts = [thought] + st.session_state.thoughts
                st.session_state.thought_map[thought["id"]] = thought
                st.success("Your thought has been added!")
                st.rerun()
            else:
                st.error("Error. Thought could not be added.")
        else:
            st.error("Please make sure all fields are filled out.")


def chat_page(initial_gpt_prompt, additional_info=""):
    # Initializating
    open_ai = get_cached_openai_service()
    if "message_count" not in st.session_state:
        st.session_state.message_count = 0

    if "display_conversation" not in st.session_state:
        st.session_state.display_conversation = []

    if (
        "gpt_conversation" not in st.session_state
        or len(st.session_state.gpt_conversation) == 0
    ):
        st.session_state.gpt_conversation = OPENAI_INITIAL_CONVERSATION
        st.session_state.gpt_conversation.append(
            {"role": "assistant", "content": initial_gpt_prompt}
        )
        st.session_state.display_conversation.append(
            {"role": "assistant", "content": initial_gpt_prompt}
        )

    for i, message in enumerate(st.session_state.display_conversation):
        l, r = st.columns((10, 1))
        with l:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        with r:
            if st.button("💾", key=f"save_{i}"):
                save_thought_dialog(message)

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
    if st.session_state.message_count > 10:
        st.warning(
            "You have passed your limit of 10 messages. In order to keep this service free, there is a 10 message limit per user. Please contact alexanderzhu07@gmail.com with any questions."
        )

    else:
        if prompt := st.chat_input(f"Prompt!", max_chars=500):
            st.session_state.message_count += 1

            with user_placeholder:
                st.chat_message("user").markdown(prompt)

            st.session_state.display_conversation.append(
                {"role": "user", "content": prompt}
            )
            st.session_state.gpt_conversation.append(
                {"role": "user", "content": prompt}
            )

            with assistant_placeholder:
                with st.chat_message("assistant"):
                    with st.spinner("Processing..."):
                        # Send message to Open AI
                        completion = open_ai.chat.completions.create(
                            model="gpt-3.5-turbo",
                            messages=st.session_state.gpt_conversation,
                        )

                        response = completion.choices[0].message.content
                        message = response

            # Display assistant response in chat message container
            full_msg = ""
            with assistant_placeholder:
                for word in message.split(" "):
                    full_msg += word + " "
                    time.sleep(0.05)
                    st.chat_message("assistant").markdown(full_msg)

            # Add assistant response to chat history
            st.session_state.display_conversation.append(
                {"role": "assistant", "content": message}
            )
            st.session_state.gpt_conversation.append(
                {"role": "assistant", "content": response}
            )

            st.rerun()


"""
You are an AI assistant designed to be an ideation partner, helping users organize, expand, and connect their thoughts across four categories: questions, problems, solutions (ideas), and general thoughts. Your goal is to facilitate productive conversations that lead users to discover new perspectives and generate thoughts they might not reach on their own. Act as a curious, supportive friend who asks insightful questions, points out potential flaws, and encourages strengths. Follow these guidelines in your interactions:

1. Condensation:
   - Summarize the user's input into a concise 100-character version.
   - Provide an expanded 500-character description that captures key details.

2. Thought Expansion:
   - Ask probing, open-ended questions to help users explore their thoughts more deeply.
   - Suggest unexpected angles or perspectives to consider.
   - Encourage users to add these new ideas as separate thoughts in the platform.

3. Unbiased Analysis:
   - Offer a balanced evaluation of the user's thoughts, presenting both strengths and potential weaknesses.
   - Highlight any logical inconsistencies or overlooked aspects in a constructive manner.
   - Suggest alternative approaches or modifications to enhance the idea.

4. Connections and Associations:
   - Identify potential links between the current thought and other ideas in the platform.
   - Propose innovative, even unconventional connections that could lead to new insights.
   - Encourage lateral thinking by drawing parallels from different fields or domains.

5. Categorization:
   - Help users determine which category (question, problem, solution, or general thought) best fits each idea.
   - Suggest how ideas might span multiple categories or evolve from one to another.

6. Curiosity-Driven Exploration:
   - Demonstrate genuine interest in the user's ideas, asking for elaboration on intriguing points.
   - Play devil's advocate when appropriate to challenge assumptions and stimulate deeper thinking.

7. Conversation Flow:
   - Maintain a balance between asking questions, providing insights, and offering constructive feedback.
   - Adapt your responses based on the user's level of engagement and the complexity of their ideas.

8. Encouragement and Support:
   - Provide positive reinforcement for creative thinking and thorough exploration of ideas.
   - Motivate users to continue developing and refining their thoughts, especially when they show promise or originality.
   - Offer reassurance when users face challenges or doubts in their ideation process.

9. Diverse Perspective Generation:
   - Suggest considering the idea from various viewpoints (e.g., different user groups, cultural contexts, or time frames).
   - Propose "what if" scenarios to explore potential variations or applications of the thought.

Remember to be supportive, genuinely curious, and thought-provoking in your interactions. Your role is to be an engaged ideation partner, helping users unlock their creative potential and discover new depths to their thoughts. Aim to create a safe space for brainstorming where all ideas are welcomed and explored, fostering an environment of creative exploration and intellectual growth.
"""
