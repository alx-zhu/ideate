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
            st.session_state.access_token = response.session.access_token
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
                    "first_name, last_name, email, tagline, bio, streak, best_streak, last_idea_timestamp"
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

    def update_user_last_idea_timestamp(self, user_id: str, timestamp: str):
        try:
            response = (
                self.supabase.table(USERS_TABLE)
                .update({"last_idea_timestamp": timestamp})
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

    def add_idea(self, summary: str, description: str, user_id: str = ""):
        insert = {"summary": summary.strip(), "description": description.strip()}
        if user_id:
            insert["user_id"] = user_id
        try:
            response = self.supabase.table(IDEAS_TABLE).insert(insert).execute()
            # print(response)
            return response.data[0]
        except Exception as e:
            print(f"Idea creation failed. {e}")
            return None

    def list_ideas(self, user_id: str):
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

    def update_idea(self, idea_id: int, new_summary: str, new_description: str):
        try:
            response = (
                self.supabase.table(IDEAS_TABLE)
                .update(
                    {
                        "summary": new_summary.strip(),
                        "description": new_description.strip(),
                    }
                )
                .eq("id", idea_id)
                .execute()
            )
            print(response)
            return response.data
        except Exception as e:
            print(f"Error updating idea {e}.")
            return None

    ################################################################################
    ################################### POSTS ######################################
    ################################################################################

    def add_post(self, idea_id: int):
        insert = {"idea_id": idea_id}
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

    def list_ideas_in_string(self, string_id: str):
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
                    "id": idea[IDEAS_TABLE]["id"],
                    "summary": idea[IDEAS_TABLE]["summary"],
                    "description": idea[IDEAS_TABLE]["description"],
                    "created_at": idea[IDEAS_TABLE]["created_at"],
                }
                for idea in response.data
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

    def add_idea_to_string(self, idea_id: int, string_id: int):
        insert = {"idea_id": idea_id, "string_id": string_id}
        try:
            response = self.supabase.table(IDEAS_STRINGS_TABLE).insert(insert).execute()
            # print(response)
            return response.data[0]
        except Exception as e:
            print(f"String creation failed. {e}")
            return None

    def add_many_ideas_to_string(self, string_id: int, idea_ids: List[int]):
        try:
            to_add = [
                {"idea_id": idea_id, "string_id": string_id} for idea_id in idea_ids
            ]
            response = self.supabase.table(IDEAS_STRINGS_TABLE).insert(to_add).execute()
            # print(response)
            return response.data
        except Exception as e:
            print(f"String creation failed. {e}")
            return None

    def add_idea_to_many_strings(self, idea_id: int, string_ids: List[int]):
        try:
            to_add = [
                {"idea_id": idea_id, "string_id": string_id} for string_id in string_ids
            ]
            response = self.supabase.table(IDEAS_STRINGS_TABLE).insert(to_add).execute()
            # print(response)
            return response.data
        except Exception as e:
            print(f"String creation failed. {e}")
            return None

    def remove_ideas_from_string(self, string_id: int, idea_ids: List[int]):
        try:
            response = (
                self.supabase.table(IDEAS_STRINGS_TABLE)
                .delete()
                .eq("string_id", string_id)
                .in_("idea_id", idea_ids)
                .execute()
            )
            # print(response)
            return response.data
        except Exception as e:
            print(f"String creation failed. {e}")
            return None

    def remove_idea_from_string(self, idea_id: int, string_id: int):
        try:
            response = (
                self.supabase.table(IDEAS_STRINGS_TABLE)
                .delete()
                .eq("idea_id", idea_id)
                .eq("string_id", string_id)
                .execute()
            )
            # print(response)
            return response.data
        except Exception as e:
            print(f"Failed to remove idea from string. {e}")
            return None
