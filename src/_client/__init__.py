__all__ = ["__version__"]

try:
    from _client.version import __version__
except ImportError:
    __version__ = "unknown"
