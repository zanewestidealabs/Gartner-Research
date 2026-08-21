"""Persistence abstractions used during JSON-to-CouchDB migration."""

from .base import CouchRepository, DocumentRepository

__all__ = ["CouchRepository", "DocumentRepository"]
