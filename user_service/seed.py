import requests

BASE = "http://localhost:5001"

usuarios = [
    {"nome": "Alice", "email": "alice@example.com"},
    {"nome": "Bob", "email": "bob@example.com"},
    {"nome": "Carol", "email": "carol@example.com"}
]

if __name__ == '__main__':
    for u in usuarios:
        r = requests.post(f"{BASE}/api/usuarios", json=u)
        print(r.status_code, r.json())
