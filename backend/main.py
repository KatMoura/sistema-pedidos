"""
Sistema de Pedidos - Backend FastAPI
Implementa o padrao Observer para notificacoes em tempo real.
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
    {"id": 1, "nome": "Notebook Dell Inspiron", "preco": 3599.90},
    {"id": 2, "nome": "Mouse Wireless Logitech", "preco": 129.90},
    {"id": 3, "nome": "Teclado Mecanico Redragon", "preco": 289.90},
    {"id": 4, "nome": 'Monitor LED 24" Samsung', "preco": 899.90},
    {"id": 5, "nome": "Headset Gamer HyperX", "preco": 349.90},
    {"id": 6, "nome": "Webcam Logitech C920", "preco": 429.90},
    {"id": 7, "nome": "SSD 1TB Kingston", "preco": 399.90},
    {"id": 8, "nome": "Memoria RAM 16GB", "preco": 289.90},
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
