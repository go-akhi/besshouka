"""Pipeline — wires analyzer and anonymizer together.

The only module that knows both the analyzer and anonymizer exist.
"""

import logging

from besshouka.analyzer.conflict_resolution import resolve_conflicts
from besshouka.analyzer.normalize import clean_punctuation, normalize_text
from besshouka.anonymizer.engine import anonymize
from besshouka.orchestrator.context import ProcessingContext

logger = logging.getLogger(__name__)


def run(
    text: str,
    recognizer_config: dict,
    operator_config: dict,
    score_threshold: float = 0.5,
) -> ProcessingContext:
    """Execute the full anonymization pipeline end-to-end.

    Steps:
        1. Create ProcessingContext with original text.
        2. Normalize text (NFKC + punctuation cleanup).
        3. Run all recognizers against normalized text.
        4. Resolve conflicts between overlapping detections.
        5. Filter out results below the score threshold.
        6. Anonymize using the operator config.
        7. Return the completed ProcessingContext.

    Args:
        text: Raw input text.
        recognizer_config: Parsed recognizer registry config dict.
        operator_config: Parsed operator rules config dict.
        score_threshold: Minimum confidence score to anonymize a result.
            Results below this threshold are detected but not anonymized.
            Default is 0.5.

    Returns:
        ProcessingContext with all fields populated.
    """
    ctx = ProcessingContext(original_text=text)

    # Step 2: Normalize
    ctx.working_text = clean_punctuation(normalize_text(text))

    # Step 3: Run recognizers
    # Load regex recognizers from config
    if "recognizers" in recognizer_config:
        from besshouka.analyzer.recognizers.regex_recognizer import RegexRecognizer

        recognizers = []
        for entry in recognizer_config["recognizers"]:
            recognizers.append(
                RegexRecognizer(
                    name=entry["name"],
                    entity_type=entry["entity_type"],
                    pattern=entry["pattern"],
                    score=entry["score"],
                    source=entry.get("source", "regex_registry"),
                )
            )
    else:
        recognizers = []

    # Add dedicated recognizers
    from besshouka.analyzer.recognizers.my_number_recognizer import MyNumberRecognizer
    recognizers.append(MyNumberRecognizer())

    # Try to add GiNZA recognizer
    try:
        from besshouka.analyzer.recognizers.ginza_recognizer import GinzaRecognizer
        recognizers.append(GinzaRecognizer())
    except Exception as e:
        logger.warning("GiNZA recognizer unavailable, running regex-only: %s", e)

    all_results = []
    for recognizer in recognizers:
        try:
            results = recognizer.recognize(ctx.working_text)
            all_results.extend(results)
        except Exception as e:
            logger.warning(
                "Recognizer '%s' failed, skipping: %s",
                recognizer.name, e,
            )

    # Step 4: Resolve conflicts
    ctx.recognizer_results = resolve_conflicts(all_results)

    # Step 5: Filter by score threshold
    above_threshold = [r for r in ctx.recognizer_results if r.score >= score_threshold]

    # Step 6: Anonymize
    op_config = operator_config.get("operators", {})
    ctx.engine_result = anonymize(ctx.working_text, above_threshold, op_config)

    return ctx
