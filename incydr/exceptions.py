class WatchlistNotFoundError(Exception):
    """Raised when a watchlist with the matching type or title is not found.

    **Attributes**:
        * **salary** - input salary which caused the error
        * **message** - explanation of the error
    """

    def __init__(self, name):
        self.name = name
        self.message = f"No watchlist matching the type or title '{name}' was found."
        super().__init__(self.message)
