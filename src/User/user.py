import hashlib

class User:
    """
    The User class represents a user in the application with basic authentication functionality.
    """

    def __init__(self, username: str, password: str):
        """
        Initializes a new user instance.

        :param username: The username of the user.
        :param password: The password of the user (will be hashed).
        """
        self.username = username
        self.password_hash = self.hash_password(password)

    def hash_password(self, password: str) -> str:
        """
        Hashes the password using SHA-256 for secure storage.

        :param password: The plain-text password to hash.
        :return: The hashed password as a hex string.
        """
        return hashlib.sha256(password.encode()).hexdigest()

    def check_password(self, password: str) -> bool:
        """
        Verifies that the provided password matches the stored password hash.

        :param password: The plain-text password to check.
        :return: True if the password matches, False otherwise.
        """
        return self.password_hash == self.hash_password(password)
