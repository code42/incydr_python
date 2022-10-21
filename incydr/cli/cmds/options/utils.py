def user_lookup(ctx, param, value):
    if not value:
        return
    if "@" in str(value):
        # assume username/email was passed
        client = ctx.obj()
        users = client.users.v1.get_page(username=value).users
        if len(users) < 1:
            raise ValueError(f"User with username '{value}' not found.")
        return users[0].user_id
    # else return ID
    return value
