from fma_django import models


class LoginMixin:
    def login_user(self, user_json):
        """Logs in user for authentication."""
        self.user = models.User.objects.get_or_create(**user_json)[0]
        self.client.force_login(self.user)

    def logout_user(self):
        """Logs out user from authentication."""
        self.client.logout()
        self.user = None

    def user_token_login(self, user_json):
        """Logs out user from authentication using tokens"""
        self.user = models.User.objects.get_or_create(**user_json)[0]
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.user.auth_token.key)

    def user_token_logout(self):
        """Logs out user from authentication using token."""
        self.client.credentials()
        self.user = None


class ClientMixin:
    def get_client_header(self, uuid):
        return {"CLIENT-UUID": uuid}

    def login_client(self, client_json):
        """Logs in user for authentication."""
        self.user_client = models.Client.objects.get_or_create(**client_json)[0]
        self.client.credentials(HTTP_CLIENT_UUID=self.user_client.uuid)

    def logout_client(self):
        """Logs out user from authentication."""
        self.client.credentials()
        self.user_client = None
