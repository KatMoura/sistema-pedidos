export interface Produto {
  id: number;
  nome: string;
  preco: number;
}

export interface PedidoResumo {
  id: number;
  cliente: string;
  status: string;
  total: number;
  quantidade_produtos: number;
  data_criacao: string;
}

export interface PedidoHistorico extends PedidoResumo {
  data_finalizacao: string;
}

export interface HistoricoItem {
  status: string;
  data: string;
  observacoes: string;
}

export interface PedidoDetalhe {
  id: number;
  cliente: string;
  status: string;
  total: number;
  produtos: Produto[];
  historico: HistoricoItem[];
  tipo: "ativo" | "finalizado";
  data_criacao: string;
  data_finalizacao: string | null;
}

export interface Notificacao {
  tipo: string;
  icone: string;
  titulo: string;
  mensagem: string;
  data: string;
}

export interface Estatisticas {
  pedidos_ativos: number;
  pedidos_finalizados: number;
  pedidos_entregues: number;
  pedidos_cancelados: number;
  total_pedidos: number;
  valor_total_vendido: number;
  valor_ativos: number;
  taxa_entrega: number;
}

export interface ObservadorInfo {
  id: string;
  nome: string;
  descricao: string;
  icone: string;
}

export type TabId = "ativos" | "historico" | "criar";
