import requests


class PlateClient:
    def __init__(self, url: str, ):
        self.url = url

    def readNumber(self, im):
        res = requests.post(f'{self.url}/readNumber', 
            headers={'Content-Type': 'application/x-www-form-urlencoded'}, 
            data=im,
        )

        return res.json()['name']

    def upper():
        pass


if __name__ == '__main__':
    client = PlateClient('http://127.0.0.1:8080')
    with open('images/10022.jpg', 'rb') as im:
        res = client.readNumber(im)
    
    print(res)
