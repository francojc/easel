"""CLI command modules."""

from .assignment import assignment
from .config import config, init
from .course import course
from .doctor import doctor
from .user import user

__all__ = ["assignment", "config", "course", "doctor", "user", "init"]
