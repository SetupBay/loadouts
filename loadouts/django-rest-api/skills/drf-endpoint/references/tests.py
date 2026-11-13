from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from notes.models import Note

User = get_user_model()


class NoteApiTests(APITestCase):
    def setUp(self):
        self.ada = User.objects.create_user("ada", password="test-only-pass")
        self.bob = User.objects.create_user("bob", password="test-only-pass")
        self.bobs_note = Note.objects.create(owner=self.bob, title="Bob's plan", body="private")

    def test_anonymous_requests_are_rejected(self):
        response = self.client.get("/api/notes/")
        self.assertIn(response.status_code, {status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN})

    def test_create_sets_owner_from_the_request_not_the_body(self):
        self.client.force_authenticate(self.ada)
        response = self.client.post("/api/notes/", {"title": "  Shopping ", "body": "milk", "owner": "bob"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["owner"], "ada")
        self.assertEqual(response.data["title"], "Shopping")

    def test_list_only_shows_own_notes(self):
        Note.objects.create(owner=self.ada, title="Ada's note", body="")
        self.client.force_authenticate(self.ada)
        response = self.client.get("/api/notes/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([n["title"] for n in response.data["results"]], ["Ada's note"])

    def test_other_users_note_is_not_found(self):
        self.client.force_authenticate(self.ada)
        for method in ("get", "patch", "delete"):
            response = getattr(self.client, method)(f"/api/notes/{self.bobs_note.pk}/")
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, method)
        self.assertTrue(Note.objects.filter(pk=self.bobs_note.pk).exists())

    def test_validation_errors_name_the_field(self):
        self.client.force_authenticate(self.ada)
        response = self.client.post("/api/notes/", {"title": "x", "body": ""})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("title", response.data)

    def test_list_query_count_does_not_grow_with_rows(self):
        for i in range(5):
            Note.objects.create(owner=self.ada, title=f"Note {i}", body="")
        self.client.force_authenticate(self.ada)
        # One count query for pagination, one select with the owner joined.
        with self.assertNumQueries(2):
            self.client.get("/api/notes/")
