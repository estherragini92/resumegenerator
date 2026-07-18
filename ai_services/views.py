import json
import os

from groq import Groq
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

        groq_api_key = os.getenv("GROQ_API_KEY")

        if not groq_api_key:
            return Response(
                {"error": "GROQ_API_KEY is missing."},
                status=500,
            )

        instruction = f"""
You are a professional ATS-friendly resume writer.

Create a professional resume using only the information supplied by the user.

Rules:
1. Do not invent personal information.
2. Leave missing values empty.
3. Do not invent companies, institutions, dates, qualifications, or experience.
4. Improve the professional summary and project descriptions.
5. Return only valid JSON.
6. Do not include markdown or code fences.

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
            client = Groq(api_key=groq_api_key)

            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You generate professional ATS-friendly resumes "
                            "and return only valid JSON."
                        ),
                    },
                    {
                        "role": "user",
                        "content": instruction,
                    },
                ],
                temperature=0.3,
                response_format={
                    "type": "json_object",
                },
            )

            generated_text = (
                response.choices[0].message.content or ""
            ).strip()

            if not generated_text:
                return Response(
                    {"error": "Groq returned an empty response."},
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

        except json.JSONDecodeError:
            return Response(
                {
                    "error": "Groq returned invalid JSON.",
                    "raw_response": generated_text,
                },
                status=502,
            )

        except Exception as error:
            return Response(
                {
                    "error": str(error),
                },
                status=500,
            )