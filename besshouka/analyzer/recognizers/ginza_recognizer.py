"""GiNZA/spaCy NER recognizer wrapper."""

import logging

from besshouka.analyzer.recognizers.base import BaseRecognizer
from besshouka.models.recognizer_result import RecognizerResult

logger = logging.getLogger(__name__)


# Mapping from GiNZA/OntoNotes labels to standardized entity types
_LABEL_MAP = {
    "Person": "PERSON",
    "PERSON": "PERSON",
    "Location": "LOCATION",
    "LOC": "LOCATION",
    "GPE": "LOCATION",
    "FAC": "LOCATION",
    "Province": "LOCATION",
    "City": "LOCATION",
    "Country": "LOCATION",
    "Organization": "ORGANIZATION",
    "ORG": "ORGANIZATION",
    "Company": "ORGANIZATION",
    "Date": "DATE",
    "DATE": "DATE",
    "Time": "TIME",
    "TIME": "TIME",
    "Money": "MONEY",
    "MONEY": "MONEY",
    "Percent": "PERCENT",
    "PERCENT": "PERCENT",
    "QUANTITY": "QUANTITY",
    "Quantity": "QUANTITY",
}


class GinzaRecognizer(BaseRecognizer):
    """Recognizer that uses GiNZA (spaCy) for Japanese NER.

    The model is lazy-loaded on first call to recognize().
    """

    def __init__(self):
        self._nlp = None

    @property
    def name(self) -> str:
        return "ginza_ner"

    @property
    def source(self) -> str:
        return "ginza_ner"

    def _load_model(self):
        """Lazy-load the GiNZA spaCy model."""
        import spacy

        self._nlp = spacy.load("ja_ginza")
        return self._nlp

    def _map_label(self, label: str) -> str | None:
        """Map a GiNZA NER label to a standardized entity type.

        Returns None if the label is not in the mapping.
        """
        return _LABEL_MAP.get(label)

    def recognize(self, text: str) -> list[RecognizerResult]:
        """Run GiNZA NER on the text and return detected entities."""
        if not text:
            return []

        if self._nlp is None:
            self._load_model()

        doc = self._nlp(text)
        results = []

        for ent in doc.ents:
            entity_type = self._map_label(ent.label_)
            if entity_type is None:
                logger.debug("Skipping unmapped GiNZA label: %s", ent.label_)
                continue

            results.append(
                RecognizerResult(
                    start=ent.start_char,
                    end=ent.end_char,
                    entity_type=entity_type,
                    score=round(ent.kb_id_ and float(ent.kb_id_) or 0.85, 2),
                    source="ginza_ner",
                    text=ent.text,
                )
            )

        return results
