import uuid


def generate_api_key():
    return uuid.uuid4().hex
