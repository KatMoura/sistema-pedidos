import { useState } from "react";
import {
  History,
  BarChart3,
  CheckCircle,
  XCircle,
  Package,
  DollarSign,
  CalendarPlus,
  CalendarCheck,
} from "lucide-react";
import type { PedidoHistorico, Estatisticas } from "../types";
import "./Historico.css";

interface Props {
  historico: PedidoHistorico[];
  stats: Estatisticas | null;
}

export default function Historico({ historico, stats }: Props) {
  const [filterStatus, setFilterStatus] = useState("");
  const [filterCliente, setFilterCliente] = useState("");

  const clientes = [...new Set(historico.map((p) => p.cliente))].sort();

  let filtrado = historico;
  if (filterStatus) filtrado = filtrado.filter((p) => p.status === filterStatus);
  if (filterCliente) filtrado = filtrado.filter((p) => p.cliente === filterCliente);

  const taxa = stats ? Math.round(stats.taxa_entrega) : 0;

  return (
    <div className="historico-grid">
      <div className="card">
        <h3 className="card-title">
          <History size={20} />
          Historico de Pedidos
        </h3>
        <div className="filters">
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="filter-select"
          >
            <option value="">Todos os Status</option>
            <option value="Entregue">Entregue</option>
            <option value="Cancelado">Cancelado</option>
          </select>
          <select
            value={filterCliente}
            onChange={(e) => setFilterCliente(e.target.value)}
            className="filter-select"
          >
            <option value="">Todos os Clientes</option>
            {clientes.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
          {(filterStatus || filterCliente) && (
            <button
              className="btn-clear-filter"
              onClick={() => {
                setFilterStatus("");
                setFilterCliente("");
              }}
            >
              Limpar Filtros
            </button>
          )}
        </div>

        {filtrado.length === 0 ? (
          <div className="empty-state">
            <History size={48} strokeWidth={1} />
            <p>Nenhum pedido no historico</p>
            <p className="text-muted">
              Os pedidos aparecerao aqui apos serem entregues ou cancelados
            </p>
          </div>
        ) : (
          <div className="historico-list">
            {filtrado.map((p) => (
              <div
                key={p.id}
                className={`historico-item ${p.status === "Entregue" ? "border-success" : "border-danger"}`}
              >
                <div className="historico-top">
                  <div>
                    <h4>
                      Pedido #{p.id} &mdash; {p.cliente}
                    </h4>
                    <span
                      className={`status-badge ${p.status === "Entregue" ? "status-entregue" : "status-cancelado"}`}
                    >
                      {p.status === "Entregue" ? (
                        <CheckCircle size={14} />
                      ) : (
                        <XCircle size={14} />
                      )}
                      {p.status}
                    </span>
                  </div>
                  <span className="historico-total">
                    R${" "}
                    {p.total.toLocaleString("pt-BR", {
                      minimumFractionDigits: 2,
                    })}
                  </span>
                </div>
                <div className="historico-dates">
                  <span>
                    <CalendarPlus size={14} /> Criado: {p.data_criacao}
                  </span>
                  <span>
                    <CalendarCheck size={14} /> Finalizado:{" "}
                    {p.data_finalizacao}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="card">
        <h3 className="card-title">
          <BarChart3 size={20} />
          Estatisticas
        </h3>
        {stats && (
          <>
            <div className="stats-grid">
              <div className="stat-card">
                <div className="stat-icon bg-accent">
                  <Package size={20} />
                </div>
                <div>
                  <div className="stat-value">{stats.total_pedidos}</div>
                  <div className="stat-label">Total de Pedidos</div>
                </div>
              </div>
              <div className="stat-card">
                <div className="stat-icon bg-success">
                  <CheckCircle size={20} />
                </div>
                <div>
                  <div className="stat-value">{stats.pedidos_entregues}</div>
                  <div className="stat-label">Entregues</div>
                </div>
              </div>
              <div className="stat-card">
                <div className="stat-icon bg-danger">
                  <XCircle size={20} />
                </div>
                <div>
                  <div className="stat-value">{stats.pedidos_cancelados}</div>
                  <div className="stat-label">Cancelados</div>
                </div>
              </div>
              <div className="stat-card">
                <div className="stat-icon bg-info">
                  <DollarSign size={20} />
                </div>
                <div>
                  <div className="stat-value">
                    R${" "}
                    {stats.valor_total_vendido.toLocaleString("pt-BR", {
                      minimumFractionDigits: 2,
                    })}
                  </div>
                  <div className="stat-label">Valor Total Vendido</div>
                </div>
              </div>
            </div>
            <div className="taxa-section">
              <h4>Taxa de Entrega</h4>
              <div className="progress-bar">
                <div
                  className="progress-fill"
                  style={{ width: `${taxa}%` }}
                />
              </div>
              <div className="progress-text">{taxa}%</div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
