import type { TabId, Estatisticas } from "../types";
import "./TabNav.css";

interface TabNavProps {
  activeTab: TabId;
  onTabChange: (tab: TabId) => void;
  stats: Estatisticas | null;
}

const TABS: { id: TabId; label: string; icon: string }[] = [
  { id: "ativos", label: "Pedidos Ativos", icon: "📋" },
  { id: "historico", label: "Histórico", icon: "📜" },
  { id: "criar", label: "Novo Pedido", icon: "➕" },
];

export default function TabNav({ activeTab, onTabChange, stats }: TabNavProps) {
  return (
    <nav className="tab-nav">
      {TABS.map((tab) => (
        <button
          key={tab.id}
          className={`tab-btn${activeTab === tab.id ? " tab-btn--active" : ""}`}
          onClick={() => onTabChange(tab.id)}
        >
          <span className="tab-icon">{tab.icon}</span>
          <span className="tab-label">{tab.label}</span>
          {tab.id === "ativos" && stats && stats.pedidos_ativos > 0 && (
            <span className="tab-badge">{stats.pedidos_ativos}</span>
          )}
        </button>
      ))}
    </nav>
  );
}
