from django.http import JsonResponse


def home(request):
    return JsonResponse(
        {
            "message": "AI Resume Generator Backend is running",
            "status": "success",
        }
    )