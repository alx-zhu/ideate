import streamlit as st
from supabase import create_client, Client

url: str = st.secrets["SUPABASE_URL"]
key: str = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)


def sign_up_user(email, password):
    try:
        user = supabase.auth.sign_up(
            {
                "email": email,
                "password": password,
            }
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
        idea = supabase.table("Ideas").insert(insert).execute()
        print(idea)
        return idea
    except Exception as e:
        print(f"Idea creation failed. {e}")
        return None
