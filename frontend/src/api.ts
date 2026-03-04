const BASE = "/api";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Erro desconhecido" }));
    throw new Error(err.detail || "Erro na requisicao");
  }
  return res.json();
}

export const api = {
  getProdutos: () => request<any[]>("/produtos"),
  getPedidos: () => request<any[]>("/pedidos"),
  getHistorico: () => request<any[]>("/pedidos/historico"),
  getPedido: (id: number) => request<any>(`/pedidos/${id}`),
  criarPedido: (data: { cliente: string; produtos: number[]; observadores: string[] }) =>
    request<any>("/pedidos", { method: "POST", body: JSON.stringify(data) }),
  atualizarStatus: (id: number, status: string) =>
    request<any>(`/pedidos/${id}/status`, {
      method: "PUT",
      body: JSON.stringify({ status }),
    }),
  getEstatisticas: () => request<any>("/estatisticas"),
  getNotificacoes: () => request<any[]>("/notificacoes"),
  getObservadores: () => request<any[]>("/observadores"),
};
