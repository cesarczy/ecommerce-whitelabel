from authlib.integrations.httpx_client import AsyncOAuth2Client

from app.application.interfaces.ports import OAuthProviderPort, OAuthUserInfo
from app.core.config.settings import settings


class GoogleOAuthProvider(OAuthProviderPort):
    AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    TOKEN_URL = "https://oauth2.googleapis.com/token"
    USERINFO_URL = "https://openidconnect.googleapis.com/v1/userinfo"

    def get_authorization_url(self, *, state: str) -> str:
        client = AsyncOAuth2Client(
            client_id=settings.google_client_id,
            client_secret=settings.google_client_secret,
            redirect_uri=settings.oauth_redirect_uri,
        )
        uri, _ = client.create_authorization_url(
            self.AUTHORIZE_URL,
            state=state,
            scope="openid email profile",
        )
        return uri

    async def exchange_code(self, code: str) -> OAuthUserInfo:
        client = AsyncOAuth2Client(
            client_id=settings.google_client_id,
            client_secret=settings.google_client_secret,
            redirect_uri=settings.oauth_redirect_uri,
        )
        token = await client.fetch_token(self.TOKEN_URL, code=code)
        resp = await client.get(self.USERINFO_URL, token=token)
        data = resp.json()
        return OAuthUserInfo(
            provider="google",
            provider_user_id=data["sub"],
            email=data.get("email", ""),
            name=data.get("name", ""),
        )


class GitHubOAuthProvider(OAuthProviderPort):
    AUTHORIZE_URL = "https://github.com/login/oauth/authorize"
    TOKEN_URL = "https://github.com/login/oauth/access_token"
    USERINFO_URL = "https://api.github.com/user"

    def get_authorization_url(self, *, state: str) -> str:
        client = AsyncOAuth2Client(
            client_id=settings.github_client_id,
            client_secret=settings.github_client_secret,
            redirect_uri=settings.oauth_redirect_uri,
        )
        uri, _ = client.create_authorization_url(
            self.AUTHORIZE_URL,
            state=state,
            scope="read:user user:email",
        )
        return uri

    async def exchange_code(self, code: str) -> OAuthUserInfo:
        client = AsyncOAuth2Client(
            client_id=settings.github_client_id,
            client_secret=settings.github_client_secret,
            redirect_uri=settings.oauth_redirect_uri,
        )
        token = await client.fetch_token(self.TOKEN_URL, code=code)
        resp = await client.get(self.USERINFO_URL, token=token)
        data = resp.json()
        email = data.get("email") or f"{data['id']}@users.noreply.github.com"
        return OAuthUserInfo(
            provider="github",
            provider_user_id=str(data["id"]),
            email=email,
            name=data.get("name") or data.get("login", ""),
        )
