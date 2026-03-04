# Microservices refactor

Este workspace contém dois microserviços separados conforme atividade final:

- **user_service**: gerencia CRUD de usuários
- **order_service**: gerencia produtos, pedidos e aplica padrão Observer/Fábrica

Cada serviço possui seu próprio banco `*.db` em SQLite e `requirements.txt`.

## Como executar localmente

1. Ative o virtualenv e instale dependências em cada pasta: 
   ```bash
   cd user_service && pip install -r requirements.txt
   cd ../order_service && pip install -r requirements.txt
   ```
2. Inicie os serviços separadamente (ou use `docker-compose up`).
   - `python user_service/app.py` -> porta 5001
   - `python order_service/app.py` -> porta 5000

   A interface web (`templates/index.html` + `static/script.js`) foi atualizada para
   chamar diretamente `http://localhost:5000` e `:5001`. Abra-a via qualquer servidor
   estático (por exemplo `python -m http.server` na raiz) ou mantenha o aplicativo
   raiz (`app.py` original) executando como gateway; ambos funcionarão devido ao CORS
   já habilitado.

4. Opcional: preencha o banco com alguns registros usando os scripts de seed:
   ```bash
   python user_service/seed.py
   python order_service/seed.py
   ```
   Eles fazem chamadas POST para criar usuários e produtos padrão.

5. Teste endpoints via `curl` ou navegador:
   - `GET http://localhost:5001/api/usuarios`
   - `POST http://localhost:5000/api/produtos` etc.

## Docker Compose

Há um `docker-compose.yml` no root que orquestra os dois serviços para deploy em VM.

```sh
docker-compose build
docker-compose up
```

Os bancos serão persistidos em volumes locais.

## Estrutura de pastas proposta para entrega

```
root/
  user_service/
  order_service/
  docker-compose.yml
  README.md
  (opcional) app.py    # cópia do código original não modificado
```

Este layout facilita entregar dois repositórios ou pastas separadas e atende aos
requisitos de containerização.
