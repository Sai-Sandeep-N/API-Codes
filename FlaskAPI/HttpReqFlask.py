import requests

url = "http://127.0.0.1:5000/books/"

for i in range(1,3):
    # POST REQ
    data = {
        "book": {
            "title": f"sample{i}",
            "pages": i
        },
        "author": {
            "firstname": f"fauthor{i}",
            "lastname": f"lauthor{i}"
        }
    }
    response = requests.post(url, json=data)
    print(f"Response Body: {response.text}")
    print("-"* 50)
 