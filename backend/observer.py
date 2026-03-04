"""
Padrao Observer - Implementacao completa

Subject (ABC) -> Pedido
Observer (ABC) -> EmailObserver, LogObserver, TelaObserver, KitchenObserver, AnalyticsObserver

Quando o status de um Pedido muda, todos os observadores registrados sao notificados
automaticamente pelo metodo notificar_observadores().
"""

from abc import ABC, abstractmethod
from typing import List
from datetime import datetime


class Subject(ABC):
    """Interface abstrata para o Subject (quem e observado)."""

    @abstractmethod
    def adicionar_observador(self, observador: "Observer") -> None:
        pass

    @abstractmethod
    def remover_observador(self, observador: "Observer") -> None:
        pass

    @abstractmethod
    def notificar_observadores(self, *args, **kwargs) -> None:
        pass


class Observer(ABC):
    """Interface abstrata para todos os observadores."""

    @abstractmethod
    def update(self, pedido: "Pedido", status_anterior: str, status_novo: str) -> dict:
        pass


class Produto:
    """Classe que representa um produto no sistema."""

    def __init__(self, nome: str, preco: float, id: int | None = None):
        self.id = id
        self.nome = nome
        self.preco = preco

    def to_dict(self) -> dict:
        return {"id": self.id, "nome": self.nome, "preco": self.preco}

    def __str__(self) -> str:
        return f"{self.nome} - R${self.preco:.2f}"


class Pedido(Subject):
    """Classe que representa um pedido no sistema. Implementa Subject do padrao Observer."""

    STATUS_PENDENTE = "Pendente"
    STATUS_PAGO = "Pago"
    STATUS_ENVIADO = "Enviado"
    STATUS_ENTREGUE = "Entregue"
    STATUS_CANCELADO = "Cancelado"

    _contador_id = 1

    def __init__(self, cliente: str, id: int | None = None):
        if id is not None:
            self.id = id
        else:
            self.id = Pedido._contador_id
            Pedido._contador_id += 1
        self.cliente = cliente
        self.produtos: List[Produto] = []
        self._status = self.STATUS_PENDENTE
        self._observadores: List[Observer] = []
        self._notificacoes: list[dict] = []

    @property
    def status(self) -> str:
        return self._status

    @status.setter
    def status(self, novo_status: str) -> None:
        if novo_status != self._status:
            status_anterior = self._status
            self._status = novo_status
            self.notificar_observadores(status_anterior, novo_status)

    def adicionar_produto(self, produto: Produto) -> None:
        self.produtos.append(produto)

    def calcular_total(self) -> float:
        return sum(produto.preco for produto in self.produtos)

    def adicionar_observador(self, observador: Observer) -> None:
        if observador not in self._observadores:
            self._observadores.append(observador)

    def remover_observador(self, observador: Observer) -> None:
        if observador in self._observadores:
            self._observadores.remove(observador)

    def notificar_observadores(self, status_anterior: str, status_novo: str) -> None:
        for observador in self._observadores:
            resultado = observador.update(self, status_anterior, status_novo)
            if resultado:
                self._notificacoes.append(resultado)

    def get_notificacoes(self) -> list[dict]:
        return list(self._notificacoes)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "cliente": self.cliente,
            "status": self.status,
            "total": self.calcular_total(),
            "quantidade_produtos": len(self.produtos),
            "produtos": [p.to_dict() for p in self.produtos],
        }


class EmailObserver(Observer):
    """Observador que simula envio de notificacoes por e-mail."""

    def update(self, pedido: Pedido, status_anterior: str, status_novo: str) -> dict:
        msg = (
            f"[E-MAIL] Notificacao enviada para cliente {pedido.cliente} - "
            f"Pedido #{pedido.id}: {status_anterior} -> {status_novo} - "
            f"Total: R${pedido.calcular_total():.2f}"
        )
        print(msg)
        return {
            "tipo": "email",
            "icone": "mail",
            "titulo": f"E-mail enviado para {pedido.cliente}",
            "mensagem": f"Pedido #{pedido.id}: {status_anterior} -> {status_novo}",
            "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        }


class LogObserver(Observer):
    """Observador que registra mudancas no log do sistema."""

    def update(self, pedido: Pedido, status_anterior: str, status_novo: str) -> dict:
        msg = (
            f"[LOG] [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
            f"Pedido #{pedido.id} | {status_anterior} -> {status_novo} | "
            f"Cliente: {pedido.cliente} | Total: R${pedido.calcular_total():.2f}"
        )
        print(msg)
        return {
            "tipo": "log",
            "icone": "file-text",
            "titulo": f"Log registrado - Pedido #{pedido.id}",
            "mensagem": f"{status_anterior} -> {status_novo} | Cliente: {pedido.cliente}",
            "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        }


class TelaObserver(Observer):
    """Observador que exibe notificacoes na interface."""

    def update(self, pedido: Pedido, status_anterior: str, status_novo: str) -> dict:
        msg = (
            f"[TELA] Pedido #{pedido.id} Atualizado! "
            f"{status_anterior} -> {status_novo} | "
            f"Cliente: {pedido.cliente} | {len(pedido.produtos)} produto(s)"
        )
        print(msg)
        return {
            "tipo": "tela",
            "icone": "monitor",
            "titulo": f"Pedido #{pedido.id} Atualizado!",
            "mensagem": f"{status_anterior} -> {status_novo} | {len(pedido.produtos)} produto(s) | R${pedido.calcular_total():.2f}",
            "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        }


class KitchenObserver(Observer):
    """Observador da cozinha - notificado quando pedido esta pago ou em preparo."""

    def update(self, pedido: Pedido, status_anterior: str, status_novo: str) -> dict | None:
        if status_novo in ["Pago", "Em Preparo"]:
            msg = (
                f"[COZINHA] Pedido #{pedido.id} enviado para preparacao - "
                f"Cliente: {pedido.cliente} | {len(pedido.produtos)} produto(s)"
            )
            print(msg)
            return {
                "tipo": "cozinha",
                "icone": "chef-hat",
                "titulo": f"Cozinha - Pedido #{pedido.id}",
                "mensagem": f"Enviado para preparacao | Cliente: {pedido.cliente}",
                "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            }
        return None


class AnalyticsObserver(Observer):
    """Observador de metricas para analise de desempenho."""

    def update(self, pedido: Pedido, status_anterior: str, status_novo: str) -> dict:
        msg = (
            f"[ANALYTICS] Pedido #{pedido.id} | "
            f"{status_anterior} -> {status_novo} | "
            f"Valor: R${pedido.calcular_total():.2f}"
        )
        print(msg)
        return {
            "tipo": "analytics",
            "icone": "bar-chart-3",
            "titulo": f"Metrica - Pedido #{pedido.id}",
            "mensagem": f"{status_anterior} -> {status_novo} | R${pedido.calcular_total():.2f}",
            "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        }
