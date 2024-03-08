import requests

url = "http://127.0.0.1:8000/book/"
for i in range(1,3):
    data = {
        "book": {
            "title": f"sample{i}",
            "number_of_pages": i
        },
        "author": {
            "first_name": f"fauthor{i}",
            "last_name": f"lauthor{i}"
        }
    }
    response = requests.post(url, json=data)
    print(f"Response Body: {response.text}")
    print("-" * 50)


    