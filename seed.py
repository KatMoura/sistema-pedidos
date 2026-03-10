from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client
import os

ROOT_DIR = Path(__file__).resolve().parent
load_dotenv(ROOT_DIR / ".env", override=True)

url = (os.getenv("SUPABASE_URL") or "").strip().strip('"').strip("'")
key = (os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY") or "").strip().strip('"').strip("'")

sb = create_client(url, key)

# Remove produtos antigos
sb.table("produtos").delete().neq("id", 0).execute()
print("Produtos antigos removidos.")

produtos = [
    {"nome": "Mouse Gamer Logitech G203", "preco": 149.90},
    {"nome": "Mouse Pad XL Extended", "preco": 59.90},
    {"nome": "Teclado Mecânico Redragon", "preco": 279.90},
    {"nome": "Memória RAM 8GB DDR4", "preco": 189.90},
    {"nome": "Memória RAM 16GB DDR4", "preco": 329.90},
    {"nome": "SSD 480GB Kingston", "preco": 249.90},
    {"nome": "SSD 1TB Samsung 870", "preco": 449.90},
    {"nome": "Fone Headset HyperX Cloud", "preco": 399.90},
    {"nome": "Fone Bluetooth JBL Tune", "preco": 219.90},
    {"nome": "Webcam Full HD 1080p", "preco": 189.90},
    {"nome": "Cabo HDMI 2.0 2m", "preco": 39.90},
    {"nome": "Hub USB-C 7 em 1", "preco": 129.90},
]

for p in produtos:
    sb.table("produtos").insert(p).execute()
    print(f"  Inserido: {p['nome']} - R$ {p['preco']}")

print(f"\nSeed concluido! {len(produtos)} produtos inseridos.")