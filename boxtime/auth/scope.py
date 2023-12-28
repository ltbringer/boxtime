from enum import Enum


class Scope(Enum):
    """
    Enum of scopes for Google Calendar API
    """

    READ_ONLY = "https://www.googleapis.com/auth/calendar.readonly"
