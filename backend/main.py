"""
Sistema de Pedidos - Backend FastAPI
Implementa o padrao Observer para notificacoes em tempo real.
Integra com Supabase para persistencia de dados quando configurado.
"""

import time
from datetime import datetime

import fastapi
import fastapi.middleware.cors
from pydantic import BaseModel

from observer import (
    Pedido,
    Produto,
    EmailObserver,
    LogObserver,
    TelaObserver,
    KitchenObserver,
    AnalyticsObserver,
)
from db import get_supabase_client

app = fastapi.FastAPI(title="Sistema de Pedidos - Observer Pattern")

app.add_middleware(
    fastapi.middleware.cors.CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Dados em memoria (simula banco de dados) ---
pedidos_ativos: dict[int, dict] = {}
pedidos_finalizados: dict[int, dict] = {}
notificacoes_globais: list[dict] = []


# --- Supabase helpers ---

def _supabase_salvar_pedido(pedido_id: int, pedido: "Pedido", data_criacao: str) -> None:
    """Persiste um novo pedido no Supabase (se configurado)."""
    supabase = get_supabase_client()
    if supabase is None:
        return
    try:
        produtos_json = [p.to_dict() for p in pedido.produtos]
        supabase.table("pedidos").upsert(
            {
                "id": pedido_id,
                "cliente": pedido.cliente,
                "status": pedido.status,
                "total": pedido.calcular_total(),
                "produtos": produtos_json,
                "data_criacao": data_criacao,
                "finalizado": False,
                "data_finalizacao": None,
            }
        ).execute()
    except Exception as exc:
        print(f"[SUPABASE] Erro ao salvar pedido #{pedido_id}: {exc}")


def _supabase_atualizar_status(
    pedido_id: int,
    novo_status: str,
    finalizado: bool,
    data_finalizacao: str | None,
) -> None:
    """Atualiza o status de um pedido no Supabase (se configurado)."""
    supabase = get_supabase_client()
    if supabase is None:
        return
    try:
        payload: dict = {"status": novo_status, "finalizado": finalizado}
        if data_finalizacao:
            payload["data_finalizacao"] = data_finalizacao
        supabase.table("pedidos").update(payload).eq("id", pedido_id).execute()
    except Exception as exc:
        print(f"[SUPABASE] Erro ao atualizar status do pedido #{pedido_id}: {exc}")

# Observadores disponiveis
OBSERVADORES = {
    "email": EmailObserver(),
    "log": LogObserver(),
    "tela": TelaObserver(),
    "cozinha": KitchenObserver(),
    "analytics": AnalyticsObserver(),
}

# Produtos disponiveis
PRODUTOS_CATALOGO: list[dict] = [
    # Computadores e Notebooks
    {"id": 1, "nome": "Notebook Dell Inspiron 15", "preco": 3599.90, "categoria": "notebooks"},
    {"id": 2, "nome": "Notebook Lenovo IdeaPad 3", "preco": 2899.90, "categoria": "notebooks"},
    {"id": 3, "nome": "MacBook Air M2", "preco": 8999.90, "categoria": "notebooks"},
    {"id": 4, "nome": "PC Gamer Completo i5", "preco": 4299.90, "categoria": "computadores"},
    # Perifericos
    {"id": 5, "nome": "Mouse Wireless Logitech MX", "preco": 129.90, "categoria": "perifericos"},
    {"id": 6, "nome": "Mouse Gamer Razer DeathAdder", "preco": 249.90, "categoria": "perifericos"},
    {"id": 7, "nome": "Teclado Mecanico Redragon", "preco": 289.90, "categoria": "perifericos"},
    {"id": 8, "nome": "Teclado Apple Magic Keyboard", "preco": 899.90, "categoria": "perifericos"},
    {"id": 9, "nome": "Headset Gamer HyperX Cloud", "preco": 349.90, "categoria": "perifericos"},
    {"id": 10, "nome": "Headset JBL Tune 510BT", "preco": 199.90, "categoria": "perifericos"},
    # Monitores
    {"id": 11, "nome": 'Monitor LED 24" Samsung', "preco": 899.90, "categoria": "monitores"},
    {"id": 12, "nome": 'Monitor Gamer 27" 144Hz LG', "preco": 1599.90, "categoria": "monitores"},
    {"id": 13, "nome": 'Monitor Ultrawide 34" Dell', "preco": 2499.90, "categoria": "monitores"},
    # Cameras e Video
    {"id": 14, "nome": "Webcam Logitech C920 HD", "preco": 429.90, "categoria": "cameras"},
    {"id": 15, "nome": "Webcam Razer Kiyo Pro", "preco": 799.90, "categoria": "cameras"},
    {"id": 16, "nome": "Ring Light 10 polegadas", "preco": 89.90, "categoria": "cameras"},
    # Armazenamento
    {"id": 17, "nome": "SSD 1TB Kingston NVMe", "preco": 399.90, "categoria": "armazenamento"},
    {"id": 18, "nome": "SSD 2TB Samsung 980 Pro", "preco": 899.90, "categoria": "armazenamento"},
    {"id": 19, "nome": "HD Externo 2TB Seagate", "preco": 449.90, "categoria": "armazenamento"},
    {"id": 20, "nome": "Pen Drive 128GB SanDisk", "preco": 79.90, "categoria": "armazenamento"},
    # Memoria e Componentes
    {"id": 21, "nome": "Memoria RAM 16GB DDR4", "preco": 289.90, "categoria": "componentes"},
    {"id": 22, "nome": "Memoria RAM 32GB DDR5", "preco": 599.90, "categoria": "componentes"},
    {"id": 23, "nome": "Placa de Video RTX 3060", "preco": 2199.90, "categoria": "componentes"},
    {"id": 24, "nome": "Fonte 650W Corsair 80Plus", "preco": 449.90, "categoria": "componentes"},
    # Acessorios
    {"id": 25, "nome": "Mousepad Gamer XL 90x40cm", "preco": 69.90, "categoria": "acessorios"},
    {"id": 26, "nome": "Suporte Notebook Ajustavel", "preco": 119.90, "categoria": "acessorios"},
    {"id": 27, "nome": "Hub USB-C 7 em 1", "preco": 189.90, "categoria": "acessorios"},
    {"id": 28, "nome": "Cadeira Gamer Thunderx3", "preco": 1299.90, "categoria": "acessorios"},
    # Smartphones e Tablets
    {"id": 29, "nome": "iPhone 15 128GB", "preco": 5999.90, "categoria": "smartphones"},
    {"id": 30, "nome": "Samsung Galaxy S24", "preco": 4499.90, "categoria": "smartphones"},
    {"id": 31, "nome": "iPad 10 64GB Wi-Fi", "preco": 3799.90, "categoria": "tablets"},
    {"id": 32, "nome": "Tablet Samsung Tab S9", "preco": 4299.90, "categoria": "tablets"},
]


# --- Schemas ---
class CriarPedidoRequest(BaseModel):
    cliente: str
    produtos: list[int]
    observadores: list[str] = ["email", "log", "tela"]


class AtualizarStatusRequest(BaseModel):
    status: str


# --- Rotas ---


@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "Sistema de Pedidos"}


@app.get("/api/produtos")
async def listar_produtos():
    return PRODUTOS_CATALOGO


@app.get("/api/pedidos")
async def listar_pedidos():
    pedidos_list = []
    for pedido_id, pedido_data in pedidos_ativos.items():
        pedido = pedido_data["pedido"]
        pedidos_list.append(
            {
                "id": pedido_id,
                "cliente": pedido.cliente,
                "status": pedido.status,
                "total": pedido.calcular_total(),
                "quantidade_produtos": len(pedido.produtos),
                "data_criacao": pedido_data["data_criacao"],
            }
        )
    return pedidos_list


@app.get("/api/pedidos/historico")
async def listar_historico():
    historico_list = []
    for pedido_id, pedido_data in pedidos_finalizados.items():
        pedido = pedido_data["pedido"]
        historico_list.append(
            {
                "id": pedido_id,
                "cliente": pedido.cliente,
                "status": pedido.status,
                "total": pedido.calcular_total(),
                "quantidade_produtos": len(pedido.produtos),
                "data_criacao": pedido_data["data_criacao"],
                "data_finalizacao": pedido_data.get("data_finalizacao", ""),
            }
        )
    historico_list.sort(key=lambda x: x["data_finalizacao"], reverse=True)
    return historico_list


@app.post("/api/pedidos")
async def criar_pedido(req: CriarPedidoRequest):
    if not req.cliente:
        raise fastapi.HTTPException(status_code=400, detail="Nome do cliente e obrigatorio")

    pedido = Pedido(req.cliente)

    # Adicionar produtos
    produtos_map = {p["id"]: p for p in PRODUTOS_CATALOGO}
    for pid in req.produtos:
        if pid in produtos_map:
            p = produtos_map[pid]
            pedido.adicionar_produto(Produto(p["nome"], p["preco"], id=p["id"]))

    # Registrar observadores selecionados
    for obs_key in req.observadores:
        if obs_key in OBSERVADORES:
            pedido.adicionar_observador(OBSERVADORES[obs_key])

    pedido_id = pedido.id
    data_criacao = time.strftime("%d/%m/%Y %H:%M:%S")
    pedidos_ativos[pedido_id] = {
        "pedido": pedido,
        "historico": [
            {
                "status": pedido.status,
                "data": data_criacao,
                "observacoes": "Pedido criado",
            }
        ],
        "data_criacao": data_criacao,
    }

    # Persistir no Supabase (se configurado)
    _supabase_salvar_pedido(pedido_id, pedido, data_criacao)

    # Notificacao global de criacao
    notificacoes_globais.append(
        {
            "tipo": "sistema",
            "icone": "plus-circle",
            "titulo": f"Novo Pedido #{pedido_id}",
            "mensagem": f"Pedido criado para {req.cliente} com {len(req.produtos)} produto(s) - Total: R${pedido.calcular_total():.2f}",
            "data": data_criacao,
        }
    )

    return {
        "message": "Pedido criado com sucesso",
        "pedido_id": pedido_id,
        "status": pedido.status,
        "total": pedido.calcular_total(),
    }


@app.put("/api/pedidos/{pedido_id}/status")
async def atualizar_status(pedido_id: int, req: AtualizarStatusRequest):
    if pedido_id not in pedidos_ativos:
        raise fastapi.HTTPException(status_code=404, detail="Pedido nao encontrado")

    pedido = pedidos_ativos[pedido_id]["pedido"]
    status_anterior = pedido.status

    # Atualizar status (dispara as notificacoes dos observadores)
    pedido.status = req.status

    data_alteracao = time.strftime("%d/%m/%Y %H:%M:%S")
    pedidos_ativos[pedido_id]["historico"].append(
        {
            "status": req.status,
            "data": data_alteracao,
            "observacoes": f"Status alterado de {status_anterior} para {req.status}",
        }
    )

    # Coleta notificacoes dos observadores e adiciona ao global
    novas_notificacoes = pedido.get_notificacoes()
    if novas_notificacoes:
        notificacoes_globais.extend(novas_notificacoes[-len(pedido._observadores) :])
        # Limita historico de notificacoes a ultimas 50
        while len(notificacoes_globais) > 50:
            notificacoes_globais.pop(0)

    movido = False
    if req.status in [Pedido.STATUS_ENTREGUE, Pedido.STATUS_CANCELADO]:
        pedidos_finalizados[pedido_id] = {
            "pedido": pedido,
            "historico": pedidos_ativos[pedido_id]["historico"],
            "data_criacao": pedidos_ativos[pedido_id]["data_criacao"],
            "data_finalizacao": data_alteracao,
        }
        del pedidos_ativos[pedido_id]
        movido = True

    # Persistir mudanca de status no Supabase (se configurado)
    _supabase_atualizar_status(
        pedido_id,
        novo_status=req.status,
        finalizado=movido,
        data_finalizacao=data_alteracao if movido else None,
    )

    return {
        "message": "Status atualizado com sucesso",
        "pedido_id": pedido_id,
        "status_anterior": status_anterior,
        "status_novo": req.status,
        "movido_para_historico": movido,
    }


@app.get("/api/pedidos/{pedido_id}")
async def detalhar_pedido(pedido_id: int):
    if pedido_id in pedidos_ativos:
        pedido_data = pedidos_ativos[pedido_id]
        tipo = "ativo"
    elif pedido_id in pedidos_finalizados:
        pedido_data = pedidos_finalizados[pedido_id]
        tipo = "finalizado"
    else:
        raise fastapi.HTTPException(status_code=404, detail="Pedido nao encontrado")

    pedido = pedido_data["pedido"]
    return {
        "id": pedido.id,
        "cliente": pedido.cliente,
        "status": pedido.status,
        "total": pedido.calcular_total(),
        "produtos": [p.to_dict() for p in pedido.produtos],
        "historico": pedido_data["historico"],
        "tipo": tipo,
        "data_criacao": pedido_data.get("data_criacao", ""),
        "data_finalizacao": pedido_data.get("data_finalizacao") if tipo == "finalizado" else None,
    }


@app.get("/api/estatisticas")
async def estatisticas():
    total_pedidos = len(pedidos_ativos) + len(pedidos_finalizados)
    pedidos_entregues = sum(
        1 for p in pedidos_finalizados.values() if p["pedido"].status == Pedido.STATUS_ENTREGUE
    )
    pedidos_cancelados = sum(
        1 for p in pedidos_finalizados.values() if p["pedido"].status == Pedido.STATUS_CANCELADO
    )
    valor_total_vendido = sum(
        p["pedido"].calcular_total()
        for p in pedidos_finalizados.values()
        if p["pedido"].status == Pedido.STATUS_ENTREGUE
    )
    valor_ativos = sum(p["pedido"].calcular_total() for p in pedidos_ativos.values())

    return {
        "pedidos_ativos": len(pedidos_ativos),
        "pedidos_finalizados": len(pedidos_finalizados),
        "pedidos_entregues": pedidos_entregues,
        "pedidos_cancelados": pedidos_cancelados,
        "total_pedidos": total_pedidos,
        "valor_total_vendido": valor_total_vendido,
        "valor_ativos": valor_ativos,
        "taxa_entrega": (pedidos_entregues / max(total_pedidos, 1)) * 100,
    }


@app.get("/api/notificacoes")
async def listar_notificacoes():
    return notificacoes_globais[-20:][::-1]


@app.get("/api/observadores")
async def listar_observadores():
    return [
        {"id": "email", "nome": "E-mail", "descricao": "Envia notificacoes por e-mail ao cliente", "icone": "mail"},
        {"id": "log", "nome": "Log", "descricao": "Registra alteracoes em arquivo de log", "icone": "file-text"},
        {"id": "tela", "nome": "Tela", "descricao": "Exibe notificacoes na interface do sistema", "icone": "monitor"},
        {"id": "cozinha", "nome": "Cozinha", "descricao": "Notifica cozinha quando pedido e pago", "icone": "chef-hat"},
        {"id": "analytics", "nome": "Analytics", "descricao": "Registra metricas de desempenho", "icone": "bar-chart-3"},
    ]
