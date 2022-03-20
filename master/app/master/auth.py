import bcrypt

class AuthManager:

    def __init__(self, parser, default_password='password') -> None:
        pass

    def update_password(self, password):
        self.password_hash = bcrypt.hashpw(password, bcrypt.gensalt())
    