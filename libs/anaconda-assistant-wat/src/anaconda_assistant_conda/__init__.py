try:
    from anaconda_assistant_conda._version import version as __version__
except ImportError:  # pragma: nocover
    __version__ = "unknown"


__all__ = ["__version__"]
