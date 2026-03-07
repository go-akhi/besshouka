"""ProcessingContext — shared state object that travels through the pipeline."""

from dataclasses import dataclass, field

from besshouka.models.recognizer_result import RecognizerResult
from besshouka.models.engine_result import EngineResult


@dataclass
class ProcessingContext:
    """Carries data through each pipeline stage.

    Attributes:
        original_text: Raw input text (immutable throughout processing).
        working_text: Text after normalization (set by the normalize step).
        recognizer_results: PII detections after conflict resolution.
        engine_result: Final anonymized output from the anonymizer.
        metadata: Optional source info (filename, timestamp, etc.).
    """

    original_text: str
    working_text: str | None = None
    recognizer_results: list[RecognizerResult] = field(default_factory=list)
    engine_result: EngineResult | None = None
    metadata: dict = field(default_factory=dict)
