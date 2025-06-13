from typing import Protocol
from enum import Enum

from django.contrib.sessions.models import Session


class MovieLogger(Enum):
    SIMKL = "simkl"


class MovieLoggerProtocol(Protocol):
    ...
