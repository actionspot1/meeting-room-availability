from django.http import HttpResponse, HttpRequest


def handle_error(
    req: HttpRequest,
    error: Exception,
    location: str,
    status_code: int = 500,
) -> HttpResponse:
    print(f"An error occurred: {str(error)}")
    print("location: ", location)
    return HttpResponse(str(error), status=status_code)
