from typing import List
import streamlit as st
from supabase import create_client, Client
from datetime import datetime
from app.constants import (
    TOPIC_THOUGHTS_TABLE,
    THOUGHTS_TABLE,
    POSTS_TABLE,
    TOPICS_TABLE,
    USERS_TABLE,
    LIKES_TABLE,
    CONNECTIONS_TABLE,
)


class SupabaseClient(object):
    def __init__(
        self,
        url: str = st.secrets["SUPABASE_URL"],
        key: str = st.secrets["SUPABASE_KEY"],
    ):
        self.url = url
        self.key = key
        self.supabase: Client = create_client(url, key)

    ################################################################################
    ############################### AUTHENTICATION #################################
    ################################################################################

    def sign_up_user(self, email, password, first_name, last_name):
        try:
            response = self.supabase.auth.sign_up(
                {
                    "email": email,
                    "password": password,
                    "options": {
                        "data": {"first_name": first_name, "last_name": last_name}
                    },
                },
            )
            return response.user
        except Exception as e:
            print(f"Sign Up Failed. {e}")
            return None

    def login_user(self, email, password):
        try:
            response = self.supabase.auth.sign_in_with_password(
                {"email": email, "password": password}
            )
            return response.user
        except Exception as e:
            print(f"Sign In Failed. {e}")
            return None

    def get_current_user(
        self,
    ):
        if "access_token" not in st.session_state:
            print("Not authenticated")
            return None, None

        try:
            # This will use the stored access token to get the user
            user = self.supabase.auth.get_user(st.session_state.access_token)
            # print(user.user)
            return user.user, None
        except Exception as e:
            print(f"Failed to get user: {e}")
            return None, e

    def sign_in_with_google(self):
        self.supabase.auth.sign_in_with_oauth(
            {
                "provider": "google",
            }
        )

    ################################################################################
    #################################### USER ######################################
    ################################################################################

    def get_user_info(self, user_id: str):
        # print(f"Getting user info for {user_id}")
        try:
            response = (
                self.supabase.table(USERS_TABLE)
                .select(
                    "first_name, last_name, email, tagline, bio, streak, best_streak, last_thought_timestamp"
                )
                .eq("id", user_id)
                .execute()
            )
            return response.data[0]
        except Exception as e:
            print(f"User info retrieval failed. {e}")
            return None

    def update_user_info(
        self,
        user_id: str,
        first_name: str,
        last_name: str,
        email: str,
        tagline: str,
        bio: str,
        **_,  # Ignore any other arguments
    ):
        try:
            response = (
                self.supabase.table(USERS_TABLE)
                .update(
                    {
                        "first_name": first_name.strip(),
                        "last_name": last_name.strip(),
                        "email": email.strip(),
                        "tagline": tagline.strip(),
                        "bio": bio.strip(),
                    }
                )
                .eq("id", user_id)
                .execute()
            )
            # print(response)
            return response.data
        except Exception as e:
            print(f"User info update failed. {e}")
            return None

    def update_user_last_thought_timestamp(self, user_id: str, timestamp: str):
        try:
            response = (
                self.supabase.table(USERS_TABLE)
                .update({"last_thought_timestamp": timestamp})
                .eq("id", user_id)
                .execute()
            )
            # print(response)
            return response.data
        except Exception as e:
            print(f"User last login update failed. {e}")
            return None

    ################################################################################
    ################################### IDEAS ######################################
    ################################################################################

    def add_thought(
        self, summary: str, description: str, thought_type: str, user_id: str = ""
    ):
        insert = {
            "summary": summary.strip(),
            "description": description.strip(),
            "type": thought_type.strip(),
        }
        if user_id:
            insert["user_id"] = user_id
        try:
            response = self.supabase.table(THOUGHTS_TABLE).insert(insert).execute()
            # print(response)
            return response.data[0]
        except Exception as e:
            print(f"Thought creation failed. {e}")
            return None

    def list_thoughts(self, user_id: str):
        try:
            response = (
                self.supabase.table(THOUGHTS_TABLE)
                .select("*")
                .eq("user_id", user_id)
                .order("created_at", desc=True)
                .execute()
            )
            # print(response)
            return response.data
        except Exception as e:
            print(f"Thought listing failed. {e}")
            return []

    def update_thought(
        self, thought, new_summary: str, new_description: str, new_type: str
    ):
        now = datetime.now().isoformat()
        try:
            interactions = thought["interactions"]
            thought_id = thought["id"]
            response = (
                self.supabase.table(THOUGHTS_TABLE)
                .update(
                    {
                        "summary": new_summary.strip(),
                        "description": new_description.strip(),
                        "type": new_type,
                        "interactions": interactions + 1,
                        "last_interaction": now,
                    }
                )
                .eq("id", thought_id)
                .execute()
            )
            # print(response)
            return response.data
        except Exception as e:
            print(f"Error updating thought {e}.")
            return None

    def interact_with_thought(self, thought):
        try:
            thought_id = thought["id"]
            interactions = thought["interactions"]
            now = datetime.now().isoformat()
            response = (
                self.supabase.table(THOUGHTS_TABLE)
                .update({"interactions": interactions + 1, "last_interaction": now})
                .eq("id", thought_id)
                .execute()
            )
            print(response)
            return response.data
        except Exception as e:
            print(f"Thought interaction failed. {e}")
            return None

    def bookmark_thought(self, thought_id: int):
        try:
            response = (
                self.supabase.table(THOUGHTS_TABLE)
                .update({"bookmarked": True})
                .eq("id", thought_id)
                .execute()
            )
            return response.data
        except Exception as e:
            print(f"Thought bookmark failed. {e}")
            return None

    def unbookmark_thought(self, thought_id: int, user_id: str):
        try:
            response = (
                self.supabase.table(THOUGHTS_TABLE)
                .update({"bookmarked": False})
                .eq("id", thought_id)
                .execute()
            )
            return response.data
        except Exception as e:
            print(f"Thought unbookmark failed. {e}")
            return None

    ################################################################################
    ################################### POSTS ######################################
    ################################################################################

    def add_post(self, thought_id: int):
        insert = {"thought_id": thought_id}
        try:
            response = self.supabase.table(POSTS_TABLE).insert(insert).execute()
            # print(response)
            return response.data[0]
        except Exception as e:
            print(f"Post creation failed. {e}")
            return None

    def list_posts(
        self,
    ):
        try:
            response = (
                self.supabase.table(POSTS_TABLE)
                .select(
                    f"id, like_count, {THOUGHTS_TABLE}(summary, description, created_at), {USERS_TABLE}!posts_user_id_fkey(first_name, last_name, email)"
                )
                .order("created_at", desc=True)
                .execute()
            )
            # print(response)
            return response.data
        except Exception as e:
            print(f"Post listing failed. {e}")
            return []

    def list_user_posts(self, user_id: str):
        try:
            response = (
                self.supabase.table(POSTS_TABLE)
                .select(
                    f"id, like_count, {THOUGHTS_TABLE}(summary, description, created_at)"
                )
                .eq("user_id", user_id)
                .order("created_at", desc=True)
                .execute()
            )
            # print(response)
            return response.data
        except Exception as e:
            print(f"Post listing failed. {e}")
            return []

    ################################################################################
    ################################### LIKES ######################################
    ################################################################################

    def user_likes_post(self, user_id: str, post_id: int):
        try:
            response = (
                self.supabase.table(LIKES_TABLE)
                .insert(
                    {
                        "user_id": user_id,
                        "post_id": post_id,
                    }
                )
                .execute()
            )
            # print(response)
            return response.data
        except Exception as e:
            print(f"Failed to like post. {e}")
            return None

    def user_unlikes_post(self, user_id: str, post_id: int):
        try:
            response = (
                self.supabase.table(LIKES_TABLE)
                .delete()
                .eq("user_id", user_id)
                .eq("post_id", post_id)
                .execute()
            )
            # print(response)
            return response.data
        except Exception as e:
            print(f"Failed to unlike post. {e}")
            return None

    def check_if_user_likes_post(self, user_id: str, post_id: int):
        try:
            response = (
                self.supabase.table(LIKES_TABLE)
                .select("", count="exact")
                .eq("user_id", user_id)
                .eq("post_id", post_id)
                .execute()
            )
            # print(response)
            return response.count > 0
        except Exception as e:
            print(f"Failed to check if user likes post. {e}")
            return False

    def count_post_likes(self, post_id: int):
        try:
            response = (
                self.supabase.table(LIKES_TABLE)
                .select("", count="exact")
                .eq("post_id", post_id)
                .execute()
            )
            # print(response)
            return response.count
        except Exception as e:
            print(f"Could not get like count. {e}")
            return 0

    def count_user_likes(self, user_id: str):
        try:
            response = (
                self.supabase.table(LIKES_TABLE)
                .select("", count="exact")
                .eq("user_id", user_id)
                .execute()
            )
            # print(response)
            return response.count
        except Exception as e:
            print(f"Could not get like count. {e}")

    ################################################################################
    ################################## STRINGS #####################################
    ################################################################################

    def list_user_strings(self, user_id: str):
        try:
            response = (
                self.supabase.table(CONNECTIONS_TABLE)
                .select("*")
                .eq("user_id", user_id)
                .execute()
            )
            # print(response)
            return response.data
        except Exception as e:
            print(f"String listing failed. {e}")
            return []

    def list_connected_thoughts(self, thought_id: int):
        try:
            data = [
                row["j"]
                for row in (
                    self.supabase.table(CONNECTIONS_TABLE)
                    .select(f"j")
                    .eq("i", thought_id)
                    .execute()
                ).data
            ]
            data += [
                row["i"]
                for row in (
                    self.supabase.table(CONNECTIONS_TABLE)
                    .select(f"i")
                    .eq("j", thought_id)
                    .execute()
                ).data
            ]
            # {THOUGHTS_TABLE}!thought_strings_i_fkey(id, summary, description, created_at)
            # flattened_data = [
            #     {
            #         "id": thought[THOUGHTS_TABLE]["id"],
            #         "summary": thought[THOUGHTS_TABLE]["summary"],
            #         "description": thought[THOUGHTS_TABLE]["description"],
            #         "created_at": thought[THOUGHTS_TABLE]["created_at"],
            #     }
            #     for thought in response.data
            # ]
            return data
        except Exception as e:
            print(f"String listing failed. {e}")
            return []

    def connect_thought(self, thought_1: int, thought_2: int):
        insert = {"i": thought_1, "j": thought_2}
        try:
            response = self.supabase.table(CONNECTIONS_TABLE).insert(insert).execute()
            # print(response)
            return response.data[0]
        except Exception as e:
            print(f"String creation failed. {e}")
            return None

    def connect_many_thoughts(self, thought_1: int, thought_ids: List[int]):
        try:
            to_add = [{"i": thought_1, "j": thought_id} for thought_id in thought_ids]
            response = self.supabase.table(CONNECTIONS_TABLE).insert(to_add).execute()
            # print(response)
            return response.data
        except Exception as e:
            print(f"String creation failed. {e}")
            return None

    def disconnect_thought(self, thought_1: int, thought_2: int):
        try:
            response = (
                self.supabase.table(CONNECTIONS_TABLE)
                .delete()
                .eq("i", thought_1)
                .eq("j", thought_2)
                .execute()
            ).data

            response += (
                self.supabase.table(CONNECTIONS_TABLE)
                .delete()
                .eq("i", thought_2)
                .eq("j", thought_1)
                .execute()
            ).data
            # print(response)
            return response
        except Exception as e:
            print(f"Failed to delete string. {e}")
            return None

    def disconnect_many_thoughts(self, thought_1: int, thought_ids: List[int]):
        try:
            response = (
                self.supabase.table(CONNECTIONS_TABLE)
                .delete()
                .eq("i", thought_1)
                .in_("j", thought_ids)
                .execute()
            ).data

            response += (
                self.supabase.table(CONNECTIONS_TABLE)
                .delete()
                .eq("j", thought_1)
                .in_("i", thought_ids)
                .execute()
            ).data

            # print(response)
            return response
        except Exception as e:
            print(f"Failed to delete string. {e}")
            return None

    ################################################################################
    ################################## TOPICS ######################################
    ################################################################################

    def add_topic(self, summary: str, description: str):
        insert = {"summary": summary.strip(), "description": description.strip()}
        try:
            response = self.supabase.table(TOPICS_TABLE).insert(insert).execute()
            # print(response)
            return response.data[0]
        except Exception as e:
            print(f"Topic creation failed. {e}")
            return None

    def list_user_topics(self, user_id: str):
        try:
            response = (
                self.supabase.table(TOPICS_TABLE)
                .select("*")
                .eq("user_id", user_id)
                .order("created_at", desc=True)
                .execute()
            )
            # print(response)
            return response.data
        except Exception as e:
            print(f"Topic listing failed. {e}")
            return []

    def list_thoughts_in_topic(self, topic_id: str):
        try:
            response = (
                self.supabase.table(TOPIC_THOUGHTS_TABLE)
                .select(f"{THOUGHTS_TABLE}(id, summary, description, created_at)")
                .eq("topic_id", topic_id)
                .execute()
            )
            # print(response)
            flattened_data = [
                {
                    "id": thought[THOUGHTS_TABLE]["id"],
                    "summary": thought[THOUGHTS_TABLE]["summary"],
                    "description": thought[THOUGHTS_TABLE]["description"],
                    "created_at": thought[THOUGHTS_TABLE]["created_at"],
                }
                for thought in response.data
            ]
            return flattened_data
        except Exception as e:
            print(f"Topic listing failed. {e}")
            return []

    def update_topic(self, topic_id: int, new_summary: str, new_description: str):
        try:
            response = (
                self.supabase.table(TOPICS_TABLE)
                .update(
                    {
                        "summary": new_summary.strip(),
                        "description": new_description.strip(),
                    }
                )
                .eq("id", topic_id)
                .execute()
            )
            # print(response)
            return response.data
        except Exception as e:
            print(f"Error updating topic {e}.")
            return None

    def add_thought_to_topic(self, thought_id: int, topic_id: int):
        insert = {"thought_id": thought_id, "topic_id": topic_id}
        try:
            response = (
                self.supabase.table(TOPIC_THOUGHTS_TABLE).insert(insert).execute()
            )
            # print(response)
            return response.data[0]
        except Exception as e:
            print(f"Topic creation failed. {e}")
            return None

    def add_many_thoughts_to_topic(self, topic_id: int, thought_ids: List[int]):
        try:
            to_add = [
                {"thought_id": thought_id, "topic_id": topic_id}
                for thought_id in thought_ids
            ]
            response = (
                self.supabase.table(TOPIC_THOUGHTS_TABLE).insert(to_add).execute()
            )
            # print(response)
            return response.data
        except Exception as e:
            print(f"Topic creation failed. {e}")
            return None

    def add_thought_to_many_topics(self, thought_id: int, topic_ids: List[int]):
        try:
            to_add = [
                {"thought_id": thought_id, "topic_id": topic_id}
                for topic_id in topic_ids
            ]
            response = (
                self.supabase.table(TOPIC_THOUGHTS_TABLE).insert(to_add).execute()
            )
            # print(response)
            return response.data
        except Exception as e:
            print(f"Topic creation failed. {e}")
            return None

    def remove_thoughts_from_topic(self, topic_id: int, thought_ids: List[int]):
        try:
            response = (
                self.supabase.table(TOPIC_THOUGHTS_TABLE)
                .delete()
                .eq("topic_id", topic_id)
                .in_("thought_id", thought_ids)
                .execute()
            )
            # print(response)
            return response.data
        except Exception as e:
            print(f"Topic creation failed. {e}")
            return None

    def remove_thought_from_topic(self, thought_id: int, topic_id: int):
        try:
            response = (
                self.supabase.table(TOPIC_THOUGHTS_TABLE)
                .delete()
                .eq("thought_id", thought_id)
                .eq("topic_id", topic_id)
                .execute()
            )
            # print(response)
            return response.data
        except Exception as e:
            print(f"Failed to remove thought from topic. {e}")
            return None
