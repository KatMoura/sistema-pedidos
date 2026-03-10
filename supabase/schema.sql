-- Supabase migration: create pedidos table
-- Run this in your Supabase SQL editor to set up the required table.

create table if not exists pedidos (
    id            bigint primary key,
    cliente       text        not null,
    status        text        not null default 'Pendente',
    total         numeric(10, 2) not null default 0,
    produtos      jsonb       not null default '[]',
    data_criacao  text        not null,
    finalizado    boolean     not null default false,
    data_finalizacao text
);

-- Enable Row Level Security (RLS) – adjust policies to your needs.
alter table pedidos enable row level security;

-- Allow all operations for service role (used server-side).
create policy "Service role full access"
    on pedidos
    for all
    using (true)
    with check (true);
