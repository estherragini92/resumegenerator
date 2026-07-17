import json
import os

import requests
from requests.exceptions import ConnectionError, RequestException, Timeout
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from resumes.models import Resume
from resumes.serializers import ResumeSerializer


class GenerateResumeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user_prompt = request.data.get("prompt", "").strip()

        if not user_prompt:
            return Response(
                {"error": "Prompt is required."},
                status=400,
            )

        # Ollama should run only when it is enabled.
        if os.getenv("OLLAMA_ENABLED", "False").lower() != "true":
            return Response(
                {
                    "error": (
                        "AI generation is available only in the local demo "
                        "version. The deployed backend is not connected to "
                        "an online AI model."
                    )
                },
                status=503,
            )

        instruction = f"""
You are a professional ATS-friendly resume writer.

Create a professional resume using only the user information.

Rules:
1. Do not invent personal information.
2. Leave missing values empty.
3. Return only valid JSON.
4. Do not use markdown or code fences.
5. Improve the professional summary and project descriptions.
6. Use clear and professional language.
7. Do not invent education, experience, dates, companies, or institutions.

Return exactly this JSON structure:

{{
  "title": "",
  "personal_details": {{
    "name": "",
    "job_title": "",
    "email": "",
    "phone": "",
    "location": "",
    "linkedin": "",
    "github": ""
  }},
  "professional_summary": "",
  "skills": [],
  "education": [],
  "experience": [],
  "projects": [],
  "certifications": [],
  "languages": []
}}

User information:

{user_prompt}
"""

        generated_text = ""

        try:
            ollama_response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "gemma3:4b",
                    "prompt": instruction,
                    "format": "json",
                    "stream": False,
                },
                timeout=600,
            )

            ollama_response.raise_for_status()

            ollama_data = ollama_response.json()
            generated_text = ollama_data.get("response", "").strip()

            if not generated_text:
                return Response(
                    {"error": "Ollama returned an empty response."},
                    status=502,
                )

            generated_resume = json.loads(generated_text)

            resume = Resume.objects.create(
                user=request.user,
                title=(
                    generated_resume.get("title")
                    or "AI Generated Resume"
                ),
                prompt=user_prompt,
                personal_details=generated_resume.get(
                    "personal_details",
                    {},
                ),
                professional_summary=generated_resume.get(
                    "professional_summary",
                    "",
                ),
                skills=generated_resume.get("skills", []),
                education=generated_resume.get("education", []),
                experience=generated_resume.get("experience", []),
                projects=generated_resume.get("projects", []),
                certifications=generated_resume.get(
                    "certifications",
                    [],
                ),
                languages=generated_resume.get("languages", []),
                status="generated",
            )

            return Response(
                {
                    "message": "Resume generated successfully.",
                    "resume": ResumeSerializer(resume).data,
                },
                status=201,
            )

        except ConnectionError:
            return Response(
                {
                    "error": (
                        "Cannot connect to Ollama. Open the Ollama "
                        "application or run 'ollama serve'."
                    )
                },
                status=503,
            )

        except Timeout:
            return Response(
                {
                    "error": (
                        "Ollama took too long to respond. "
                        "Try using a shorter prompt."
                    )
                },
                status=504,
            )

        except json.JSONDecodeError:
            return Response(
                {
                    "error": "Ollama returned invalid JSON.",
                    "raw_response": generated_text,
                },
                status=502,
            )

        except RequestException as error:
            return Response(
                {
                    "error": f"Ollama request failed: {str(error)}"
                },
                status=500,
            )

        except Exception as error:
            return Response(
                {
                    "error": f"Unexpected error: {str(error)}"
                },
                status=500,
            )