import os.path
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.discovery import Resource
from boxtime.auth.scope import Scope


def get_token_path(scope: Scope) -> Path:
    par = Path("credentials", scope.name.lower())
    par.mkdir(parents=True, exist_ok=True)
    p = par / "token.json"
    return p


def get_credential_path() -> Path:
    return Path("credentials", "google.credentials.json")


def get_local_credentials(scope: Scope) -> Credentials | None:
    token_path = get_token_path(scope)
    if os.path.exists(token_path):
        return Credentials.from_authorized_user_file(token_path, [scope.value])
    return None


def refresh_credentials(creds: Credentials | None, scope: Scope) -> Credentials:
    credential_path = get_credential_path()
    token_path = get_token_path(scope)

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(credential_path, [scope.value])
        creds = flow.run_local_server(port=0)

    with open(token_path, "w") as token:
        token.write(creds.to_json())


def get_calendar_client(scope: Scope) -> Resource:
    creds = get_local_credentials(scope)

    if not creds or not creds.valid:
        refresh_credentials(creds, scope)

    return build("calendar", "v3", credentials=creds)
