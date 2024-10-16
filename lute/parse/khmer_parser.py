"""
Uses khmernltk to parse khmer words as tokens
https://github.com/VietHoang1512/khmer-nltk
"""
from typing import List
from functools import lru_cache
import logging

import khmernltk as kh

from lute.parse.base import AbstractParser
from lute.parse.base import ParsedToken


KH_SYMBOLS = kh.utils.constants.KHSYM.union(kh.utils.constants.KHNUMBER)


class KhmerParser(AbstractParser):
    """
    Parses Khmer using the khmernltk library
    """
    @classmethod
    def is_supported(cls):
        return True

    @classmethod
    def name(cls):
        return "Khmer"

    @lru_cache()
    def parse_para(self, para_text):
        """
        Parsing the paragraph
        """
        para_result = []
        for tok in kh.word_tokenize(para_text):
            is_word = tok not in KH_SYMBOLS
            para_result.append((tok, is_word))

        return para_result

    @lru_cache()
    def get_parsed_tokens(self, text: str, language) -> List:
        """
        Parsing the text by paragraph, then generate the ParsedToken List,
        for the correct token order.
        cached the parsed result
        """
        tokens = []
        for para in text.split("\n"):
            para = para.strip()
            tokens.extend(self.parse_para(para))
            tokens.append(["¶", False])

        # Remove the trailing ¶ by stripping it from the result
        tokens.pop()

        return [ParsedToken(tok, is_word, tok == "¶") for tok, is_word in tokens]
