"""Besshouka CLI — command-line interface for the anonymization engine."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from besshouka.config.loader import load_recognizer_config, load_operator_config
from besshouka.orchestrator.pipeline import run

app = typer.Typer(help="Besshouka — Japanese PII anonymization engine.")
console = Console()

_DEFAULTS_DIR = Path(__file__).parent / "defaults"


def _get_recognizer_config(recognizers: Optional[Path]) -> dict:
    path = recognizers if recognizers else _DEFAULTS_DIR / "recognizers.yaml"
    return load_recognizer_config(path)


def _get_operator_config(rules: Optional[Path]) -> dict:
    path = rules if rules else _DEFAULTS_DIR / "operators.yaml"
    return load_operator_config(path)


def _read_input(text: Optional[str], input_file: Optional[Path]) -> str:
    if input_file:
        if not input_file.exists():
            console.print(f"[red]Error: file not found: {input_file}[/red]")
            raise typer.Exit(code=1)
        return input_file.read_text(encoding="utf-8")
    if text:
        return text
    console.print("[red]Error: provide TEXT or --input FILE[/red]")
    raise typer.Exit(code=1)


@app.command()
def anonymize(
    text: Optional[str] = typer.Argument(None, help="Text to anonymize."),
    input: Optional[Path] = typer.Option(None, "--input", "-i", help="Input file path."),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file path."),
    rules: Optional[Path] = typer.Option(None, "--rules", "-r", help="Custom operator rules YAML."),
    recognizers: Optional[Path] = typer.Option(None, "--recognizers", help="Custom recognizer registry YAML."),
):
    """Run the full anonymization pipeline on the input text."""
    raw = _read_input(text, input)
    rec_config = _get_recognizer_config(recognizers)
    op_config = _get_operator_config(rules)

    ctx = run(raw, rec_config, op_config)

    if output:
        output.write_text(ctx.engine_result.text, encoding="utf-8")
        console.print(f"[green]Anonymized output written to {output}[/green]")
    else:
        console.print(ctx.engine_result.text)


@app.command()
def analyze(
    text: Optional[str] = typer.Argument(None, help="Text to analyze."),
    input: Optional[Path] = typer.Option(None, "--input", "-i", help="Input file path."),
    explain: bool = typer.Option(False, "--explain", "-e", help="Show source and score reasoning."),
    recognizers: Optional[Path] = typer.Option(None, "--recognizers", help="Custom recognizer registry YAML."),
):
    """Run the analyzer only and show detected PII entities."""
    raw = _read_input(text, input)
    rec_config = _get_recognizer_config(recognizers)
    # Use a no-op operator config — we only need the analyzer results
    op_config = {"operators": {}}

    ctx = run(raw, rec_config, op_config)

    if not ctx.recognizer_results:
        console.print("[dim]No PII entities detected.[/dim]")
        return

    table = Table(title="Detected Entities")
    table.add_column("Entity Type", style="cyan")
    table.add_column("Text", style="yellow")
    table.add_column("Start", justify="right")
    table.add_column("End", justify="right")

    if explain:
        table.add_column("Score", justify="right", style="green")
        table.add_column("Source", style="magenta")

    for r in ctx.recognizer_results:
        row = [r.entity_type, r.text, str(r.start), str(r.end)]
        if explain:
            row.extend([f"{r.score:.2f}", r.source])
        table.add_row(*row)

    console.print(table)


if __name__ == "__main__":
    app()
