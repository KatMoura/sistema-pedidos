import requests

BASE = "http://localhost:5000"

produtos = [
    {"nome": "Notebook Dell Inspiron", "preco": 3599.90},
    {"nome": "Mouse Wireless Logitech", "preco": 129.90},
    {"nome": "Teclado Mecânico Redragon", "preco": 289.90},
    {"nome": "Monitor LED 24\" Samsung", "preco": 899.90},
    {"nome": "Headset Gamer HyperX", "preco": 349.90},
    {"nome": "Webcam Logitech C920", "preco": 429.90},
    {"nome": "SSD 1TB Kingston", "preco": 399.90},
    {"nome": "Memória RAM 16GB", "preco": 289.90}
]

if __name__ == '__main__':
    for p in produtos:
        r = requests.post(f"{BASE}/api/produtos", json=p)
        print(r.status_code, r.json())
