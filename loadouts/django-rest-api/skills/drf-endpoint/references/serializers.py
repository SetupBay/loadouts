from rest_framework import serializers

from notes.models import Note


class NoteSerializer(serializers.ModelSerializer):
    # Explicit fields: a new model column never leaks into the API by accident.
    owner = serializers.CharField(source="owner.username", read_only=True)

    class Meta:
        model = Note
        fields = ["id", "title", "body", "owner", "created_at"]
        read_only_fields = ["id", "owner", "created_at"]

    def validate_title(self, value: str) -> str:
        value = value.strip()
        if len(value) < 3:
            raise serializers.ValidationError("Title must be at least 3 characters.")
        return value
