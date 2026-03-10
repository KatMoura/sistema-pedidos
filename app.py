from pathlib import Path
from types import SimpleNamespace
import os
import time

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv
from supabase import create_client, Client

from observer import Pedido, Produto, EmailObserver, LogObserver, TelaObserver

# Carrega .env da raiz do projeto
ROOT_DIR = Path(__file__).resolve().parent
load_dotenv(ROOT_DIR / ".env", override=True)

def _env(name: str, required: bool = True) -> str:
    value = (os.getenv(name) or "").strip().strip('"').strip("'")
    if required and not value:
        raise RuntimeError(f"Variável obrigatória ausente: {name}")
    return value

SUPABASE_URL = _env("SUPABASE_URL")
SUPABASE_KEY = (
    _env("SUPABASE_SERVICE_KEY", required=False)
    or _env("SUPABASE_KEY", required=False)
    or _env("SUPABASE_ANON_KEY", required=False)
)

if not SUPABASE_KEY:
    raise RuntimeError("Defina SUPABASE_SERVICE_KEY ou SUPABASE_KEY no .env")

if not SUPABASE_URL.startswith("https://") or ".supabase.co" not in SUPABASE_URL:
    raise RuntimeError("SUPABASE_URL inválida")

# Correto: argumentos posicionais, sem keyword
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = Flask(__name__)
CORS(app)

observadores_ativos = {
    "email": EmailObserver(),
    "log": LogObserver(),
    "tela": TelaObserver(),
}

STATUS_FINALIZADOS = [Pedido.STATUS_ENTREGUE, Pedido.STATUS_CANCELADO]

def now_str() -> str:
    return time.strftime("%d/%m/%Y %H:%M:%S")

def _to_float(v):
    try:
        return float(v)
    except Exception:
        return 0.0

def _get_produtos_do_pedido(pedido_id: int):
    links = supabase.table("pedido_produtos").select("produto_id").eq("pedido_id", pedido_id).execute().data or []
    if not links:
        return []
    ids = [l["produto_id"] for l in links]
    return supabase.table("produtos").select("id,nome,preco").in_("id", ids).execute().data or []

def _total_pedido(produtos: list) -> float:
    return sum(_to_float(p.get("preco")) for p in produtos)

def _notificar_observadores(pedido_id: int, cliente: str, status: str, produtos_rows: list, observadores_ids=None):
    if observadores_ids is None:
        observadores_ids = ["email", "log", "tela"]

    pedido = Pedido(cliente)
    pedido.id = pedido_id
    for p in produtos_rows:
        pedido.adicionar_produto(Produto(p["nome"], _to_float(p["preco"])))

    for oid in observadores_ids:
        obs = observadores_ativos.get(oid)
        if obs:
            pedido.adicionar_observador(obs)

    pedido.status = status

@app.route("/")
def index():
    try:
        return render_template("index.html")
    except Exception:
        return jsonify({"ok": True, "message": "API de pedidos online"}), 200

@app.route("/api/health/supabase", methods=["GET"])
def health_supabase():
    try:
        supabase.table("pedidos").select("id").limit(1).execute()
        return jsonify({"ok": True, "supabase": "connected"})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@app.route("/api/produtos", methods=["GET"])
def get_produtos():
    try:
        produtos = supabase.table("produtos").select("id,nome,preco").order("id").execute().data or []
        return jsonify(produtos)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/pedidos", methods=["GET"])
def get_pedidos():
    try:
        rows = (
            supabase.table("pedidos")
            .select("id,cliente,status,data_criacao")
            .not_.in_("status", STATUS_FINALIZADOS)
            .order("id", desc=True)
            .execute()
            .data or []
        )
        result = []
        for row in rows:
            produtos = _get_produtos_do_pedido(row["id"])
            result.append({
                "id": row["id"],
                "cliente": row["cliente"],
                "status": row["status"],
                "total": _total_pedido(produtos),
                "quantidade_produtos": len(produtos),
                "data_criacao": row.get("data_criacao"),
            })
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/pedidos/historico", methods=["GET"])
def get_historico_pedidos():
    try:
        rows = (
            supabase.table("pedidos")
            .select("id,cliente,status,data_criacao,data_finalizacao")
            .in_("status", STATUS_FINALIZADOS)
            .order("id", desc=True)
            .execute()
            .data or []
        )
        historico = []
        for row in rows:
            produtos = _get_produtos_do_pedido(row["id"])
            historico.append({
                "id": row["id"],
                "cliente": row["cliente"],
                "status": row["status"],
                "total": _total_pedido(produtos),
                "quantidade_produtos": len(produtos),
                "data_criacao": row.get("data_criacao"),
                "data_finalizacao": row.get("data_finalizacao"),
                "dias_ativos": 1,
            })
        return jsonify(historico)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/pedidos", methods=["POST"])
def criar_pedido():
    try:
        data = request.json or {}
        cliente = (data.get("cliente") or "").strip()
        produtos_ids = data.get("produtos", [])
        observadores_ids = data.get("observadores", ["email", "log", "tela"])

        if not cliente:
            return jsonify({"error": "Nome do cliente é obrigatório"}), 400

        data_criacao = now_str()

        pedido_resp = supabase.table("pedidos").insert({
            "cliente": cliente,
            "status": Pedido.STATUS_PENDENTE,
            "data_criacao": data_criacao,
            "data_finalizacao": None,
        }).execute().data

        if not pedido_resp:
            return jsonify({"error": "Falha ao criar pedido"}), 500

        pedido_id = pedido_resp[0]["id"]

        if produtos_ids:
            payload_links = [{"pedido_id": pedido_id, "produto_id": int(pid)} for pid in produtos_ids]
            supabase.table("pedido_produtos").insert(payload_links).execute()

        supabase.table("historico").insert({
            "pedido_id": pedido_id,
            "status": Pedido.STATUS_PENDENTE,
            "data": data_criacao,
            "observacoes": "Pedido criado",
        }).execute()

        produtos_rows = _get_produtos_do_pedido(pedido_id)
        _notificar_observadores(pedido_id, cliente, Pedido.STATUS_PENDENTE, produtos_rows, observadores_ids)

        return jsonify({
            "message": "Pedido criado com sucesso",
            "pedido_id": pedido_id,
            "status": Pedido.STATUS_PENDENTE,
            "total": _total_pedido(produtos_rows),
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/pedidos/<int:pedido_id>/status", methods=["PUT"])
def atualizar_status(pedido_id):
    try:
        data = request.json or {}
        novo_status = data.get("status")

        if not novo_status:
            return jsonify({"error": "Status é obrigatório"}), 400

        pedido_rows = supabase.table("pedidos").select("id,cliente,status").eq("id", pedido_id).execute().data or []
        if not pedido_rows:
            return jsonify({"error": "Pedido não encontrado"}), 404

        pedido_row = pedido_rows[0]
        status_anterior = pedido_row["status"]
        data_alteracao = now_str()

        update_payload = {"status": novo_status}
        if novo_status in STATUS_FINALIZADOS:
            update_payload["data_finalizacao"] = data_alteracao

        supabase.table("pedidos").update(update_payload).eq("id", pedido_id).execute()

        supabase.table("historico").insert({
            "pedido_id": pedido_id,
            "status": novo_status,
            "data": data_alteracao,
            "observacoes": f"Status alterado de {status_anterior} para {novo_status}",
        }).execute()

        produtos_rows = _get_produtos_do_pedido(pedido_id)
        _notificar_observadores(pedido_id, pedido_row["cliente"], novo_status, produtos_rows)

        return jsonify({
            "message": "Status atualizado com sucesso",
            "pedido_id": pedido_id,
            "status_anterior": status_anterior,
            "status_novo": novo_status,
            "movido_para_historico": novo_status in STATUS_FINALIZADOS,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/pedidos/<int:pedido_id>", methods=["GET"])
def get_pedido_detalhes(pedido_id):
    try:
        pedido_rows = (
            supabase.table("pedidos")
            .select("id,cliente,status,data_criacao,data_finalizacao")
            .eq("id", pedido_id)
            .execute()
            .data or []
        )
        if not pedido_rows:
            return jsonify({"error": "Pedido não encontrado"}), 404

        pedido = pedido_rows[0]
        produtos = _get_produtos_do_pedido(pedido_id)

        hist = (
            supabase.table("historico")
            .select("status,data,observacoes")
            .eq("pedido_id", pedido_id)
            .order("id")
            .execute()
            .data or []
        )

        tipo = "finalizado" if pedido["status"] in STATUS_FINALIZADOS else "ativo"

        return jsonify({
            "id": pedido["id"],
            "cliente": pedido["cliente"],
            "status": pedido["status"],
            "total": _total_pedido(produtos),
            "produtos": [{"nome": p["nome"], "preco": _to_float(p["preco"])} for p in produtos],
            "historico": hist,
            "tipo": tipo,
            "data_criacao": pedido.get("data_criacao"),
            "data_finalizacao": pedido.get("data_finalizacao"),
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/estatisticas", methods=["GET"])
def get_estatisticas():
    try:
        all_pedidos = supabase.table("pedidos").select("id,status").execute().data or []
        total_pedidos = len(all_pedidos)
        pedidos_entregues_ids = [p["id"] for p in all_pedidos if p["status"] == Pedido.STATUS_ENTREGUE]
        pedidos_cancelados = sum(1 for p in all_pedidos if p["status"] == Pedido.STATUS_CANCELADO)
        pedidos_finalizados = sum(1 for p in all_pedidos if p["status"] in STATUS_FINALIZADOS)
        pedidos_ativos = total_pedidos - pedidos_finalizados

        valor_total_vendido = 0.0
        for pid in pedidos_entregues_ids:
            valor_total_vendido += _total_pedido(_get_produtos_do_pedido(pid))

        return jsonify({
            "pedidos_ativos": pedidos_ativos,
            "pedidos_finalizados": pedidos_finalizados,
            "pedidos_entregues": len(pedidos_entregues_ids),
            "pedidos_cancelados": pedidos_cancelados,
            "total_pedidos": total_pedidos,
            "valor_total_vendido": valor_total_vendido,
            "taxa_entrega": (len(pedidos_entregues_ids) / max(total_pedidos, 1)) * 100,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/notificacoes", methods=["GET"])
def get_notificacoes():
    return jsonify({"notificacoes": ["Sistema iniciado. Aguardando pedidos..."]})

@app.route("/api/observadores", methods=["GET"])
def get_observadores():
    return jsonify([
        {"id": "email", "nome": "Notificação por E-mail", "descricao": "Envia e-mails para o cliente"},
        {"id": "log", "nome": "Registro em Log", "descricao": "Registra todas as alterações em arquivo de log"},
        {"id": "tela", "nome": "Notificação na Tela", "descricao": "Exibe notificações na interface"},
    ])

if __name__ == "__main__":
    print("SISTEMA DE GERENCIAMENTO DE PEDIDOS")
    print("Servidor iniciado em: http://localhost:5000")
    app.run(debug=True, port=5000)