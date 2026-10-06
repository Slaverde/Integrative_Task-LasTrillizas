from src.vocabulary import PROFILE_ORDER, TOKENS, Category, Profile


def test_every_profile_has_an_order():
    assert set(PROFILE_ORDER) == set(Profile)


def test_profile_orders_have_no_repeated_categories():
    for profile, order in PROFILE_ORDER.items():
        assert len(order) == len(set(order)), profile


def test_tokens_are_uppercase_identifiers():
    for token in TOKENS:
        assert token == token.upper()
        assert token.replace("_", "").isalnum(), token


def test_every_token_category_is_used_by_some_profile():
    used = {c for order in PROFILE_ORDER.values() for c in order}
    for token, category in TOKENS.items():
        assert category in used, token


def test_example_from_the_assignment_categories():
    assert TOKENS["JAVASCRIPT"] == Category.LANGUAGE
    assert TOKENS["POSTGRESQL"] == Category.DATABASE
    assert TOKENS["GIT"] == Category.VERSION_CONTROL
