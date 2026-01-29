class ScraperError(Exception):
    """ Base class for scraper-related exceptions. """

class RateLimitError(ScraperError):
    """ Raised when the server rate limits the scraper (HTTP 429). """

class FetchError(ScraperError):
    """ Raised when a request fails for other reasons. """
