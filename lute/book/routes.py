"""
/book routes.
"""
import csv
import json
import logging
import os

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


bp = Blueprint("book", __name__, url_prefix="/book")


def datatables_source(is_archived):
    "Get datatables json for books."
    parameters = DataTablesFlaskParamParser.parse_params(request.form)
    data = get_data_tables_list(parameters, is_archived)
    return jsonify(data)


@bp.route("/datatables/active", methods=["POST"])
def datatables_active_source():
    "Datatables data for active books."
    return datatables_source(False)


@bp.route("/archived", methods=["GET"])
def archived():
    "List archived books."
    return render_template("book/index.html", status="Archived")


# Archived must be capitalized, or the ajax call 404's.
@bp.route("/datatables/Archived", methods=["POST"])
def datatables_archived_source():
    "Datatables data for archived books."
    return datatables_source(True)


def _get_file_content(filefielddata):
    """
    Get the content of the file.
    """
    _, ext = os.path.splitext(filefielddata.filename)
    ext = (ext or "").lower()
    if ext == ".txt":
        return service.get_textfile_content(filefielddata)
    if ext == ".epub":
        return service.get_epub_content(filefielddata)
    if ext == ".pdf":
        msg = """
        Note: pdf imports can be inaccurate, due to how PDFs are encoded.
        Please be aware of this while reading.
        """
        flash(msg, "notice")
        return service.get_pdf_content_from_form(filefielddata)
    raise ValueError(f'Unknown file extension "{ext}"')


def _book_from_url(url):
    "Create a new book, or flash an error if can't parse."
    b = Book()
    try:
        b = service.book_from_url(url)
    except service.BookImportException as e:
        flash(e.message, "notice")
        b = Book()
    return b


def _language_is_rtl_map():
    """
    Return language-id to is_rtl map, to be used during book creation.
    """
    ret = {}
    for lang in db.session.query(Language).all():
        ret[lang.id] = lang.right_to_left
    return ret


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


def read_csv(file_path: str, delimiter: str = ","):
    with open(file_path, "r") as handle:
        csv_reader =  csv.DictReader(handle, delimiter=delimiter)
        for row in csv_reader:
            yield row


@bp.route("/new", methods=["GET", "POST"])
def new():
    "Create a new book, either from text or from a file."
    logging.info("Making the new book now")
    b = Book()
    import_url = request.args.get("importurl", "").strip()
    if import_url != "":
        b = _book_from_url(import_url)

    form = NewBookForm(obj=b)
    form.language_id.choices = lute.utils.formutils.language_choices()
    max_page_tokens = form.data['max_page_tokens']
    repo = Repository(db)

    if form.validate_on_submit():
        try:
            form.populate_obj(b)
            if form.textfile.data:
                b.text = _get_file_content(form.textfile.data)
            f = form.audiofile.data
            if f:
                b.audio_filename = service.save_audio_file(f)
            book = repo.add(b)
            repo.commit()

            # All this code is related to the definition auto-adder
            logging.info("Execute some logic here to parse the tokens and add them to the db")

            for page in book.texts:
                parsed_tokens = [t.token for t in book.language.get_parsed_tokens(page.text)]
                logging.info(f"Got these tokens: {parsed_tokens}")
                parsed_tokens = _get_new_terms(book.language_id, parsed_tokens)
                logging.info(f"The following tokens are new: {parsed_tokens}")
                result = _add_terms("/home/justin/Documents/Repos/language_toolbox/cc_cdict/lute_terms.csv",
                                    book.language_id, parsed_tokens)
                logging.info("Attempted to add tokens")
                parsed_tokens = _get_new_terms(book.language_id, parsed_tokens)
                logging.info(f"The following tokens were not added: {parsed_tokens}")
            # End of definition auto-adder code
            return redirect(f"/read/{book.id}/page/1", 302)
        except service.BookImportException as e:
            flash(e.message, "notice")

    return render_template(
        "book/create_new.html",
        book=b,
        form=form,
        tags=repo.get_book_tags(),
        rtl_map=json.dumps(_language_is_rtl_map()),
        show_language_selector=True,
    )


@bp.route("/edit/<int:bookid>", methods=["GET", "POST"])
def edit(bookid):
    "Edit a book - can only change a few fields."
    repo = Repository(db)
    b = repo.load(bookid)
    form = EditBookForm(obj=b)

    if form.validate_on_submit():
        form.populate_obj(b)
        f = form.audiofile.data
        if f:
            b.audio_filename = service.save_audio_file(f)
            b.audio_bookmarks = None
            b.audio_current_pos = None
        repo.add(b)
        repo.commit()
        flash(f"{b.title} updated.")
        return redirect("/", 302)

    lang = Language.find(b.language_id)
    return render_template(
        "book/edit.html",
        book=b,
        title_direction="rtl" if lang.right_to_left else "ltr",
        form=form,
        tags=repo.get_book_tags(),
    )


@bp.route("/import_webpage", methods=["GET", "POST"])
def import_webpage():
    return render_template("book/import_webpage.html")


@bp.route("/archive/<int:bookid>", methods=["POST"])
def archive(bookid):
    "Archive a book."
    b = DBBook.find(bookid)
    b.archived = True
    db.session.add(b)
    db.session.commit()
    return redirect("/", 302)


@bp.route("/unarchive/<int:bookid>", methods=["POST"])
def unarchive(bookid):
    "Archive a book."
    b = DBBook.find(bookid)
    b.archived = False
    db.session.add(b)
    db.session.commit()
    return redirect("/", 302)


@bp.route("/delete/<int:bookid>", methods=["POST"])
def delete(bookid):
    "Archive a book."
    b = DBBook.find(bookid)
    db.session.delete(b)
    db.session.commit()
    return redirect("/", 302)
