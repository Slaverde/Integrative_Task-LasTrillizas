"""The diagrams and sizes of docs/normalization-transducers.md come from the code."""

from pathlib import Path

import pytest

from src.normalization.diagrams import blocks, main, mermaid_compact, summary
from src.normalization.fst import build_cleaner
from src.normalization.transducers import all_transducers, languages_transducer

DOC = Path(__file__).resolve().parents[1] / "docs" / "normalization-transducers.md"


@pytest.fixture(scope="module")
def doc_text() -> str:
    return DOC.read_text(encoding="utf-8")


@pytest.mark.parametrize("name", ["counts", "cleaner", "languages", "frameworks", "databases_tools"])
def test_the_document_contains_the_generated_block(name, doc_text):
    assert blocks()[name] in doc_text, (
        f"docs/normalization-transducers.md is out of date for {name}: "
        f"run `python -m src.normalization.diagrams {name}` and paste the block"
    )


def test_the_document_lists_every_key_of_every_transducer(doc_text):
    from src.normalization.variants import GROUPS, key_map

    for group in GROUPS.values():
        for key in key_map(group):
            assert f"`{key}`" in doc_text, key


def test_summary_counts_of_the_cleaner():
    counts = summary(build_cleaner())
    assert counts["states"] == 1
    assert counts["final_states"] == 1
    # one loop per symbol of the input alphabet
    assert counts["transitions"] == counts["input_symbols"]


def test_summary_of_a_prefix_tree_is_a_tree_plus_shared_final_states():
    for name, fst in all_transducers().items():
        counts = summary(fst)
        # every state except q0 has exactly one way in, except the final
        # states, which are reached once per spelling of the token
        assert counts["transitions"] >= counts["states"] - 1, name
        assert counts["final_states"] == counts["output_symbols"], name


def test_the_compact_diagram_draws_start_final_and_branching_states():
    diagram = mermaid_compact(languages_transducer())
    assert diagram.startswith("flowchart LR")
    assert '(("q0"))' in diagram  # initial state
    assert '((("f:JAVASCRIPT")))' in diagram  # final state: double circle
    assert '"p:JAVA"' in diagram  # JAVA is a prefix of JAVASCRIPT: it branches
    assert "SCRIPT⊣ / JAVASCRIPT" in diagram  # a folded chain of states
    assert "p:JAVAS" not in diagram  # it was folded into an edge


def test_the_compact_diagram_loses_no_output():
    for fst in all_transducers().values():
        diagram = mermaid_compact(fst)
        for symbol in fst.output_symbols:
            assert f"/ {symbol}" in diagram


def test_the_command_line_prints_a_known_block(capsys):
    assert main(["languages"]) == 0
    printed = capsys.readouterr().out
    assert "flowchart LR" in printed
    assert "JAVASCRIPT" in printed


def test_the_command_line_rejects_an_unknown_name(capsys):
    assert main(["nothing"]) == 2
    assert "unknown transducer" in capsys.readouterr().out
