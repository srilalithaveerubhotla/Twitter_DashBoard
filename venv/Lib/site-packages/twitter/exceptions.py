class TwitterException(Exception):
    status_code = None
    api_code = None
    message = None
    response = None

    def __init__(self, code, response):
        self.status_code = code
        self.response = response

        if 'errors' in response:
            self.message = response['errors'][0]['message']
            self.api_code = response['errors'][0]['code']
