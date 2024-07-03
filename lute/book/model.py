"""
Book domain objects.
"""
import logging

from lute.models.book import Book as DBBook, BookTag
from lute.models.language import Language
from lute.termimport.service import import_file


class Book:  # pylint: disable=too-many-instance-attributes
    """
    A book domain object, to create/edit lute.models.book.Books.
    """

    def __init__(self):
        self.id = None
        self.language_id = None
        self.title = None
        self.text = None
        self.max_page_tokens = 250
        self.source_uri = None
        self.audio_filename = None
        self.audio_current_pos = None
        self.audio_bookmarks = None
        self.book_tags = []

    def __repr__(self):
        return f"<Book (id={self.id}, title='{self.title}')>"

    def add_tag(self, tag):
        self.book_tags.append(tag)


def read_csv_terms(file_path, delimiter=","):
    pass 

def cant_find(term: str):
    return True

def add_mandarin_definitions(tokens: list[str]):
    logging.info("Adding definition for non-existant mandarin definitions")
    new_tokens = [t for t in tokens if cant_find(t)]
    if not new_tokens:
        logging.info("No new tokens to add")
        return True

    logging.info(f"Found the following new tokens: {new_tokens}")

    # Iterate through giant master CSV file
    # if the term of the line is in the new_tokens list, then add the line to a temp csv
    new_entries = []
    giant_csv = []
    for entry in giant_csv:
        if entry["term"] not in new_tokens:
            continue
        new_entries.append(entry["term"])

    # Write to temporary CSV file and import it
    if not new_entries:
        logging.info("No new terms to add, doing nothing")
        return False
    tmp_file = "temp.csv"
    logging.info("Writing the following terms to a file: {new_terms}")
    breakpoint()
    return True

def add_russian_definitions(tokens):
    logging.info("Adding definition for non-existant russian definitions")
    return False


class Repository:
    """
    Maps Book BO to and from lute.model.Book.
    """

    def __init__(self, _db):
        self.db = _db

    def load(self, book_id):
        "Loads a Book business object for the DBBook."
        dbb = DBBook.find(book_id)
        if dbb is None:
            raise ValueError(f"No book with id {book_id} found")
        return self._build_business_book(dbb)

    def get_book_tags(self):
        "Get all available book tags, helper method."
        bts = self.db.session.query(BookTag).all()
        return [t.text for t in bts]

    def add(self, book):
        """
        Add a book to be saved to the db session.
        Returns DBBook for tests and verification only,
        clients should not change it.
        """
        dbbook = self._build_db_book(book)
        self.db.session.add(dbbook)
        return dbbook
        
        # All this code is related to the definition auto-adder
        logging.info("Execute some logic here to parse the tokens and add them to the db")
        _language_finders = {
            "Mandarin": add_mandarin_definitions,
            "Russian": add_russian_definitions,
        }
        term_function = _language_finders.get(dbbook.language.name, None)
        if term_function is None:
            return dbbook

        for page in dbbook.texts:
            parsed_tokens = dbbook.language.get_parsed_tokens(page.text)
            term_function(parsed_tokens)
            breakpoint()

        # End of definition auto-adder code
        return dbbook

    def delete(self, book):
        """
        Delete.
        """
        if book.id is None:
            raise ValueError(f"book {book.title} not saved")
        b = DBBook.find(book.id)
        self.db.session.delete(b)

    def commit(self):
        """
        Commit everything.
        """
        self.db.session.commit()

    def _build_db_book(self, book):
        "Convert a book business object to a DBBook."

        lang = Language.find(book.language_id)

        b = None
        if book.id is None:
            b = DBBook.create_book(book.title, lang, book.text, book.max_page_tokens)
        else:
            b = DBBook.find(book.id)
        b.title = book.title
        b.source_uri = book.source_uri
        b.audio_filename = book.audio_filename
        b.audio_current_pos = book.audio_current_pos
        b.audio_bookmarks = book.audio_bookmarks

        booktags = []
        for s in book.book_tags:
            booktags.append(BookTag.find_or_create_by_text(s))
        b.remove_all_book_tags()
        for tt in booktags:
            b.add_book_tag(tt)

        return b

    def _build_business_book(self, dbbook):
        "Convert db book to Book."
        b = Book()
        b.id = dbbook.id
        b.language_id = dbbook.language.id
        b.title = dbbook.title
        b.text = None  # Not returning this for now
        b.source_uri = dbbook.source_uri
        b.audio_filename = dbbook.audio_filename
        b.audio_current_pos = dbbook.audio_current_pos
        b.audio_bookmarks = dbbook.audio_bookmarks
        b.book_tags = [t.text for t in dbbook.book_tags]
        return b
