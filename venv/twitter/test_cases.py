import requests
import unittest

url = "http://127.0.0.1:5000/"

headers = {
    'User-Agent': "PostmanRuntime/7.18.0",
    'Accept': "*/*",
    'Cache-Control': "no-cache",
    'Postman-Token': "48bfc273-2cb5-42ab-82c5-51e1641d265e,0239b1b1-165b-4cf7-9bd3-847e0d5db04a",
    'Host': "127.0.0.1:5000",
    'Accept-Encoding': "gzip, deflate",
    'Connection': "keep-alive",
    'cache-control': "no-cache"
    }

response = requests.request("GET", url, headers=headers)

df=response.status_code


class TestStringMethods(unittest.TestCase):

    def test_upper(self):
        self.assertEqual(df, 400)



if __name__ == '__main__':
    unittest.main()