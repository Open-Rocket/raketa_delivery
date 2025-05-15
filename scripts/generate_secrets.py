import secrets


def generate_secret_web_hook():
    for _ in range(4):
        print(secrets.token_urlsafe(32))


generate_secret_web_hook()
