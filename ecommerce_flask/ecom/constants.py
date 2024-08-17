ROLES_SEED_DATA = [
    {
        "role_name": "Admin",
        "role_desc": "Role for admin users",
    },
    {
        "role_name": "Business User",
        "role_desc": "Role for business users",
    },
]

USERS_SEED_DATA = [
    {
        "first_name": "admin",
        "last_name": "admin",
        "email": "admin@mycervello.com",
        "role": "Admin",
    },
    {
        "first_name": "guest",
        "last_name": "guest",
        "email": "guest@mycervello.com",
        "role": "Admin",
    },
]

CACHE_CLEAR_SAFE_SUFFIX = "_clear_safe"
CACHE_INDEFINETLY = 0
