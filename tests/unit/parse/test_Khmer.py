"""
Testing the KhmerParser class
"""
from lute.parse.base import ParsedToken


def assert_tokens_equals(text, lang, expected):
    """
    Parsing a text using a language should give the expected parsed tokens.
    expected is given as array of:
    [ original_text, is_word, is_end_of_sentence ]
    """
    p = lang.parser
    print("passing text:")
    print(text)
    actual = p.get_parsed_tokens(text, lang)
    expected = [ParsedToken(*a) for a in expected]
    assert [str(a) for a in actual] == [str(e) for e in expected]


def test_sample_1(khmer):
    "Sample text parsed."
    s = "ខ្ញុំរៀនភាសាខ្មែរ។"

    expected = [["ខ្ញុំ", True],
                ["រៀន", True],
                ["ភាសា", True],
                ["ខ្មែរ", True],
                ["។", False]]
    assert_tokens_equals(s, khmer, expected)
