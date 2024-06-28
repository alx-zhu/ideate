import streamlit as st
from supabase import create_client, Client

from constants import IDEAS_TABLE, POSTS_TABLE, USERS_TABLE

url: str = st.secrets["SUPABASE_URL"]
key: str = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)


def sign_up_user(email, password, first_name, last_name):
    try:
        user = supabase.auth.sign_up(
            {
                "email": email,
                "password": password,
                "options": {"data": {"first_name": first_name, "last_name": last_name}},
            },
        )
        return user
    except Exception as e:
        print(f"Sign Up Failed. {e}")
        return None


def login_user(email, password):
    try:
        user = supabase.auth.sign_in_with_password(
            {"email": email, "password": password}
        )
        return user
    except Exception as e:
        print(f"Sign In Failed. {e}")
        return None


def add_idea(summary: str, description: str, user_id: str = ""):
    insert = {"summary": summary, "description": description}
    if user_id:
        insert["user_id"] = user_id
    try:
        response = supabase.table(IDEAS_TABLE).insert(insert).execute()
        print(response)
        return response.data[0]
    except Exception as e:
        print(f"Idea creation failed. {e}")
        return None


def list_ideas(user_id: str):
    try:
        response = (
            supabase.table(IDEAS_TABLE)
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .execute()
        )
        print(response)
        return response.data
    except Exception as e:
        print(f"Idea listing failed. {e}")
        return []


def update_idea(idea_id: int, new_summary: str, new_description: str):
    print(idea_id, new_summary, new_description)
    try:
        response = (
            supabase.table(IDEAS_TABLE)
            .update({"summary": new_summary, "description": new_description})
            .eq("id", idea_id)
            .execute()
        )
        print(response)
        return response.data
    except Exception as e:
        print(f"Error updating idea {e}.")
        return None


def add_post(idea_id: int):
    insert = {"idea_id": idea_id}
    try:
        response = supabase.table(POSTS_TABLE).insert(insert).execute()
        print(response)
        return response.data[0]
    except Exception as e:
        print(f"Post creation failed. {e}")
        return None


def list_posts():
    try:
        response = (
            supabase.table(POSTS_TABLE)
            .select(
                f"{IDEAS_TABLE}(summary, description, created_at), {USERS_TABLE}(first_name, last_name, email)"
            )
            .order("created_at", desc=True)
            .execute()
        )
        print(response)
        return response.data
    except Exception as e:
        print(f"Post listing failed. {e}")
        return []
