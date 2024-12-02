try:
    from anaconda_assistant._version import version as __version__
except ImportError:  # pragma: nocover
    __version__ = "unknown"


from anaconda_assistant.core import ChatSession, ChatClient

__all__ = ["__version__", "ChatSession", "ChatClient"]
