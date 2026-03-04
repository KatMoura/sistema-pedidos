import {
  Bell,
  Mail,
  FileText,
  Monitor,
  BarChart3,
  Package,
  PlusCircle,
  CheckCircle,
  Info,
} from "lucide-react";
import type { Notificacao } from "../types";
import "./Notificacoes.css";

const ICON_MAP: Record<string, typeof Bell> = {
  mail: Mail,
  "file-text": FileText,
  monitor: Monitor,
  "bar-chart-3": BarChart3,
  "chef-hat": Package,
  "plus-circle": PlusCircle,
  "check-circle": CheckCircle,
  info: Info,
};

const TYPE_COLORS: Record<string, string> = {
  email: "var(--info)",
  log: "var(--warning)",
  tela: "var(--accent)",
  cozinha: "#f97316",
  analytics: "#a855f7",
  sistema: "var(--success)",
};

export default function Notificacoes({
  notificacoes,
}: {
  notificacoes: Notificacao[];
}) {
  return (
    <div className="card notif-card">
      <h3 className="card-title">
        <Bell size={20} />
        Notificacoes (Observer)
        {notificacoes.length > 0 && (
          <span className="notif-count">{notificacoes.length}</span>
        )}
      </h3>
      <div className="notif-list">
        {notificacoes.length === 0 ? (
          <div className="empty-state small">
            <Bell size={32} strokeWidth={1} />
            <p>Nenhuma notificacao ainda</p>
            <p className="text-muted">
              As notificacoes dos observadores aparecerao aqui
            </p>
          </div>
        ) : (
          notificacoes.map((n, i) => {
            const Icon = ICON_MAP[n.icone] ?? Info;
            const color = TYPE_COLORS[n.tipo] ?? "var(--text-secondary)";
            return (
              <div key={i} className="notif-item">
                <div
                  className="notif-icon"
                  style={{ borderColor: color }}
                >
                  <Icon size={16} style={{ color }} />
                </div>
                <div className="notif-content">
                  <div className="notif-header">
                    <span className="notif-title">{n.titulo}</span>
                    <span
                      className="notif-type"
                      style={{ color }}
                    >
                      {n.tipo}
                    </span>
                  </div>
                  <p className="notif-msg">{n.mensagem}</p>
                  <span className="notif-time">{n.data}</span>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
