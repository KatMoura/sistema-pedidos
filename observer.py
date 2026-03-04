from abc import ABC, abstractmethod #para criar classes que ninguem instancia, só herda
from typing import List, Dict, Any #para deixar o código com dicas de tipo
from datetime import datetime #para registrar o horario exato dos eventos



class Subject(ABC):
    #quem precisa ser "observado", ou seja, quem notifica os observadores
    
    @abstractmethod
    def adicionar_observador(self, observador: 'Observer') -> None:
        #Adiciona um observador à lista.
        pass
    
    @abstractmethod
    def remover_observador(self, observador: 'Observer') -> None:
        #Remove um observador da lista.
        pass
    
    @abstractmethod
    def notificar_observadores(self, *args, **kwargs) -> None:
        #Notifica todos os observadores registrados.

        pass




class Observer(ABC):
    #Interface abstrata para todos os observadores.
    
    @abstractmethod
    def update(self, pedido: 'Pedido', status_anterior: str, status_novo: str) -> None:
        #metodo chamado quando o subject notifica os observadores
        pass



class Produto:
    #Classe que representa um produto no sistema.
    
    def __init__(self, nome: str, preco: float):
        #inicializa um novo produto
        self.nome = nome
        self.preco = preco
    
    def __str__(self) -> str:
        return f"{self.nome} - R${self.preco:.2f}"



class Pedido(Subject):  #herda de Subject
    #classe que representa um pedido no sistema.
    
    # Status possíveis para um pedido
    STATUS_PENDENTE = "Pendente"
    STATUS_PAGO = "Pago"
    STATUS_ENVIADO = "Enviado"
    STATUS_ENTREGUE = "Entregue"
    STATUS_CANCELADO = "Cancelado"
    
    # Contador para gerar IDs únicos
    _contador_id = 1
    
    def __init__(self, cliente: str):
        #inicializa um novo pedido
        self.id = Pedido._contador_id
        Pedido._contador_id += 1
        
        self.cliente = cliente
        self.produtos: List[Produto] = []
        self._status = self.STATUS_PENDENTE
        self._observadores: List['Observer'] = []
    
    @property
    def status(self) -> str:
        #Getter para o status do pedido.
        return self._status
    
    @status.setter
    def status(self, novo_status: str) -> None:
        #Setter para o status do pedido. Notifica observadores se houver mudança.
        if novo_status != self._status:
            status_anterior = self._status
            self._status = novo_status
            self.notificar_observadores(status_anterior, novo_status)
    
    def adicionar_produto(self, produto: Produto) -> None:
        #Adiciona um produto ao pedido.
        self.produtos.append(produto)
    
    def calcular_total(self) -> float:
       #Calcula o valor total do pedido.
        return sum(produto.preco for produto in self.produtos)
    
    
    
    def adicionar_observador(self, observador: 'Observer') -> None:
       # Adiciona um observador à lista de observadores.
        if observador not in self._observadores:
            self._observadores.append(observador)
    
    def remover_observador(self, observador: 'Observer') -> None:
        # Remove um observador da lista de observadores.
        if observador in self._observadores:
            self._observadores.remove(observador)
    
    def notificar_observadores(self, status_anterior: str, status_novo: str) -> None:
       # Notifica todos os observadores registrados sobre a mudança de status.
        for observador in self._observadores:
            observador.update(self, status_anterior, status_novo)
    
    def __str__(self) -> str:
        produtos_str = "\n  ".join(str(p) for p in self.produtos)
        return (f"Pedido #{self.id} - Cliente: {self.cliente}\n"
                f"Status: {self.status}\n"
                f"Produtos:\n  {produtos_str}\n"
                f"Total: R${self.calcular_total():.2f}")



class EmailObserver(Observer):
    
    # Observador que envia notificações por e-mail sobre mudanças de status.
    
    def update(self, pedido: Pedido, status_anterior: str, status_novo: str) -> None:
        # Simula o envio de um e-mail ao cliente sobre a mudança de status do pedido.
        print(f"[E-MAIL] Notificação enviada para cliente {pedido.cliente}")
        print(f"  Pedido #{pedido.id} alterou status:")
        print(f"  De: {status_anterior} → Para: {status_novo}")
        print(f"  Total do pedido: R${pedido.calcular_total():.2f}")
        print(f"  Data da alteração: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print("-" * 50)


class LogObserver(Observer):
# Observador que registra mudanças de status em um arquivo de log.    
    def __init__(self, arquivo_log: str = "pedidos.log"):
        self.arquivo_log = arquivo_log
    
    def update(self, pedido: Pedido, status_anterior: str, status_novo: str) -> None:
      # Registra a mudança de status em um arquivo de log.
        mensagem = (
            f"[LOG] [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
            f"Pedido #{pedido.id} | "
            f"Status: {status_anterior} → {status_novo} | "
            f"Cliente: {pedido.cliente} | "
            f"Total: R${pedido.calcular_total():.2f}"
        )
        

        print(mensagem)
 

class TelaObserver(Observer):
    # Observador que exibe notificações na interface gráfica do sistema.
    
    def update(self, pedido: Pedido, status_anterior: str, status_novo: str) -> None:
        # Simula a exibição de uma notificação na tela do sistema sobre a mudança de status do pedido.
        print("[INTERFACE] Notificação exibida na tela:")
        print(f"  ⚡ Status do Pedido #{pedido.id} Atualizado!")
        print(f"  📋 Status: {status_anterior} → {status_novo}")
        print(f"  👤 Cliente: {pedido.cliente}")
        print(f"  📦 Itens: {len(pedido.produtos)} produto(s)")
        print(f"  💰 Valor Total: R${pedido.calcular_total():.2f}")
        print("-" * 50)


class KitchenObserver(Observer):
# Observador específico, que é notificada quando um pedido está pronto.    
    def update(self, pedido: Pedido, status_anterior: str, status_novo: str) -> None:
        # Simula a notificação quando um pedido é pago ou enviado para preparo.
        if status_novo in ["Pago", "Em Preparo"]:
            print(f"[COZINHA] 🍳 Pedido #{pedido.id} enviado para preparação")
            print(f"  Cliente: {pedido.cliente}")
            print(f"  Itens: {len(pedido.produtos)} produto(s)")
            print(f"  Status: {status_novo}")
            print(f"  Hora: {datetime.now().strftime('%H:%M:%S')}")
            print("-" * 50)


class AnalyticsObserver(Observer):
   # Observador que registra métricas para análise de desempenho do sistema.
    
    def update(self, pedido: Pedido, status_anterior: str, status_novo: str) -> None:
        # Registra métricas para análise de desempenho.
        print(f"[ANALYTICS] 📊 Métrica registrada: Pedido #{pedido.id}")
        print(f"  Status: {status_anterior} → {status_novo}")
        print(f"  Cliente: {pedido.cliente}")
        print(f"  Valor: R${pedido.calcular_total():.2f}")
        print(f"  Timestamp: {datetime.now().isoformat()}")
        print("-" * 50)



if __name__ == "__main__":
    
    print("SISTEMA DE GERENCIAMENTO DE PEDIDOS COM PADRÃO OBSERVER")
   
    
    # Teste rápido para verificar que tudo funciona
    produto1 = Produto("Notebook Dell Inspiron", 3599.90)
    pedido = Pedido("Maria Santos")
    pedido.adicionar_produto(produto1)
    
    # Adicionar observadores
    pedido.adicionar_observador(EmailObserver())
    pedido.adicionar_observador(LogObserver())
    
    print(f"\nPedido criado: #{pedido.id}")
    print(f"Status inicial: {pedido.status}")
    
    print("\n>>> Alterando status para 'Pago' (deve notificar):")
    pedido.status = Pedido.STATUS_PAGO
    
    print("\n>>> Verificando herança do Subject:")
    print(f"    Pedido é uma instância de Subject? {isinstance(pedido, Subject)}")
    print(f"    Pedido é uma instância de Observer? {isinstance(pedido, Observer)}")
    
    print("TESTE CONCLUÍDO - PADRÃO OBSERVER 100% IMPLEMENTADO")
