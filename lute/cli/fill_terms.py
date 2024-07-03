"""
Implementations for filling in the unknown terms from a book object in lute.
"""
import csv
import json
import logging
import os
import sys

from flask import (
    Blueprint,
    request,
    jsonify,
    render_template,
    redirect,
    flash,
)
from lute.utils.data_tables import DataTablesFlaskParamParser
from lute.book import service
from lute.book.datatables import get_data_tables_list
from lute.book.forms import NewBookForm, EditBookForm
import lute.utils.formutils
from lute.db import db

from lute.models.language import Language
from lute.term.model import Repository as TermRepo, Term as BusinessTerm
from lute.models.term import Term
from lute.models.book import Book as DBBook
from lute.book.model import Book, Repository


def fill_missing_terms(book_id):
    logging.info("Execute some logic here to parse the tokens and add them to the db")
    csv_language_dict = {
        "Mandarin": "/home/justin/Documents/Projects/language_toolbox/cc_cdict/lute_terms.csv",
        "Russian": "/home/justin/Documents/Projects/language_toolbox/cc_cdict/lute_russian_terms.csv",
    }
    book = DBBook.find(book_id)
    if book.language.name not in csv_language_dict:
        return False

    master_csv = csv_language_dict[book.language.name]
    for page in book.texts:
        parsed_tokens = [t.token for t in book.language.get_parsed_tokens(page.text)]
        logging.info(f"Got these tokens: {parsed_tokens}")
        parsed_tokens = _get_new_terms(book.language_id, parsed_tokens)
        logging.info(f"The following tokens are new: {parsed_tokens}")
        result = _add_terms(master_csv, book.language_id, parsed_tokens)
        logging.info("Attempted to add tokens")
        parsed_tokens = _get_new_terms(book.language_id, parsed_tokens)
        logging.info(f"The following tokens were not added: {parsed_tokens}")

    return True


def _get_new_terms(language_id: int, tokens: list[str]):
    repo = Repository(db)
    terms_matching_tokens = (
        db.session.query(Term)
        .filter(
            Term.language_id == language_id,
            Term.text_lc.in_(tokens),
            Term.token_count == 1,
        )
        .all()
    )
    existing_terms = [t.text for t in terms_matching_tokens]
    return [t for t in tokens if t not in existing_terms]


def _term_exists(language_id: int, term: str) -> bool:
    logging.info(f"Checking if the following term exists: {language_id} {term}")
    return _get_new_terms(language_id, [term]) == []

def _add_term(language_id: int, entry: str) -> bool:
    repo = TermRepo(db)
    term = BusinessTerm()
    term.language_id = language_id
    term.text = entry["term"]
    term.original_text = entry["term"]
    term.status = entry["status"]
    term.translation = entry["translation"]
    term.romanization = entry["pronunciation"]

    # db_term = repo._build_db_term(term)
    logging.info(f"Now adding the following term: {language_id} {term}")
    repo.add(term)
    repo.commit()
    return True


def _add_terms(csv_file_path: str, language_id: int, terms: list[str]):
    """
    Import only the lines from the CSV file representing the term definitions
    """
    # entry keys: language, term, translation, parent, status, tags, pronunciation
    csv_entries = []

    # get the csv lines representing all the terms
    for entry in read_csv(csv_file_path):
        if entry["term"] not in terms:
            continue
        csv_entries.append(entry)
        if len(csv_entries) == len(terms):
            break

    result = True
    for entry in csv_entries:
        if _term_exists(language_id, entry["term"]):
            continue

        if entry["parent"] and not _add_terms(csv_file_path, language_id, [entry["parent"]]):
            result = False

        if not _add_term(language_id, entry):
            logging.info(f"The token could not be added: {language_id}: {entry}")
            result = False

    return result


csv.field_size_limit(sys.maxsize)
def read_csv(file_path: str, delimiter: str = ","):
    with open(file_path, "r") as handle:
        csv_reader =  csv.DictReader(handle, delimiter=delimiter)
        for row in csv_reader:
            yield row
