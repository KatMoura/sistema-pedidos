import type { PedidoHistorico, Estatisticas } from "../types";
import "./Historico.css";

interface HistoricoProps {
  historico: PedidoHistorico[];
  stats: Estatisticas | null;
}

export default function Historico({ historico, stats }: HistoricoProps) {
  return (
    <div className="historico-container">
      {stats && (
        <div className="historico-stats">
          <div className="hstat-card">
            <span className="hstat-value">{stats.total_pedidos}</span>
            <span className="hstat-label">Total de Pedidos</span>
          </div>
          <div className="hstat-card">
            <span className="hstat-value">{stats.pedidos_entregues}</span>
            <span className="hstat-label">Entregues</span>
          </div>
          <div className="hstat-card">
            <span className="hstat-value">{stats.pedidos_cancelados}</span>
            <span className="hstat-label">Cancelados</span>
          </div>
          <div className="hstat-card">
            <span className="hstat-value">{stats.taxa_entrega.toFixed(1)}%</span>
            <span className="hstat-label">Taxa de Entrega</span>
          </div>
          <div className="hstat-card hstat-card--wide">
            <span className="hstat-value">R${stats.valor_total_vendido.toFixed(2)}</span>
            <span className="hstat-label">Valor Total Vendido</span>
          </div>
        </div>
      )}

      {historico.length === 0 ? (
        <div className="empty-state">
          <span className="empty-icon">📜</span>
          <p>Nenhum pedido finalizado ainda.</p>
        </div>
      ) : (
        <table className="historico-table">
          <thead>
            <tr>
              <th>#</th>
              <th>Cliente</th>
              <th>Status</th>
              <th>Total</th>
              <th>Criado em</th>
              <th>Finalizado em</th>
            </tr>
          </thead>
          <tbody>
            {historico.map((p) => (
              <tr key={p.id}>
                <td>{p.id}</td>
                <td>{p.cliente}</td>
                <td>
                  <span
                    className={`status-badge ${
                      p.status === "Entregue" ? "status--entregue" : "status--cancelado"
                    }`}
                  >
                    {p.status}
                  </span>
                </td>
                <td>R${p.total.toFixed(2)}</td>
                <td>{p.data_criacao}</td>
                <td>{p.data_finalizacao}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
