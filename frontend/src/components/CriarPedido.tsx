import { useState, useEffect } from "react";
import {
  Package,
  PlusCircle,
  Plus,
  Minus,
  User,
  Bell,
  ShoppingCart,
  Mail,
  FileText,
  Monitor,
  BarChart3,
} from "lucide-react";
import { api } from "../api";
import type { Produto, Notificacao, ObservadorInfo } from "../types";
import "./CriarPedido.css";

interface Props {
  produtos: Produto[];
  onCreated: () => void;
  addNotif: (n: Notificacao) => void;
}

interface SelectedProduct extends Produto {
  quantidade: number;
}

const OBS_ICONS: Record<string, typeof Mail> = {
  mail: Mail,
  "file-text": FileText,
  monitor: Monitor,
  "chef-hat": Package,
  "bar-chart-3": BarChart3,
};

export default function CriarPedido({ produtos, onCreated, addNotif }: Props) {
  const [selected, setSelected] = useState<SelectedProduct[]>([]);
  const [cliente, setCliente] = useState("");
  const [observadores, setObservadores] = useState<string[]>([
    "email",
    "log",
    "tela",
  ]);
  const [obsInfo, setObsInfo] = useState<ObservadorInfo[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    api.getObservadores().then(setObsInfo).catch(() => {});
  }, []);

  function addProduct(prod: Produto) {
    setSelected((prev) => {
      const exists = prev.find((p) => p.id === prod.id);
      if (exists) {
        return prev.map((p) =>
          p.id === prod.id ? { ...p, quantidade: p.quantidade + 1 } : p
        );
      }
      return [...prev, { ...prod, quantidade: 1 }];
    });
  }

  function removeProduct(id: number) {
    setSelected((prev) => {
      const item = prev.find((p) => p.id === id);
      if (!item) return prev;
      if (item.quantidade > 1) {
        return prev.map((p) =>
          p.id === id ? { ...p, quantidade: p.quantidade - 1 } : p
        );
      }
      return prev.filter((p) => p.id !== id);
    });
  }

  const total = selected.reduce(
    (sum, p) => sum + p.preco * p.quantidade,
    0
  );

  function toggleObs(id: string) {
    setObservadores((prev) =>
      prev.includes(id) ? prev.filter((o) => o !== id) : [...prev, id]
    );
  }

  async function criarPedido() {
    if (!cliente.trim()) return;
    if (selected.length === 0) return;

    setLoading(true);
    try {
      const prodIds: number[] = [];
      selected.forEach((p) => {
        for (let i = 0; i < p.quantidade; i++) prodIds.push(p.id);
      });

      const res = await api.criarPedido({
        cliente: cliente.trim(),
        produtos: prodIds,
        observadores,
      });

      addNotif({
        tipo: "sistema",
        icone: "plus-circle",
        titulo: `Pedido #${res.pedido_id} criado`,
        mensagem: `Cliente: ${cliente.trim()} | Total: R$ ${res.total.toFixed(2)}`,
        data: new Date().toLocaleString("pt-BR"),
      });

      setCliente("");
      setSelected([]);
      onCreated();
    } catch {
      /* ignore */
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="criar-grid">
      <div className="card">
        <h3 className="card-title">
          <Package size={20} />
          Produtos Disponiveis
        </h3>
        <div className="product-grid">
          {produtos.map((p) => (
            <div key={p.id} className="product-card">
              <div>
                <h4>{p.nome}</h4>
                <span className="product-price">
                  R${" "}
                  {p.preco.toLocaleString("pt-BR", {
                    minimumFractionDigits: 2,
                  })}
                </span>
              </div>
              <button className="btn-add" onClick={() => addProduct(p)}>
                <Plus size={16} />
                Adicionar
              </button>
            </div>
          ))}
        </div>

        {selected.length > 0 && (
          <div className="selected-section">
            <h4 className="selected-title">Produtos Selecionados</h4>
            <div className="selected-list">
              {selected.map((p) => (
                <div key={p.id} className="selected-item">
                  <div>
                    <span className="selected-name">{p.nome}</span>
                    <span className="selected-qty">Qtd: {p.quantidade}</span>
                  </div>
                  <div className="selected-right">
                    <button
                      className="btn-icon-sm"
                      onClick={() => removeProduct(p.id)}
                    >
                      <Minus size={14} />
                    </button>
                    <span className="selected-subtotal">
                      R${" "}
                      {(p.preco * p.quantidade).toLocaleString("pt-BR", {
                        minimumFractionDigits: 2,
                      })}
                    </span>
                  </div>
                </div>
              ))}
            </div>
            <div className="selected-total">
              Total: R${" "}
              {total.toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
            </div>
          </div>
        )}
      </div>

      <div className="card">
        <h3 className="card-title">
          <PlusCircle size={20} />
          Criar Novo Pedido
        </h3>

        <div className="form-group">
          <label>
            <User size={16} />
            Nome do Cliente
          </label>
          <input
            type="text"
            placeholder="Digite o nome do cliente"
            value={cliente}
            onChange={(e) => setCliente(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && criarPedido()}
          />
        </div>

        <div className="form-group">
          <label>
            <Bell size={16} />
            Observadores (Padrao Observer)
          </label>
          <div className="obs-grid">
            {obsInfo.map((obs) => {
              const Icon = OBS_ICONS[obs.icone] ?? Bell;
              const checked = observadores.includes(obs.id);
              return (
                <label
                  key={obs.id}
                  className={`obs-option${checked ? " checked" : ""}`}
                >
                  <input
                    type="checkbox"
                    checked={checked}
                    onChange={() => toggleObs(obs.id)}
                  />
                  <Icon size={16} />
                  <div>
                    <span className="obs-name">{obs.nome}</span>
                    <span className="obs-desc">{obs.descricao}</span>
                  </div>
                </label>
              );
            })}
          </div>
        </div>

        <button
          className="btn-create"
          disabled={loading || !cliente.trim() || selected.length === 0}
          onClick={criarPedido}
        >
          <ShoppingCart size={18} />
          {loading ? "Criando..." : "Criar Pedido"}
        </button>

        {(!cliente.trim() || selected.length === 0) && (
          <p className="form-hint">
            {!cliente.trim() && "Insira o nome do cliente. "}
            {selected.length === 0 && "Selecione ao menos um produto."}
          </p>
        )}
      </div>
    </div>
  );
}
