from typing import List
import streamlit as st
from supabase import create_client, Client
from constants import (
    IDEAS_STRINGS_TABLE,
    IDEAS_TABLE,
    POSTS_TABLE,
    STRINGS_TABLE,
    USERS_TABLE,
    LIKES_TABLE,
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
            response = self.supabase.table(IDEAS_TABLE).insert(insert).execute()
            # print(response)
            return response.data[0]
        except Exception as e:
            print(f"Idea creation failed. {e}")
            return None

    def list_thoughts(self, user_id: str):
        try:
            response = (
                self.supabase.table(IDEAS_TABLE)
                .select("*")
                .eq("user_id", user_id)
                .order("created_at", desc=True)
                .execute()
            )
            # print(response)
            return response.data
        except Exception as e:
            print(f"Idea listing failed. {e}")
            return []

    def update_thought(
        self, thought_id: int, new_summary: str, new_description: str, new_type: str
    ):
        try:
            response = (
                self.supabase.table(IDEAS_TABLE)
                .update(
                    {
                        "summary": new_summary.strip(),
                        "description": new_description.strip(),
                        "type": new_type,
                    }
                )
                .eq("id", thought_id)
                .execute()
            )
            print(response)
            return response.data
        except Exception as e:
            print(f"Error updating thought {e}.")
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
                    f"id, like_count, {IDEAS_TABLE}(summary, description, created_at), {USERS_TABLE}!posts_user_id_fkey(first_name, last_name, email)"
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
                    f"id, like_count, {IDEAS_TABLE}(summary, description, created_at)"
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

    def add_string(self, summary: str, description: str):
        insert = {"summary": summary.strip(), "description": description.strip()}
        try:
            response = self.supabase.table(STRINGS_TABLE).insert(insert).execute()
            # print(response)
            return response.data[0]
        except Exception as e:
            print(f"String creation failed. {e}")
            return None

    def list_user_strings(self, user_id: str):
        try:
            response = (
                self.supabase.table(STRINGS_TABLE)
                .select("*")
                .eq("user_id", user_id)
                .order("created_at", desc=True)
                .execute()
            )
            # print(response)
            return response.data
        except Exception as e:
            print(f"String listing failed. {e}")
            return []

    def list_thoughts_in_string(self, string_id: str):
        try:
            response = (
                self.supabase.table(IDEAS_STRINGS_TABLE)
                .select(f"{IDEAS_TABLE}(id, summary, description, created_at)")
                .eq("string_id", string_id)
                .execute()
            )
            # print(response)
            flattened_data = [
                {
                    "id": thought[IDEAS_TABLE]["id"],
                    "summary": thought[IDEAS_TABLE]["summary"],
                    "description": thought[IDEAS_TABLE]["description"],
                    "created_at": thought[IDEAS_TABLE]["created_at"],
                }
                for thought in response.data
            ]
            return flattened_data
        except Exception as e:
            print(f"String listing failed. {e}")
            return []

    def update_string(self, string_id: int, new_summary: str, new_description: str):
        try:
            response = (
                self.supabase.table(STRINGS_TABLE)
                .update(
                    {
                        "summary": new_summary.strip(),
                        "description": new_description.strip(),
                    }
                )
                .eq("id", string_id)
                .execute()
            )
            # print(response)
            return response.data
        except Exception as e:
            print(f"Error updating string {e}.")
            return None

    def add_thought_to_string(self, thought_id: int, string_id: int):
        insert = {"thought_id": thought_id, "string_id": string_id}
        try:
            response = self.supabase.table(IDEAS_STRINGS_TABLE).insert(insert).execute()
            # print(response)
            return response.data[0]
        except Exception as e:
            print(f"String creation failed. {e}")
            return None

    def add_many_thoughts_to_string(self, string_id: int, thought_ids: List[int]):
        try:
            to_add = [
                {"thought_id": thought_id, "string_id": string_id}
                for thought_id in thought_ids
            ]
            response = self.supabase.table(IDEAS_STRINGS_TABLE).insert(to_add).execute()
            # print(response)
            return response.data
        except Exception as e:
            print(f"String creation failed. {e}")
            return None

    def add_thought_to_many_strings(self, thought_id: int, string_ids: List[int]):
        try:
            to_add = [
                {"thought_id": thought_id, "string_id": string_id}
                for string_id in string_ids
            ]
            response = self.supabase.table(IDEAS_STRINGS_TABLE).insert(to_add).execute()
            # print(response)
            return response.data
        except Exception as e:
            print(f"String creation failed. {e}")
            return None

    def remove_thoughts_from_string(self, string_id: int, thought_ids: List[int]):
        try:
            response = (
                self.supabase.table(IDEAS_STRINGS_TABLE)
                .delete()
                .eq("string_id", string_id)
                .in_("thought_id", thought_ids)
                .execute()
            )
            # print(response)
            return response.data
        except Exception as e:
            print(f"String creation failed. {e}")
            return None

    def remove_thought_from_string(self, thought_id: int, string_id: int):
        try:
            response = (
                self.supabase.table(IDEAS_STRINGS_TABLE)
                .delete()
                .eq("thought_id", thought_id)
                .eq("string_id", string_id)
                .execute()
            )
            # print(response)
            return response.data
        except Exception as e:
            print(f"Failed to remove thought from string. {e}")
            return None
