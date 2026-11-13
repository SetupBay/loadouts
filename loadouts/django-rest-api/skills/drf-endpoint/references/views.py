from rest_framework import permissions, viewsets

from notes.models import Note
from notes.serializers import NoteSerializer


class NoteViewSet(viewsets.ModelViewSet):
    """Notes belong to one user. Every query is scoped to request.user, so other users' notes are a 404."""

    serializer_class = NoteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Note.objects.filter(owner=self.request.user).select_related("owner").order_by("-created_at", "-id")

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
