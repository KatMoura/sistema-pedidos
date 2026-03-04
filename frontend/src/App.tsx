import { useState, useEffect, useCallback } from "react";
import { api } from "./api";
import type {
  TabId,
  PedidoResumo,
  PedidoHistorico,
  Estatisticas,
  Notificacao,
  Produto,
} from "./types";
import Header from "./components/Header";
import TabNav from "./components/TabNav";
import PedidosAtivos from "./components/PedidosAtivos";
import Historico from "./components/Historico";
import CriarPedido from "./components/CriarPedido";
import Notificacoes from "./components/Notificacoes";
import "./App.css";

export default function App() {
  const [activeTab, setActiveTab] = useState<TabId>("ativos");
  const [pedidos, setPedidos] = useState<PedidoResumo[]>([]);
  const [historico, setHistorico] = useState<PedidoHistorico[]>([]);
  const [stats, setStats] = useState<Estatisticas | null>(null);
  const [notificacoes, setNotificacoes] = useState<Notificacao[]>([]);
  const [produtos, setProdutos] = useState<Produto[]>([]);
  const [localNotifs, setLocalNotifs] = useState<Notificacao[]>([]);

  const loadPedidos = useCallback(async () => {
    try {
      const data = await api.getPedidos();
      setPedidos(data);
    } catch (e) {
      console.error("Erro carregando pedidos:", e);
    }
  }, []);

  const loadHistorico = useCallback(async () => {
    try {
      const data = await api.getHistorico();
      setHistorico(data);
    } catch (e) {
      console.error("Erro carregando historico:", e);
    }
  }, []);

  const loadStats = useCallback(async () => {
    try {
      const data = await api.getEstatisticas();
      setStats(data);
    } catch (e) {
      console.error("Erro carregando stats:", e);
    }
  }, []);

  const loadNotificacoes = useCallback(async () => {
    try {
      const data = await api.getNotificacoes();
      setNotificacoes(data);
    } catch (e) {
      console.error("Erro carregando notificacoes:", e);
    }
  }, []);

  const loadProdutos = useCallback(async () => {
    try {
      const data = await api.getProdutos();
      setProdutos(data);
    } catch (e) {
      console.error("Erro carregando produtos:", e);
    }
  }, []);

  const refreshAll = useCallback(() => {
    loadPedidos();
    loadHistorico();
    loadStats();
    loadNotificacoes();
  }, [loadPedidos, loadHistorico, loadStats, loadNotificacoes]);

  useEffect(() => {
    loadProdutos();
    refreshAll();
  }, [loadProdutos, refreshAll]);

  useEffect(() => {
    const interval = setInterval(refreshAll, 8000);
    return () => clearInterval(interval);
  }, [refreshAll]);

  const addLocalNotif = useCallback((notif: Notificacao) => {
    setLocalNotifs((prev) => [notif, ...prev].slice(0, 20));
  }, []);

  const allNotifs = [...localNotifs, ...notificacoes].slice(0, 25);

  return (
    <div className="app-container">
      <Header stats={stats} />
      <TabNav activeTab={activeTab} onTabChange={setActiveTab} stats={stats} />
      <div className="main-layout">
        <div className="main-content">
          {activeTab === "ativos" && (
            <PedidosAtivos
              pedidos={pedidos}
              onRefresh={refreshAll}
              addNotif={addLocalNotif}
            />
          )}
          {activeTab === "historico" && (
            <Historico historico={historico} stats={stats} />
          )}
          {activeTab === "criar" && (
            <CriarPedido
              produtos={produtos}
              onCreated={() => {
                refreshAll();
                setActiveTab("ativos");
              }}
              addNotif={addLocalNotif}
            />
          )}
        </div>
        <aside className="side-panel">
          <Notificacoes notificacoes={allNotifs} />
        </aside>
      </div>
      <footer className="app-footer">
        <p>
          Sistema de Gerenciamento de Pedidos &mdash; Padrao Observer em Python
        </p>
        <p>
          Status do servidor:{" "}
          <span className="status-dot active" />
          Online
        </p>
      </footer>
    </div>
  );
}
