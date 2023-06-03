def user_photo_upload_location(obj, image):
    return f'photos/{obj.phone_number}/{image}'


def default_user_authentication_rule(user):
    if user.director:
        return user is not None and user.is_active and user.director.is_active
    return user is not None and user.is_active
