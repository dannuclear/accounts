def is_user_in_group(user, groups):
    return user.groups.filter(name__in=groups).exists()