from rest_framework import serializers

from .models import Resume


class ResumeSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Resume
        fields = [
            "id",
            "user",
            "title",
            "prompt",
            "personal_details",
            "professional_summary",
            "skills",
            "education",
            "experience",
            "projects",
            "certifications",
            "languages",
            "status",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "user",
            "created_at",
            "updated_at",
        ]