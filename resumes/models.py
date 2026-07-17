from django.conf import settings
from django.db import models


class Resume(models.Model):
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("generated", "Generated"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="resumes",
    )

    title = models.CharField(
        max_length=150,
        default="My Resume",
    )

    prompt = models.TextField()

    personal_details = models.JSONField(
        default=dict,
        blank=True,
    )

    professional_summary = models.TextField(
        blank=True,
    )

    skills = models.JSONField(
        default=list,
        blank=True,
    )

    education = models.JSONField(
        default=list,
        blank=True,
    )

    experience = models.JSONField(
        default=list,
        blank=True,
    )

    projects = models.JSONField(
        default=list,
        blank=True,
    )

    certifications = models.JSONField(
        default=list,
        blank=True,
    )

    languages = models.JSONField(
        default=list,
        blank=True,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return f"{self.title} - {self.user.username}"