"""CouchDB HTTP integration."""

from .client import (
    CouchDBClient,
    CouchDBConflict,
    CouchDBError,
    CouchDBNotFound,
    CouchDBResponseError,
)

__all__ = [
    "CouchDBClient",
    "CouchDBConflict",
    "CouchDBError",
    "CouchDBNotFound",
    "CouchDBResponseError",
]
