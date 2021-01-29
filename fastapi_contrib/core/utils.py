import secrets
import string


class Proxy(dict):
    def __getattr__(self, key):
        return self[key]


def random_string(size=12):
    choices = string.ascii_letters + string.digits
    return "".join(secrets.choice(choices) for _ in range(size))
