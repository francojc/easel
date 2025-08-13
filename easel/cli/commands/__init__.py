"""CLI command modules."""

from .assignment import assignment
from .config import config, init
from .content import content
from .course import course
from .doctor import doctor
from .grade import grade
from .page import page
from .user import user

__all__ = [
    "assignment",
    "config",
    "content",
    "course",
    "doctor",
    "grade",
    "page",
    "user",
    "init",
]
