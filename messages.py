class ErrorMessage:
    USER_EXISTS_EMAIL = {'email': 'User with this email already exists'}
    USER_NOT_EXISTS = {'non_field': 'User doesn\'t exist'}
    USER_NOT_ADMIN = {'non_field': 'User is not admin'}
    INVALID_TOKEN = {'non_field': 'Invalid JWT'}
    WRONG_TOKEN = {'non_field': 'Wrong JWT type'}
    WRONG_TOKEN_HEADER = {'non_field': 'Wrong JWT header'}
    INCORRECT_PASSWORD = {'password': 'Incorrect password'}
    CURRENT_PASSWORD = {'current_password': 'Incorrect password'}
    AUTH_NEEDED = {'non_field': 'You need to be logged'}
    PERMISSION_DENIED = {'non_field': 'Permission denied'}

    PASSWORD_NOT_MATCH = 'Passwords do not match'
    PASSWORD_ERROR = 'Invalid password format. Your password must be at least 8 characters long and include' \
                     ' at least one uppercase letter, one lowercase letter, one number, and one special character.'
    NOT_FOUND = 'Object not found'
    VALUE_REQUIRED = 'This field is required'
    ACCOUNT_NOT_FOUND = 'The Instagram account {} does not exist.'
    EXTRACTING_PHOTOS = 'Error occurred while extracting photos for user {}'
    PRIVATE_ACCOUNT = 'The Instagram account {} is private.'


class SuccessMessage:
    PASSWORD_CHANGED = 'Password changed'
