"""Query-count test: a list of books with authors must not issue one query per book (N+1).

Adapt the app, model and function names. Uses Django's TestCase.assertNumQueries.
"""

from django.test import TestCase

from shop.models import Author, Book
from shop.queries import book_titles_with_authors


class BookListQueries(TestCase):
    @classmethod
    def setUpTestData(cls):
        for i in range(5):
            author = Author.objects.create(name=f"Author {i}")
            Book.objects.create(title=f"Book {i}", author=author)

    def test_one_query_for_any_number_of_books(self):
        with self.assertNumQueries(1):
            rows = book_titles_with_authors()
        self.assertEqual(len(rows), 5)
        self.assertEqual(rows[0], ("Book 0", "Author 0"))
