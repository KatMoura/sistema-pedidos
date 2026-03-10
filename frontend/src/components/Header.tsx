import type { Estatisticas } from "../types";
import "./Header.css";

interface HeaderProps {
  stats: Estatisticas | null;
}

export default function Header({ stats }: HeaderProps) {
  return (
    <header className="header">
      <div className="header-brand">
        <span className="header-icon">📦</span>
        <div>
          <h1 className="header-title">Sistema de Pedidos</h1>
          <p className="header-subtitle">Padrão Observer em Python + FastAPI</p>
        </div>
      </div>
      <div className="header-stats">
        <div className="stat-card">
          <span className="stat-value">{stats?.pedidos_ativos ?? 0}</span>
          <span className="stat-label">Ativos</span>
        </div>
        <div className="stat-card">
          <span className="stat-value">{stats?.pedidos_entregues ?? 0}</span>
          <span className="stat-label">Entregues</span>
        </div>
        <div className="stat-card">
          <span className="stat-value">
            R${(stats?.valor_total_vendido ?? 0).toFixed(2)}
          </span>
          <span className="stat-label">Total Vendido</span>
        </div>
      </div>
    </header>
  );
}
