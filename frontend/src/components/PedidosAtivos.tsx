import { useState } from "react";
import { api } from "../api";
import type { PedidoResumo, Notificacao } from "../types";
import "./PedidosAtivos.css";

const STATUS_OPTIONS = ["Pago", "Em Preparo", "Enviado", "Entregue", "Cancelado"];

const STATUS_COLORS: Record<string, string> = {
  Pendente: "status--pendente",
  Pago: "status--pago",
  "Em Preparo": "status--preparo",
  Enviado: "status--enviado",
  Entregue: "status--entregue",
  Cancelado: "status--cancelado",
};

interface PedidosAtivosProps {
  pedidos: PedidoResumo[];
  onRefresh: () => void;
  addNotif: (notif: Notificacao) => void;
}

export default function PedidosAtivos({ pedidos, onRefresh, addNotif }: PedidosAtivosProps) {
  const [updating, setUpdating] = useState<number | null>(null);

  async function handleStatusChange(pedidoId: number, novoStatus: string) {
    setUpdating(pedidoId);
    try {
      await api.atualizarStatus(pedidoId, novoStatus);
      addNotif({
        tipo: "sistema",
        icone: "✅",
        titulo: `Pedido #${pedidoId} atualizado`,
        mensagem: `Status alterado para ${novoStatus}`,
        data: new Date().toLocaleString("pt-BR"),
      });
      onRefresh();
    } catch (e: any) {
      addNotif({
        tipo: "erro",
        icone: "❌",
        titulo: "Erro ao atualizar",
        mensagem: e.message ?? "Erro desconhecido",
        data: new Date().toLocaleString("pt-BR"),
      });
    } finally {
      setUpdating(null);
    }
  }

  if (pedidos.length === 0) {
    return (
      <div className="empty-state">
        <span className="empty-icon">📭</span>
        <p>Nenhum pedido ativo no momento.</p>
        <p className="empty-hint">Clique em "Novo Pedido" para criar um.</p>
      </div>
    );
  }

  return (
    <div className="pedidos-grid">
      {pedidos.map((pedido) => (
        <div key={pedido.id} className="pedido-card">
          <div className="pedido-card__header">
            <span className="pedido-id">Pedido #{pedido.id}</span>
            <span className={`status-badge ${STATUS_COLORS[pedido.status] ?? ""}`}>
              {pedido.status}
            </span>
          </div>
          <div className="pedido-card__body">
            <p className="pedido-cliente">👤 {pedido.cliente}</p>
            <p className="pedido-info">
              🛒 {pedido.quantidade_produtos} produto(s) &mdash; R${pedido.total.toFixed(2)}
            </p>
            <p className="pedido-data">🕐 {pedido.data_criacao}</p>
          </div>
          <div className="pedido-card__footer">
            <select
              className="status-select"
              defaultValue=""
              disabled={updating === pedido.id}
              onChange={(e) => {
                if (e.target.value) handleStatusChange(pedido.id, e.target.value);
                e.target.value = "";
              }}
            >
              <option value="" disabled>
                Alterar status…
              </option>
              {STATUS_OPTIONS.map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </select>
            {updating === pedido.id && <span className="spinner">⏳</span>}
          </div>
        </div>
      ))}
    </div>
  );
}
