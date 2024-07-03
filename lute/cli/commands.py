"""
Simple CLI commands.
"""

import click
from flask import Blueprint

from lute.cli.language_term_export import generate_file
from lute.cli.fill_terms import fill_missing_terms

bp = Blueprint("cli", __name__)

@bp.cli.command("fill_terms")
@click.argument("book_id")
def cmd_fill_terms(book_id):
    """
    Takes in a book ID and fills in the 
    """
    print(f"Filling in unknown terms for book: {book_id}")
    print(type(int(book_id)))
    return fill_missing_terms(book_id)

@bp.cli.command("hello")
def hello():
    "Say hello -- proof-of-concept CLI command only."
    msg = """
    Hello there!

    This is the Lute cli.

    There may be some experimental scripts here ...
    nothing that will change or damage your Lute data,
    but the CLI may change.

    Thanks for looking.
    """
    print(msg)


@bp.cli.command("language_export")
@click.argument("language")
@click.argument("output_path")
def language_export(language, output_path):
    """
    Get all terms from active books in the language, and write a
    data file of term frequencies and children.
    """
    generate_file(language, output_path)
