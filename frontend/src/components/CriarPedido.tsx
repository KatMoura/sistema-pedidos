import { useState } from "react";
import { api } from "../api";
import type { Produto, Notificacao } from "../types";
import "./CriarPedido.css";

const OBSERVADORES = [
  { id: "email", label: "📧 E-mail" },
  { id: "log", label: "📄 Log" },
  { id: "tela", label: "🖥️ Tela" },
  { id: "cozinha", label: "👨‍🍳 Cozinha" },
  { id: "analytics", label: "📊 Analytics" },
];

interface CriarPedidoProps {
  produtos: Produto[];
  onCreated: () => void;
  addNotif: (notif: Notificacao) => void;
}

export default function CriarPedido({ produtos, onCreated, addNotif }: CriarPedidoProps) {
  const [cliente, setCliente] = useState("");
  const [selectedProdutos, setSelectedProdutos] = useState<number[]>([]);
  const [selectedObs, setSelectedObs] = useState<string[]>(["email", "log", "tela"]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function toggleProduto(id: number) {
    setSelectedProdutos((prev) =>
      prev.includes(id) ? prev.filter((p) => p !== id) : [...prev, id]
    );
  }

  function toggleObs(id: string) {
    setSelectedObs((prev) =>
      prev.includes(id) ? prev.filter((o) => o !== id) : [...prev, id]
    );
  }

  const total = produtos
    .filter((p) => selectedProdutos.includes(p.id))
    .reduce((sum, p) => sum + p.preco, 0);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    if (!cliente.trim()) {
      setError("Informe o nome do cliente.");
      return;
    }
    if (selectedProdutos.length === 0) {
      setError("Selecione pelo menos um produto.");
      return;
    }
    setLoading(true);
    try {
      const res = await api.criarPedido({
        cliente: cliente.trim(),
        produtos: selectedProdutos,
        observadores: selectedObs,
      });
      addNotif({
        tipo: "sistema",
        icone: "🆕",
        titulo: `Pedido #${res.pedido_id} criado`,
        mensagem: `Cliente: ${cliente} | Total: R$${res.total.toFixed(2)}`,
        data: new Date().toLocaleString("pt-BR"),
      });
      setCliente("");
      setSelectedProdutos([]);
      onCreated();
    } catch (e: any) {
      setError(e.message ?? "Erro ao criar pedido.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form className="criar-pedido-form" onSubmit={handleSubmit}>
      <h2 className="form-title">Novo Pedido</h2>

      {error && <div className="form-error">{error}</div>}

      <div className="form-group">
        <label className="form-label" htmlFor="cliente">
          Nome do Cliente
        </label>
        <input
          id="cliente"
          type="text"
          className="form-input"
          placeholder="Ex: João Silva"
          value={cliente}
          onChange={(e) => setCliente(e.target.value)}
        />
      </div>

      <div className="form-group">
        <label className="form-label">Produtos</label>
        <div className="produtos-grid">
          {produtos.map((p) => (
            <label
              key={p.id}
              className={`produto-item${selectedProdutos.includes(p.id) ? " produto-item--selected" : ""}`}
            >
              <input
                type="checkbox"
                checked={selectedProdutos.includes(p.id)}
                onChange={() => toggleProduto(p.id)}
              />
              <span className="produto-nome">{p.nome}</span>
              <span className="produto-preco">R${p.preco.toFixed(2)}</span>
            </label>
          ))}
        </div>
      </div>

      <div className="form-group">
        <label className="form-label">Observadores</label>
        <div className="obs-list">
          {OBSERVADORES.map((o) => (
            <label key={o.id} className="obs-item">
              <input
                type="checkbox"
                checked={selectedObs.includes(o.id)}
                onChange={() => toggleObs(o.id)}
              />
              {o.label}
            </label>
          ))}
        </div>
      </div>

      {selectedProdutos.length > 0 && (
        <div className="form-total">
          Total: <strong>R${total.toFixed(2)}</strong> ({selectedProdutos.length} produto(s))
        </div>
      )}

      <button type="submit" className="btn-submit" disabled={loading}>
        {loading ? "Criando…" : "Criar Pedido"}
      </button>
    </form>
  );
}
