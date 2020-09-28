import requests

class Request_API:
    def __init__(self, endpoint, method, payload=''):
        self.endpoint = endpoint
        self.method = method
        self.payload = payload

    def request_api(self):
        if str(self.method).upper() == "POST" and self.payload =='':
            raise Exception("Post without payload or empty payload not allowed buddy")
        elif str(self.method).upper() == 'GET':
            return requests.get(self.endpoint)
        else:
            return requests.post(self.endpoint, files=self.payload)