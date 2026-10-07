from pathlib import Path

from src.extraction import extract
from src.extraction.skills import extract_databases, extract_frameworks, extract_languages

RESUMES = Path(__file__).resolve().parent.parent / "examples" / "resumes"


def read_resume(name: str) -> str:
    return (RESUMES / name).read_text(encoding="utf-8")


def test_language_variants_are_kept_as_written():
    text = "JS, Javascript, Java Script, TypeScript, TS, Python3, C++, C#, Kotlin, PHP"
    assert extract_languages(text) == [
        "JS",
        "Javascript",
        "Java Script",
        "TypeScript",
        "TS",
        "Python3",
        "C++",
        "C#",
        "Kotlin",
        "PHP",
    ]


def test_java_is_not_found_inside_javascript():
    assert extract_languages("Javascript only") == ["Javascript"]
    assert extract_languages("Java and JavaScript") == ["Java", "JavaScript"]


def test_duplicates_ignore_case_and_keep_first_spelling():
    assert extract_languages("JS ... js ... Js") == ["JS"]


def test_capitalized_languages_are_case_sensitive():
    assert extract_languages("Swift and Rust, but not swift or rust") == ["Swift", "Rust"]


def test_framework_variants_are_kept_as_written():
    text = "React, React.js, ReactJS, NodeJS, Node.js, Node JS, Vue.js, Angular, Spring Boot"
    assert extract_frameworks(text) == [
        "React",
        "React.js",
        "ReactJS",
        "NodeJS",
        "Node.js",
        "Node JS",
        "Vue.js",
        "Angular",
        "Spring Boot",
    ]


def test_ml_library_variants():
    text = "sklearn, scikit learn, Scikit-learn, Tensor Flow, TensorFlow, Py Torch, PyTorch, pandas, NumPy"
    assert extract_frameworks(text) == [
        "sklearn",
        "scikit learn",
        "Scikit-learn",
        "Tensor Flow",
        "TensorFlow",
        "Py Torch",
        "PyTorch",
        "pandas",
        "NumPy",
    ]


def test_js_inside_a_framework_is_not_a_language():
    text = "Node JS, React.js, NodeJS"
    assert extract_languages(text) == []
    assert extract_frameworks(text) == ["Node JS", "React.js", "NodeJS"]


def test_node_without_js_is_not_a_framework():
    assert extract_frameworks("a tree node and a graph node") == []


def test_database_variants():
    text = "Postgres, PostgreSQL, Postgre SQL, MySQL, Mongo DB, MongoDB, SQL Server, SQLite, NoSQL, SQL"
    assert extract_databases(text) == [
        "Postgres",
        "PostgreSQL",
        "Postgre SQL",
        "MySQL",
        "Mongo DB",
        "MongoDB",
        "SQL Server",
        "SQLite",
        "NoSQL",
        "SQL",
    ]


def test_sql_is_not_found_inside_other_databases():
    assert extract_databases("PostgreSQL") == ["PostgreSQL"]
    assert extract_databases("MySQL, NoSQL") == ["MySQL", "NoSQL"]


def test_sentence_final_period_is_not_part_of_the_match():
    assert extract_frameworks("Skills: JS, React.js, NodeJS.") == ["React.js", "NodeJS"]


def test_text_without_skills():
    text = "I enjoy hiking and cooking."
    assert extract_languages(text) == []
    assert extract_frameworks(text) == []
    assert extract_databases(text) == []


def test_wednesday_addams_resume():
    result = extract(read_resume("wednesday_addams.txt"))
    assert result.languages == ["JS"]
    assert result.frameworks == ["React.js", "NodeJS"]
    assert result.databases == ["Postgres"]


def test_mary_jane_watson_resume():
    result = extract(read_resume("mary_jane_watson.txt"))
    assert result.languages == ["Python"]
    assert result.frameworks == ["Pandas", "NumPy", "Scikit-learn", "TensorFlow"]
    assert result.databases == ["SQL"]
