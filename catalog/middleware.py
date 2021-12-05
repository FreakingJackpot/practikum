from forms import RequestForm


class RequestFormMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == 'POST':
            data = RequestForm(request.POST)
            if data.is_valid():
                data.save()

        response = self.get_response(request)

        return response
