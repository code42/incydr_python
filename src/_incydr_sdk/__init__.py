__all__ = ["__version__"]

try:
    from _incydr_sdk.version import __version__
except ImportError:
    __version__ = "unknown"
