import { useState } from "react";
import {
  Eye,
  Edit3,
  ClipboardList,
  Search,
  Clock,
  CreditCard,
  Truck,
  CheckCircle,
  XCircle,
  X,
} from "lucide-react";
import { api } from "../api";
import type { PedidoResumo, PedidoDetalhe, Notificacao } from "../types";
import "./PedidosAtivos.css";

interface Props {
  pedidos: PedidoResumo[];
  onRefresh: () => void;
  addNotif: (n: Notificacao) => void;
}

const STATUS_CONFIG: Record<string, { cls: string; icon: typeof Clock }> = {
  Pendente: { cls: "status-pendente", icon: Clock },
  Pago: { cls: "status-pago", icon: CreditCard },
  Enviado: { cls: "status-enviado", icon: Truck },
  Entregue: { cls: "status-entregue", icon: CheckCircle },
  Cancelado: { cls: "status-cancelado", icon: XCircle },
};

const ALL_STATUS = ["Pendente", "Pago", "Enviado", "Entregue", "Cancelado"];

export default function PedidosAtivos({ pedidos, onRefresh, addNotif }: Props) {
  const [detalhe, setDetalhe] = useState<PedidoDetalhe | null>(null);
  const [modal, setModal] = useState<{ id: number; cliente: string } | null>(null);
  const [loading, setLoading] = useState(false);

  async function verDetalhes(id: number) {
    try {
      const data = await api.getPedido(id);
      setDetalhe(data);
    } catch {
      /* ignore */
    }
  }

  async function mudarStatus(id: number, novoStatus: string) {
    setLoading(true);
    try {
      const res = await api.atualizarStatus(id, novoStatus);
      addNotif({
        tipo: "sistema",
        icone: "check-circle",
        titulo: res.movido_para_historico
          ? `Pedido #${id} finalizado`
          : `Status atualizado`,
        mensagem: `${res.status_anterior} -> ${res.status_novo}`,
        data: new Date().toLocaleString("pt-BR"),
      });
      setModal(null);
      onRefresh();
      if (detalhe?.id === id) setDetalhe(null);
    } catch {
      /* ignore */
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="ativos-grid">
      <div className="card">
        <h3 className="card-title">
          <ClipboardList size={20} />
          Pedidos Ativos
        </h3>
        {pedidos.length === 0 ? (
          <div className="empty-state">
            <ClipboardList size={48} strokeWidth={1} />
            <p>Nenhum pedido ativo no momento</p>
            <p className="text-muted">Crie um novo pedido para comecar</p>
          </div>
        ) : (
          <div className="orders-list">
            {pedidos.map((p) => {
              const cfg = STATUS_CONFIG[p.status] ?? STATUS_CONFIG["Pendente"];
              const Icon = cfg.icon;
              return (
                <div key={p.id} className="order-item">
                  <div className="order-info">
                    <h4>
                      Pedido #{p.id} &mdash; {p.cliente}
                    </h4>
                    <div className="order-meta">
                      <span>
                        R${" "}
                        {p.total.toLocaleString("pt-BR", {
                          minimumFractionDigits: 2,
                        })}
                      </span>
                      <span>{p.quantidade_produtos} produto(s)</span>
                    </div>
                    <span className={`status-badge ${cfg.cls}`}>
                      <Icon size={14} />
                      {p.status}
                    </span>
                  </div>
                  <div className="order-actions">
                    <button
                      className="btn-icon"
                      onClick={() => verDetalhes(p.id)}
                      title="Ver detalhes"
                    >
                      <Eye size={16} />
                    </button>
                    <button
                      className="btn-icon"
                      onClick={() =>
                        setModal({ id: p.id, cliente: p.cliente })
                      }
                      title="Alterar status"
                    >
                      <Edit3 size={16} />
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      <div className="card">
        <h3 className="card-title">
          <Search size={20} />
          Detalhes do Pedido
        </h3>
        {detalhe ? (
          <div className="detail-content">
            <div className="detail-row">
              <strong>ID</strong>
              <span>
                #{detalhe.id} ({detalhe.tipo})
              </span>
            </div>
            <div className="detail-row">
              <strong>Cliente</strong>
              <span>{detalhe.cliente}</span>
            </div>
            <div className="detail-row">
              <strong>Status</strong>
              <span
                className={`status-badge ${STATUS_CONFIG[detalhe.status]?.cls ?? ""}`}
              >
                {detalhe.status}
              </span>
            </div>
            <div className="detail-row">
              <strong>Total</strong>
              <span>
                R${" "}
                {detalhe.total.toLocaleString("pt-BR", {
                  minimumFractionDigits: 2,
                })}
              </span>
            </div>
            <div className="detail-section">
              <strong>Produtos</strong>
              <ul className="detail-products">
                {detalhe.produtos.map((prod, i) => (
                  <li key={i}>
                    <span>{prod.nome}</span>
                    <span>
                      R${" "}
                      {prod.preco.toLocaleString("pt-BR", {
                        minimumFractionDigits: 2,
                      })}
                    </span>
                  </li>
                ))}
              </ul>
            </div>
            <div className="detail-section">
              <strong>Historico</strong>
              <div className="detail-history">
                {detalhe.historico.map((h, i) => (
                  <div key={i} className="history-entry">
                    <span className="history-status">{h.status}</span>
                    <span className="history-date">{h.data}</span>
                    <span className="history-note">{h.observacoes}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ) : (
          <div className="empty-state">
            <Search size={48} strokeWidth={1} />
            <p>Selecione um pedido para ver os detalhes</p>
          </div>
        )}
      </div>

      {/* Modal de Status */}
      {modal && (
        <div className="modal-overlay" onClick={() => setModal(null)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Alterar Status do Pedido</h3>
              <button className="btn-icon" onClick={() => setModal(null)}>
                <X size={20} />
              </button>
            </div>
            <div className="modal-body">
              <p className="modal-info">
                Pedido #{modal.id} &mdash; {modal.cliente}
              </p>
              <div className="status-grid">
                {ALL_STATUS.map((s) => {
                  const cfg = STATUS_CONFIG[s];
                  const Icon = cfg.icon;
                  const isFinal = s === "Entregue" || s === "Cancelado";
                  return (
                    <button
                      key={s}
                      className={`status-option ${cfg.cls}`}
                      disabled={loading}
                      onClick={() => mudarStatus(modal.id, s)}
                    >
                      <Icon size={20} />
                      <span>{s}</span>
                      {isFinal && (
                        <small className="final-tag">Finaliza</small>
                      )}
                    </button>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
