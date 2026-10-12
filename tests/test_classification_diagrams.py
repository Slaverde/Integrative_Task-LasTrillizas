"""The diagrams and sizes of docs/classification-automata.md come from the code."""

from pathlib import Path

import pytest

from src.classification.automata import build_full_stack_developer
from src.classification.diagrams import (
    AUTOMATA_BUILDERS,
    blocks,
    main,
    mermaid,
    required_path,
    summary,
)

DOC = Path(__file__).resolve().parents[1] / "docs" / "classification-automata.md"


@pytest.fixture(scope="module")
def doc_text() -> str:
    return DOC.read_text(encoding="utf-8")


@pytest.mark.parametrize(
    "name",
    ["counts", "full_stack_developer", "machine_learning_engineer", "backend_developer", "data_scientist"],
)
def test_the_document_contains_the_generated_block(name, doc_text):
    assert blocks()[name] in doc_text, (
        f"docs/classification-automata.md is out of date for {name}: "
        f"run `python -m src.classification.diagrams {name}` and paste the block"
    )


def test_every_automaton_is_total():
    for builder in AUTOMATA_BUILDERS.values():
        dfa = builder()
        counts = summary(dfa)
        assert counts["transitions"] == counts["states"] * counts["input_symbols"]


def test_required_path_matches_the_required_categories_lists():
    from src.classification.automata import (
        BACKEND_DEVELOPER_REQUIRED,
        DATA_SCIENTIST_REQUIRED,
        FULL_STACK_REQUIRED,
        MACHINE_LEARNING_ENGINEER_REQUIRED,
        build_backend_developer,
        build_data_scientist,
        build_machine_learning_engineer,
    )

    cases = [
        (build_full_stack_developer(), FULL_STACK_REQUIRED),
        (build_machine_learning_engineer(), MACHINE_LEARNING_ENGINEER_REQUIRED),
        (build_backend_developer(), BACKEND_DEVELOPER_REQUIRED),
        (build_data_scientist(), DATA_SCIENTIST_REQUIRED),
    ]
    for dfa, required in cases:
        categories = [category for _, category, _ in required_path(dfa)]
        assert categories == [c.value for c in required]


def test_the_diagram_draws_start_final_and_every_required_edge():
    diagram = mermaid(build_full_stack_developer())
    assert diagram.startswith("flowchart LR")
    assert '(("q0"))' in diagram  # initial state
    assert '((("q5")))' in diagram  # final state: double circle
    assert '|"LANGUAGE"| q1' in diagram
    assert '|"VERSION_CONTROL"| q5' in diagram
    assert '|"any category"| q5' in diagram  # final state's own self-loop label


def test_the_command_line_prints_a_known_block(capsys):
    assert main(["full_stack_developer"]) == 0
    printed = capsys.readouterr().out
    assert "flowchart LR" in printed
    assert "LANGUAGE" in printed


def test_the_command_line_rejects_an_unknown_name(capsys):
    assert main(["nothing"]) == 2
    assert "unknown automaton" in capsys.readouterr().out
