import type { Notificacao } from "../types";
import "./Notificacoes.css";

interface NotificacoesProps {
  notificacoes: Notificacao[];
}

const TIPO_ICON: Record<string, string> = {
  email: "📧",
  log: "📄",
  tela: "🖥️",
  cozinha: "👨‍🍳",
  analytics: "📊",
  sistema: "🔔",
  erro: "❌",
};

export default function Notificacoes({ notificacoes }: NotificacoesProps) {
  return (
    <div className="notificacoes-panel">
      <h3 className="notif-heading">🔔 Notificações</h3>
      {notificacoes.length === 0 ? (
        <p className="notif-empty">Nenhuma notificação ainda.</p>
      ) : (
        <ul className="notif-list">
          {notificacoes.map((n, i) => (
            <li key={i} className={`notif-item notif-item--${n.tipo}`}>
              <span className="notif-icon">{TIPO_ICON[n.tipo] ?? n.icone ?? "🔔"}</span>
              <div className="notif-content">
                <p className="notif-titulo">{n.titulo}</p>
                <p className="notif-mensagem">{n.mensagem}</p>
                <p className="notif-data">{n.data}</p>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
