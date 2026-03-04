-- Tabela de produtos
CREATE TABLE IF NOT EXISTS produtos (
  id SERIAL PRIMARY KEY,
  nome TEXT NOT NULL,
  preco NUMERIC(10,2) NOT NULL
);

-- Tabela de usuarios
CREATE TABLE IF NOT EXISTS usuarios (
  id SERIAL PRIMARY KEY,
  nome TEXT NOT NULL,
  email TEXT NOT NULL UNIQUE
);

-- Tabela de pedidos
CREATE TABLE IF NOT EXISTS pedidos (
  id SERIAL PRIMARY KEY,
  cliente TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'Pendente',
  data_criacao TEXT,
  data_finalizacao TEXT
);

-- Ligacao pedido-produtos
CREATE TABLE IF NOT EXISTS pedido_produtos (
  id SERIAL PRIMARY KEY,
  pedido_id INTEGER REFERENCES pedidos(id) ON DELETE CASCADE,
  produto_id INTEGER REFERENCES produtos(id) ON DELETE SET NULL
);

-- Historico de status
CREATE TABLE IF NOT EXISTS historico (
  id SERIAL PRIMARY KEY,
  pedido_id INTEGER REFERENCES pedidos(id) ON DELETE CASCADE,
  status TEXT NOT NULL,
  data TEXT,
  observacoes TEXT
);

-- Desabilitar RLS para todas as tabelas (sistema publico sem autenticacao)
ALTER TABLE produtos ENABLE ROW LEVEL SECURITY;
CREATE POLICY "allow_all_produtos" ON produtos FOR ALL USING (true) WITH CHECK (true);

ALTER TABLE usuarios ENABLE ROW LEVEL SECURITY;
CREATE POLICY "allow_all_usuarios" ON usuarios FOR ALL USING (true) WITH CHECK (true);

ALTER TABLE pedidos ENABLE ROW LEVEL SECURITY;
CREATE POLICY "allow_all_pedidos" ON pedidos FOR ALL USING (true) WITH CHECK (true);

ALTER TABLE pedido_produtos ENABLE ROW LEVEL SECURITY;
CREATE POLICY "allow_all_pedido_produtos" ON pedido_produtos FOR ALL USING (true) WITH CHECK (true);

ALTER TABLE historico ENABLE ROW LEVEL SECURITY;
CREATE POLICY "allow_all_historico" ON historico FOR ALL USING (true) WITH CHECK (true);
