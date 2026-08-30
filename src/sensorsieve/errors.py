"""Public SensorSieve error categories."""


class SensorSieveError(Exception):
    """Base class for expected user-facing failures."""


class InputError(SensorSieveError):
    """Input paths, files, or command values are invalid."""


class CaptureQualityError(SensorSieveError):
    """Decoded images cannot support the promised analysis."""


class OutputError(SensorSieveError):
    """The requested output boundary is invalid."""
