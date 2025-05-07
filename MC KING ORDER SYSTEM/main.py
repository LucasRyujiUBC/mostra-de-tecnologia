import tkinter as tk
from tkinter import messagebox
import datetime
import os

# Caminho do banco de dados em TXT
DB_PATH = "log/pedidos.txt"
LOG_PATH = "log/logs_drive_thru.txt"

# Função para registrar eventos no arquivo de logs
def registrar_log(tipo, mensagem):
    timestamp = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    log_entry = f"{timestamp} {tipo}: {mensagem}\n"
    
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as arquivo_log:
        arquivo_log.write(log_entry)

# Função para obter o próximo número de pedido (auto incremental)
def obter_proximo_numero_pedido():
    if not os.path.exists(DB_PATH):
        return 1  # Primeiro pedido

    with open(DB_PATH, "r", encoding="utf-8") as arquivo:
        linhas = arquivo.readlines()
        if not linhas:
            return 1
        ultimo_pedido = int(linhas[-1].split(",")[0])  # Pega o último ID de pedido
        return ultimo_pedido + 1

# Função para salvar pedido no banco
def salvar_pedido(numero_pedido, status):
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with open(DB_PATH, "a", encoding="utf-8") as arquivo:
        arquivo.write(f"{numero_pedido},{status}\n")

# Classe para gerenciar pedidos
class Pedido:
    def __init__(self):
        self.numero = obter_proximo_numero_pedido()
        self.status = "Iniciado"
        salvar_pedido(self.numero, self.status)
        registrar_log("INFO", f"Pedido {self.numero} iniciado no drive-thru")

    def preparar(self):
        self.status = "Preparado"
        salvar_pedido(self.numero, self.status)
        registrar_log("INFO", f"Pedido {self.numero} preparado na cozinha")

    def entregar(self):
        self.status = "Entregue"
        salvar_pedido(self.numero, self.status)
        registrar_log("INFO", f"Pedido {self.numero} entregue ao cliente")

# Interface gráfica do sistema
class DriveThruApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema Drive-Thru")
        self.pedidos = []

        self.label = tk.Label(root, text="Gerenciamento de Pedidos", font=("Arial", 14))
        self.label.pack()

        self.botao_novo_pedido = tk.Button(root, text="Novo Pedido", command=self.criar_pedido)
        self.botao_novo_pedido.pack()

        self.lista_pedidos = tk.Listbox(root)
        self.lista_pedidos.pack()

        self.botao_preparar = tk.Button(root, text="Preparar Pedido", command=self.preparar_pedido)
        self.botao_preparar.pack()

        self.botao_entregar = tk.Button(root, text="Entregar Pedido", command=self.entregar_pedido)
        self.botao_entregar.pack()

        # Botão para registrar erros
        self.botao_registrar_erro = tk.Button(root, text="Registrar Erro", command=self.registrar_erro)
        self.botao_registrar_erro.pack()

        self.carregar_pedidos_existentes()

    def carregar_pedidos_existentes(self):
        if os.path.exists(DB_PATH):
            with open(DB_PATH, "r", encoding="utf-8") as arquivo:
                linhas = arquivo.readlines()
                for linha in linhas:
                    numero_pedido, status = linha.strip().split(",")
                    self.lista_pedidos.insert(tk.END, f"Pedido {numero_pedido} - {status}")

    def criar_pedido(self):
        pedido = Pedido()
        self.pedidos.append(pedido)
        self.lista_pedidos.insert(tk.END, f"Pedido {pedido.numero} - {pedido.status}")

    def preparar_pedido(self):
        selecionado = self.lista_pedidos.curselection()
        if selecionado:
            index = selecionado[0]
            numero_pedido = int(self.lista_pedidos.get(index).split()[1])
            pedido = next(p for p in self.pedidos if p.numero == numero_pedido)
            pedido.preparar()
            self.lista_pedidos.delete(index)
            self.lista_pedidos.insert(index, f"Pedido {pedido.numero} - {pedido.status}")

    def entregar_pedido(self):
        selecionado = self.lista_pedidos.curselection()
        if selecionado:
            index = selecionado[0]
            numero_pedido = int(self.lista_pedidos.get(index).split()[1])
            pedido = next(p for p in self.pedidos if p.numero == numero_pedido)
            pedido.entregar()
            self.lista_pedidos.delete(index)
            self.lista_pedidos.insert(index, f"Pedido {pedido.numero} - {pedido.status}")

    def registrar_erro(self):
        # Criar janela de erro
        janela_erro = tk.Toplevel(self.root)
        janela_erro.title("Registrar Erro")

        tk.Label(janela_erro, text="Selecione o tipo de erro:").pack()

        # Mapeamento dos tipos de erro
        tipos_erro = {
            "CRITICAL - CRÍTICO": "CRITICAL",
            "WARNING - AVISO": "WARNING",
            "ERROR - ERRO": "ERROR"
        }

        tipo_erro = tk.StringVar(janela_erro)
        tipo_erro.set("ERROR - ERRO")  # Valor padrão

        # Criar lista de opções formatadas
        tk.OptionMenu(janela_erro, tipo_erro, *tipos_erro.keys()).pack()

        tk.Label(janela_erro, text="Descrição do erro:").pack()
        entrada_descricao = tk.Entry(janela_erro, width=40)
        entrada_descricao.pack()

        def confirmar_erro():
            descricao = entrada_descricao.get()
            if descricao:
                registrar_log(tipos_erro[tipo_erro.get()], descricao)
                messagebox.showinfo("Erro Registrado", f"Erro '{tipo_erro.get()}' registrado com sucesso!")
                janela_erro.destroy()
            else:
                messagebox.showwarning("Erro", "Por favor, insira uma descrição!")

        tk.Button(janela_erro, text="Registrar", command=confirmar_erro).pack()

# Criando a aplicação
if __name__ == "__main__":
    root = tk.Tk()
    app = DriveThruApp(root)
    root.mainloop()
