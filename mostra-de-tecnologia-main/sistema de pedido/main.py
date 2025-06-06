import tkinter as tk
from tkinter import messagebox
import datetime
import os

# Caminhos do banco de dados
DB_PATH = "log/pedidos.txt"
LOG_PATH = "log/logs_drive_thru.txt"

# Função para registrar eventos no arquivo de logs
def registrar_log(tipo, mensagem):
    timestamp = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    log_entry = f"{timestamp} {tipo}: {mensagem}\n"

    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as arquivo_log:
        arquivo_log.write(log_entry)

# Função para obter o próximo número de pedido
def obter_proximo_numero_pedido():
    if not os.path.exists(DB_PATH):
        return 1

    with open(DB_PATH, "r", encoding="utf-8") as arquivo:
        linhas = arquivo.readlines()
        if not linhas:
            return 1
        ultimo_pedido = int(linhas[-1].split(",")[0])
        return ultimo_pedido + 1

# Função para salvar pedido no banco
def salvar_pedido(numero_pedido, status):
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with open(DB_PATH, "a", encoding="utf-8") as arquivo:
        arquivo.write(f"{numero_pedido},{status}\n")

# Mapeamento de problemas por etapa
problemas_por_etapa = {
    "Iniciado": ["Pagamento não processado", "Pedido recusado pelo cliente"],
    "Preparado": ["Pedido frio", "Erro ao adicionar condimentos", "Produto indisponível"],
    "Entregue": ["Item faltando", "Item incorreto", "Pedido trocado", "Embalagem danificada", "Bebida derramada"]
}

# Classe Pedido
class Pedido:
    def __init__(self):
        self.numero = obter_proximo_numero_pedido()
        self.status = "Iniciado"
        salvar_pedido(self.numero, self.status)
        registrar_log("INFO", f"Pedido {self.numero} iniciado no drive-thru")

    def preparar(self):
        if self.status != "Iniciado":
            registrar_log("ERROR", f"Pedido {self.numero} não pode ser preparado sem ter sido iniciado!")
            return
        
        self.status = "Preparado"
        salvar_pedido(self.numero, self.status)
        registrar_log("INFO", f"Pedido {self.numero} preparado na cozinha")

    def entregar(self):
        if self.status != "Preparado":
            registrar_log("ERROR", f"Pedido {self.numero} não pode ser entregue sem ter sido preparado!")
            return
        
        self.status = "Entregue"
        salvar_pedido(self.numero, self.status)
        registrar_log("INFO", f"Pedido {self.numero} entregue ao cliente")

    def cancelar(self):
        """Cancela o pedido e registra no log"""
        self.status = "Cancelado"
        salvar_pedido(self.numero, self.status)
        registrar_log("WARNING", f"Pedido {self.numero} cancelado pelo usuário")

# Interface gráfica
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
        self.lista_pedidos.bind("<<ListboxSelect>>", lambda event: self.atualizar_lista_problemas())

        self.botao_preparar = tk.Button(root, text="Preparar Pedido", command=self.preparar_pedido)
        self.botao_preparar.pack()

        self.botao_entregar = tk.Button(root, text="Entregar Pedido", command=self.entregar_pedido)
        self.botao_entregar.pack()

        self.botao_cancelar = tk.Button(root, text="Cancelar Pedido", command=self.cancelar_pedido)
        self.botao_cancelar.pack()

        self.carregar_pedidos_existentes()

        # Criar lista suspensa de problemas recorrentes
        self.label_problema = tk.Label(root, text="Registrar Problema no Pedido", font=("Arial", 12))
        self.label_problema.pack()

        self.problema_var = tk.StringVar(root)
        self.problema_var.set("Selecione um problema")  # Valor padrão

        self.menu_problemas = tk.OptionMenu(root, self.problema_var, "")
        self.menu_problemas.pack()

        self.botao_registrar_problema = tk.Button(root, text="Registrar Problema", command=self.registrar_problema)
        self.botao_registrar_problema.pack()

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
            pedido = next((p for p in self.pedidos if p.numero == numero_pedido), None)
            if pedido:
                pedido.preparar()
                self.lista_pedidos.delete(index)
                self.lista_pedidos.insert(index, f"Pedido {pedido.numero} - {pedido.status}")

    def entregar_pedido(self):
        selecionado = self.lista_pedidos.curselection()
        if selecionado:
            index = selecionado[0]
            numero_pedido = int(self.lista_pedidos.get(index).split()[1])
            pedido = next((p for p in self.pedidos if p.numero == numero_pedido), None)
            if pedido:
                pedido.entregar()
                self.lista_pedidos.delete(index)
                self.lista_pedidos.insert(index, f"Pedido {pedido.numero} - {pedido.status}")

    def cancelar_pedido(self):
        selecionado = self.lista_pedidos.curselection()
        if selecionado:
            index = selecionado[0]
            numero_pedido = int(self.lista_pedidos.get(index).split()[1])
            pedido = next((p for p in self.pedidos if p.numero == numero_pedido), None)
            if pedido:
                pedido.cancelar()
                self.lista_pedidos.delete(index)
                messagebox.showinfo("Pedido Cancelado", f"Pedido {pedido.numero} foi cancelado!")

    def atualizar_lista_problemas(self):
        """ Atualiza a lista de problemas baseada na etapa do pedido """
        selecionado = self.lista_pedidos.curselection()
        if selecionado:
            index = selecionado[0]
            numero_pedido = int(self.lista_pedidos.get(index).split()[1])
            pedido = next((p for p in self.pedidos if p.numero == numero_pedido), None)
            if pedido:
                self.menu_problemas["menu"].delete(0, "end")
                problemas = problemas_por_etapa.get(pedido.status, [])
                for problema in problemas:
                    self.menu_problemas["menu"].add_command(label=problema, command=lambda p=problema: self.problema_var.set(p))

    def registrar_problema(self):
        selecionado = self.lista_pedidos.curselection()
        if selecionado:
            index = selecionado[0]
            numero_pedido = int(self.lista_pedidos.get(index).split()[1])
            problema = self.problema_var.get()
            if problema and problema != "Selecione um problema":
                registrar_log("ERROR", f"Pedido {numero_pedido} {problema}")  # Removido "-"
                messagebox.showinfo("Erro Registrado", f"Erro '{problema}' registrado para Pedido {numero_pedido}!")
            else:
                messagebox.showwarning("Erro", "Por favor, selecione um problema válido!")


# Criando a aplicação
if __name__ == "__main__":
    root = tk.Tk()
    app = DriveThruApp(root)
    root.mainloop()
