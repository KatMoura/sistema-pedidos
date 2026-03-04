from abc import ABC, abstractmethod
from typing import List
from datetime import datetime


class Subject(ABC):
    @abstractmethod
    def adicionar_observador(self, observador: 'Observer') -> None:
        pass

    @abstractmethod
    def remover_observador(self, observador: 'Observer') -> None:
        pass

    @abstractmethod
    def notificar_observadores(self, *args, **kwargs) -> None:
        pass


class Observer(ABC):
    @abstractmethod
    def update(self, pedido: 'Pedido', status_anterior: str, status_novo: str) -> None:
        pass


class Produto:
    def __init__(self, nome: str, preco: float, id: int = None):
        self.id = id
        self.nome = nome
        self.preco = preco

    def __str__(self) -> str:
        return f"{self.nome} - R${self.preco:.2f}"


class Pedido(Subject):
    STATUS_PENDENTE = "Pendente"
    STATUS_PAGO = "Pago"
    STATUS_ENVIADO = "Enviado"
    STATUS_ENTREGUE = "Entregue"
    STATUS_CANCELADO = "Cancelado"

    def __init__(self, cliente: str, id: int = None):
        self.id = id
        self.cliente = cliente
        self.produtos: List[Produto] = []
        self._status = self.STATUS_PENDENTE
        self._observadores: List['Observer'] = []

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

    def adicionar_observador(self, observador: 'Observer') -> None:
        if observador not in self._observadores:
            self._observadores.append(observador)

    def remover_observador(self, observador: 'Observer') -> None:
        if observador in self._observadores:
            self._observadores.remove(observador)

    def notificar_observadores(self, status_anterior: str, status_novo: str) -> None:
        for observador in self._observadores:
            observador.update(self, status_anterior, status_novo)

    def __str__(self) -> str:
        produtos_str = "\n  ".join(str(p) for p in self.produtos)
        return (
            f"Pedido #{self.id} - Cliente: {self.cliente}\n"
            f"Status: {self.status}\n"
            f"Produtos:\n  {produtos_str}\n"
            f"Total: R${self.calcular_total():.2f}")


# Observadores permanecem idênticos ao original, mantidos aqui para contexto
class EmailObserver(Observer):
    def update(self, pedido: Pedido, status_anterior: str, status_novo: str) -> None:
        print(f"[E-MAIL] Notificação enviada para cliente {pedido.cliente}")
        print(f"  Pedido #{pedido.id} alterou status:")
        print(f"  De: {status_anterior} → Para: {status_novo}")
        print(f"  Total do pedido: R${pedido.calcular_total():.2f}")
        print(f"  Data da alteração: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print("-" * 50)


class LogObserver(Observer):
    def __init__(self, arquivo_log: str = "pedidos.log"):
        self.arquivo_log = arquivo_log

    def update(self, pedido: Pedido, status_anterior: str, status_novo: str) -> None:
        mensagem = (
            f"[LOG] [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
            f"Pedido #{pedido.id} | "
            f"Status: {status_anterior} → {status_novo} | "
            f"Cliente: {pedido.cliente} | "
            f"Total: R${pedido.calcular_total():.2f}"
        )
        print(mensagem)


class TelaObserver(Observer):
    def update(self, pedido: Pedido, status_anterior: str, status_novo: str) -> None:
        print("[INTERFACE] Notificação exibida na tela:")
        print(f"  ⚡ Status do Pedido #{pedido.id} Atualizado!")
        print(f"  📋 Status: {status_anterior} → {status_novo}")
        print(f"  👤 Cliente: {pedido.cliente}")
        print(f"  📦 Itens: {len(pedido.produtos)} produto(s)")
        print(f"  💰 Valor Total: R${pedido.calcular_total():.2f}")
        print("-" * 50)
