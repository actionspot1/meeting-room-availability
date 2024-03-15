from django.http import HttpResponse, HttpRequest


def handle_error(
    req: HttpRequest, error: Exception, status_code: int = 500
) -> HttpResponse:
    print(f"An error occurred: {str(error)}")
    return HttpResponse(str(error), status=status_code)
