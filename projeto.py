import threading
import time
import random
import tkinter as tk
from tkinter import ttk


class DummyContextManager:
    def __enter__(self): pass
    def __exit__(self, exc_type, exc_val, exc_tb): pass


class SimulacaoJanelaDeslizante:
    def __init__(self, tamanho_janela, total_pacotes, escalonamento="FCFS", registrar_callback=None):
        self.tamanho_janela = tamanho_janela
        self.total_pacotes = total_pacotes
        self.escalonamento = escalonamento
        self.pacotes_enviados = 0
        self.pacotes_confirmados = 0
        self.semaforo = threading.Semaphore(tamanho_janela)
        self.lista_pacotes = self.gerar_pacotes()
        self.registrar = registrar_callback if registrar_callback else print
        self.tempos_processamento = {}

    def gerar_pacotes(self):
        tempo_criacao = time.time()
        return [{
            "id": i,
            "tempo_estimado": random.uniform(0.5, 2.0),
            "prioridade": random.randint(1, 10),
            "tempo_criacao": tempo_criacao
        } for i in range(1, self.total_pacotes + 1)]

    def ordenar_pacotes(self):
        if self.escalonamento == "FCFS":
            return sorted(self.lista_pacotes, key=lambda p: p["id"])
        elif self.escalonamento == "SJF":
            return sorted(self.lista_pacotes, key=lambda p: p["tempo_estimado"])
        elif self.escalonamento == "PS":
            return sorted(self.lista_pacotes, key=lambda p: -p["prioridade"])
        return self.lista_pacotes

    def enviar_pacote(self, id_pacote):
        pacote = next(p for p in self.lista_pacotes if p["id"] == id_pacote)
        if id_pacote not in self.tempos_processamento:
            tempo_inicio = time.time()
            self.tempos_processamento[id_pacote] = {
                "inicio": tempo_inicio,
                "espera": tempo_inicio - pacote["tempo_criacao"]
            }

        with self.semaforo:
            self.registrar(f"Enviando pacote {id_pacote}...")
            time.sleep(random.uniform(0.5, 2.0))
            if random.random() > 0.2:
                self.registrar(f"Pacote {id_pacote} entregue com sucesso.")
                self.confirmar_recebimento(id_pacote)
            else:
                self.registrar(f"Pacote {id_pacote} perdido. Reenviando...")
                self.reenviar_pacote(id_pacote)

    def confirmar_recebimento(self, id_pacote):
        fim = time.time()
        inicio = self.tempos_processamento[id_pacote]["inicio"]
        duracao = fim - inicio
        self.tempos_processamento[id_pacote]["fim"] = fim
        self.tempos_processamento[id_pacote]["duracao"] = duracao

        self.registrar(f"ACK recebido para o pacote {id_pacote} (Tempo total: {duracao:.2f} segundos)")
        self.pacotes_confirmados += 1
        self.semaforo.release()

    def reenviar_pacote(self, id_pacote):
        time.sleep(random.uniform(0.5, 1.0))
        self.enviar_pacote(id_pacote)

    def executar_simulacao(self):
        inicio = time.time()
        threads = []
        pacotes_ordenados = self.ordenar_pacotes()
        indice_pacote = 0
        numero_janela = 1

        while self.pacotes_confirmados < self.total_pacotes:
            janela_pacotes = []
            self.registrar(f"\n>>> Enviando janela {numero_janela}")
            while (indice_pacote < len(pacotes_ordenados) and
                   self.pacotes_enviados - self.pacotes_confirmados < self.tamanho_janela):
                pacote = pacotes_ordenados[indice_pacote]
                indice_pacote += 1
                janela_pacotes.append(pacote)
                self.pacotes_enviados += 1

            for pacote in janela_pacotes:
                thread = threading.Thread(target=self.enviar_pacote, args=(pacote["id"],))
                threads.append(thread)
                thread.start()

            for thread in threads:
                thread.join()

            numero_janela += 1

        fim = time.time()
        self.registrar("\nResumo dos tempos de processamento por pacote:")
        for id_pacote, tempos in sorted(self.tempos_processamento.items()):
            duracao = tempos.get("duracao", 0)
            espera = tempos.get("espera", 0)
            self.registrar(f"Pacote {id_pacote}: Tempo Total = {duracao:.2f}s | Espera = {espera:.2f}s")
        self.registrar(f"\nTodos os pacotes foram entregues com sucesso em {fim - inicio:.2f} segundos!")


class SimulacaoJanelaDeslizanteSemThreads:
    def __init__(self, tamanho_janela, total_pacotes, escalonamento="FCFS", registrar_callback=None):
        self.tamanho_janela = tamanho_janela
        self.total_pacotes = total_pacotes
        self.escalonamento = escalonamento
        self.pacotes_enviados = 0
        self.pacotes_confirmados = 0
        self.lista_pacotes = self.gerar_pacotes()
        self.registrar = registrar_callback if registrar_callback else print
        self.tempos_processamento = {}

    def gerar_pacotes(self):
        tempo_criacao = time.time()
        return [{
            "id": i,
            "tempo_estimado": random.uniform(0.5, 2.0),
            "prioridade": random.randint(1, 10),
            "tempo_criacao": tempo_criacao
        } for i in range(1, self.total_pacotes + 1)]

    def ordenar_pacotes(self):
        if self.escalonamento == "FCFS":
            return sorted(self.lista_pacotes, key=lambda p: p["id"])
        elif self.escalonamento == "SJF":
            return sorted(self.lista_pacotes, key=lambda p: p["tempo_estimado"])
        elif self.escalonamento == "PS":
            return sorted(self.lista_pacotes, key=lambda p: -p["prioridade"])
        return self.lista_pacotes

    def enviar_pacote(self, id_pacote):
        pacote = next(p for p in self.lista_pacotes if p["id"] == id_pacote)
        if id_pacote not in self.tempos_processamento:
            tempo_inicio = time.time()
            self.tempos_processamento[id_pacote] = {
                "inicio": tempo_inicio,
                "espera": tempo_inicio - pacote["tempo_criacao"]
            }

        with DummyContextManager():
            self.registrar(f"Enviando pacote {id_pacote}...")
            time.sleep(random.uniform(0.5, 2.0))
            if random.random() > 0.2:
                self.registrar(f"Pacote {id_pacote} entregue com sucesso.")
                self.confirmar_recebimento(id_pacote)
            else:
                self.registrar(f"Pacote {id_pacote} perdido. Reenviando...")
                self.reenviar_pacote(id_pacote)

    def confirmar_recebimento(self, id_pacote):
        fim = time.time()
        inicio = self.tempos_processamento[id_pacote]["inicio"]
        duracao = fim - inicio
        self.tempos_processamento[id_pacote]["fim"] = fim
        self.tempos_processamento[id_pacote]["duracao"] = duracao

        self.registrar(f"ACK recebido para o pacote {id_pacote} (Tempo total: {duracao:.2f} segundos)")
        self.pacotes_confirmados += 1

    def reenviar_pacote(self, id_pacote):
        time.sleep(random.uniform(0.5, 1.0))
        self.enviar_pacote(id_pacote)

    def executar_simulacao(self):
        inicio = time.time()
        pacotes_ordenados = self.ordenar_pacotes()
        indice_pacote = 0

        while self.pacotes_confirmados < self.total_pacotes:
            for _ in range(self.tamanho_janela):
                if indice_pacote < len(pacotes_ordenados):
                    pacote = pacotes_ordenados[indice_pacote]
                    indice_pacote += 1
                    self.enviar_pacote(pacote["id"])
                    self.pacotes_enviados += 1

        fim = time.time()
        self.registrar("\nResumo dos tempos de processamento por pacote:")
        for id_pacote, tempos in sorted(self.tempos_processamento.items()):
            duracao = tempos.get("duracao", 0)
            espera = tempos.get("espera", 0)
            self.registrar(f"Pacote {id_pacote}: Tempo Total = {duracao:.2f}s | Espera = {espera:.2f}s")
        self.registrar(f"\nTodos os pacotes foram entregues com sucesso em {fim - inicio:.2f} segundos!")


class InterfaceJanelaDeslizante:
    def __init__(self, raiz):
        self.raiz = raiz
        raiz.title("Simulação do Protocolo de Janela Deslizante")

        self.rotulo_janela = tk.Label(raiz, text="Tamanho da Janela:")
        self.rotulo_janela.grid(row=0, column=0)
        self.entrada_janela = tk.Entry(raiz)
        self.entrada_janela.insert(0, "4")
        self.entrada_janela.grid(row=0, column=1)

        self.rotulo_total = tk.Label(raiz, text="Total de Pacotes:")
        self.rotulo_total.grid(row=1, column=0)
        self.entrada_total = tk.Entry(raiz)
        self.entrada_total.insert(0, "10")
        self.entrada_total.grid(row=1, column=1)

        self.rotulo_escalonamento = tk.Label(raiz, text="Algoritmo de Escalonamento:")
        self.rotulo_escalonamento.grid(row=2, column=0)
        self.caixa_escalonamento = ttk.Combobox(raiz, values=["FCFS", "SJF", "PS"])
        self.caixa_escalonamento.current(0)
        self.caixa_escalonamento.grid(row=2, column=1)

        self.variavel_thread = tk.BooleanVar()
        self.caixa_thread = tk.Checkbutton(raiz, text="Usar Semáforo", variable=self.variavel_thread)
        self.caixa_thread.grid(row=3, columnspan=2)

        self.botao_iniciar = tk.Button(raiz, text="Iniciar Simulação", command=self.executar_simulacao)
        self.botao_iniciar.grid(row=4, columnspan=2, pady=10)

        self.caixa_log = tk.Text(raiz, height=20, width=70)
        self.caixa_log.grid(row=5, columnspan=2, padx=10, pady=10)

    def registrar(self, mensagem):
        self.caixa_log.insert(tk.END, mensagem + "\n")
        self.caixa_log.see(tk.END)
        self.raiz.update()

    def executar_simulacao(self):
        self.caixa_log.delete(1.0, tk.END)
        tamanho_janela = int(self.entrada_janela.get())
        total_pacotes = int(self.entrada_total.get())
        escalonamento = self.caixa_escalonamento.get()
        usar_thread = self.variavel_thread.get()

        classe_simulacao = SimulacaoJanelaDeslizante if usar_thread else SimulacaoJanelaDeslizanteSemThreads
        simulacao = classe_simulacao(tamanho_janela, total_pacotes, escalonamento, self.registrar)

        if usar_thread:
            thread = threading.Thread(target=simulacao.executar_simulacao)
            thread.start()
        else:
            simulacao.executar_simulacao()


if __name__ == "__main__":
    raiz = tk.Tk()
    app = InterfaceJanelaDeslizante(raiz)
    raiz.mainloop()
