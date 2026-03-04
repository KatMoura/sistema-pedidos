import { ClipboardList, History, PlusCircle } from "lucide-react";
import type { TabId, Estatisticas } from "../types";
import "./TabNav.css";

interface Props {
  activeTab: TabId;
  onTabChange: (tab: TabId) => void;
  stats: Estatisticas | null;
}

const tabs: { id: TabId; label: string; icon: typeof ClipboardList }[] = [
  { id: "ativos", label: "Pedidos Ativos", icon: ClipboardList },
  { id: "historico", label: "Historico", icon: History },
  { id: "criar", label: "Criar Pedido", icon: PlusCircle },
];

export default function TabNav({ activeTab, onTabChange, stats }: Props) {
  return (
    <nav className="tab-nav">
      {tabs.map((tab) => {
        const Icon = tab.icon;
        const badge =
          tab.id === "ativos"
            ? stats?.pedidos_ativos ?? 0
            : tab.id === "historico"
              ? stats?.pedidos_finalizados ?? 0
              : null;
        return (
          <button
            key={tab.id}
            className={`tab-btn${activeTab === tab.id ? " active" : ""}`}
            onClick={() => onTabChange(tab.id)}
          >
            <Icon size={18} />
            <span className="tab-label">{tab.label}</span>
            {badge !== null && <span className="tab-badge">{badge}</span>}
          </button>
        );
      })}
    </nav>
  );
}
