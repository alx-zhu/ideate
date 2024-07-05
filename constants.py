IDEAS_TABLE = "thoughts"
POSTS_TABLE = "posts"
USERS_TABLE = "users"
LIKES_TABLE = "likes"
STRINGS_TABLE = "strings"
IDEAS_STRINGS_TABLE = "thoughts_strings"
SUMMARY_MAX = 100
DESCRIPTION_MAX = 500
HOME_PAGE = "Home"
FEED_PAGE = "Feed"
ABOUT_PAGE = "About"
LOGIN_PAGE = "Login/Sign Up"
THOUGHT_TYPES = ["problem", "question", "thought", "solution"]


def pick_type_icon(thought_type):
    if thought_type == "problem":
        return "🔍"
    elif thought_type == "question":
        return "❓"
    elif thought_type == "thought":
        return "💭"
    elif thought_type == "solution":
        return "💡"
    else:
        return "🤔"
