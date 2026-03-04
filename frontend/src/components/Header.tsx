import {
  ShoppingCart,
  Package,
  History,
  CheckCircle,
  DollarSign,
} from "lucide-react";
import type { Estatisticas } from "../types";
import "./Header.css";

export default function Header({ stats }: { stats: Estatisticas | null }) {
  return (
    <header className="header">
      <div className="header-top">
        <div className="header-logo">
          <ShoppingCart size={28} />
          <h1>Sistema de Pedidos</h1>
        </div>
        <p className="header-subtitle">
          Padrao Observer &mdash; Notificacoes em Tempo Real (Python)
        </p>
      </div>
      {stats && (
        <div className="header-stats">
          <div className="header-stat">
            <Package size={16} />
            <span>Ativos: {stats.pedidos_ativos}</span>
          </div>
          <div className="header-stat">
            <History size={16} />
            <span>Historico: {stats.pedidos_finalizados}</span>
          </div>
          <div className="header-stat">
            <CheckCircle size={16} />
            <span>Entregues: {stats.pedidos_entregues}</span>
          </div>
          <div className="header-stat">
            <DollarSign size={16} />
            <span>
              Total: R${" "}
              {stats.valor_total_vendido.toLocaleString("pt-BR", {
                minimumFractionDigits: 2,
              })}
            </span>
          </div>
        </div>
      )}
    </header>
  );
}
