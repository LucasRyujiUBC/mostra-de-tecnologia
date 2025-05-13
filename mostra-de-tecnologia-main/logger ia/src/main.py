import os
import pandas as pd
import tkinter as tk
from tkinter import filedialog, ttk
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Função para carregar arquivo
def carregar_arquivo():
    global caminho_logs
    caminho_logs = filedialog.askopenfilename(title="Selecione o arquivo de logs", filetypes=[("Arquivos de Texto", "*.txt"), ("Todos os Arquivos", "*.*")])
    if caminho_logs:
        label_arquivo.config(text=f"📁 Arquivo Selecionado: {os.path.basename(caminho_logs)}", anchor="w")

# Função para processar logs
def processar_logs():
    if not caminho_logs:
        label_status.config(text="⚠ Nenhum arquivo selecionado!", anchor="w")
        return
    
    logs = []
    try:
        with open(caminho_logs, "r", encoding="utf-8") as arquivo:
            logs = arquivo.readlines()
    except Exception as e:
        label_status.config(text=f"🚫 Erro ao carregar logs: {e}", anchor="w")
        return
    
    dados = []
    for linha in logs:
        partes = linha.strip().split(" ", 2)
        if len(partes) >= 3:
            timestamp, resto = partes[0] + " " + partes[1], partes[2]
            if ": " in resto:
                tipo, mensagem = resto.split(": ", 1)
                dados.append([timestamp, tipo, mensagem])

    global df_logs
    df_logs = pd.DataFrame(dados, columns=["Timestamp", "Tipo", "Mensagem"])
    df_logs["Timestamp"] = pd.to_datetime(df_logs["Timestamp"].str.extract(r"\[(.*?)\]")[0], errors="coerce")
    df_logs["Categoria"] = df_logs["Tipo"].map({"INFO": 0, "WARNING": 1, "ERROR": 2, "CRITICAL": 3, "CANCELADO": 4}).fillna(0)

    label_status.config(text="✅ Logs processados com sucesso!", anchor="w")

# Função para exibir relatório detalhado
def gerar_relatorio():
    total_eventos = len(df_logs)
    eventos_por_tipo = df_logs["Tipo"].value_counts()
    eventos_por_dia = df_logs.groupby(df_logs["Timestamp"].dt.date).size()
    
    # KPIs
    media_erros = df_logs[df_logs["Tipo"] == "ERROR"].shape[0] / total_eventos * 100
    media_criticos = df_logs[df_logs["Tipo"] == "CRITICAL"].shape[0] / total_eventos * 100
    media_avisos = df_logs[df_logs["Tipo"] == "WARNING"].shape[0] / total_eventos * 100
    total_cancelamentos = df_logs[df_logs["Tipo"] == "CANCELADO"].shape[0]

    df_logs["Dia_Semana"] = df_logs["Timestamp"].dt.day_name()
    pedidos_por_dia_semana = df_logs.groupby("Dia_Semana").size()

    texto_relatorio.set(f"""
📊 RELATÓRIO ESTRATÉGICO DOS LOGS
📅 Data de Geração: {pd.to_datetime("today").strftime("%d/%m/%Y")}
📁 Arquivo Processado: {os.path.basename(caminho_logs)}

🔍 ANÁLISE GERAL:
- Total de eventos registrados: {total_eventos}
- Distribuição de eventos:
{eventos_por_tipo.to_string()}

📈 KPI – Indicadores Estratégicos:
- Média de Erros: {media_erros:.2f}%
- Média de Eventos Críticos: {media_criticos:.2f}%
- Média de Eventos de Aviso: {media_avisos:.2f}%
- Total de Cancelamentos: {total_cancelamentos}
- Tendência de eventos ao longo dos dias:
{eventos_por_dia.to_string()}
- Distribuição de pedidos por dia da semana:
{pedidos_por_dia_semana.to_string()}
""")

# Função para análise de logs por classe
def analisar_por_classe(tipo_evento):
    df_filtrado = df_logs[df_logs["Tipo"] == tipo_evento]

    if df_filtrado.empty:
        label_classe.config(text=f"⚠ Nenhum evento do tipo {tipo_evento} encontrado!", anchor="w")
        return

    eventos_por_dia = df_filtrado.groupby(df_filtrado["Timestamp"].dt.date).size()

    label_classe.config(text=f"""
📌 Análise de Logs - Classe: {tipo_evento}
- Total de eventos {tipo_evento}: {df_filtrado.shape[0]}
- Evolução ao longo do tempo:
{eventos_por_dia.to_string()}
""")

# Função para abrir dashboard
def abrir_dashboard():
    for widget in aba_dashboard.winfo_children():
        widget.destroy()

    fig, ax = plt.subplots(figsize=(8, 4))
    sns.countplot(data=df_logs, x="Tipo", palette="viridis", ax=ax)
    ax.set_title("Distribuição de Eventos nos Logs")
    ax.set_xlabel("Tipo de Evento")
    ax.set_ylabel("Quantidade")

    canvas = FigureCanvasTkAgg(fig, master=aba_dashboard)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

# Interface gráfica melhorada
janela = tk.Tk()
janela.title("Business Intelligence - Gestão Estratégica")
janela.geometry("900x650")

notebook = ttk.Notebook(janela)
notebook.pack(expand=True, fill=tk.BOTH)

# Aba Upload
aba_upload = ttk.Frame(notebook)
notebook.add(aba_upload, text="📂 Upload")

btn_selecionar = tk.Button(aba_upload, text="Selecionar Arquivo", command=carregar_arquivo)
btn_selecionar.pack(fill=tk.X, padx=10, pady=5)
label_arquivo = tk.Label(aba_upload, text="Nenhum arquivo selecionado", anchor="w")
label_arquivo.pack(fill=tk.X, padx=10)

btn_processar = tk.Button(aba_upload, text="Processar Logs", command=processar_logs)
btn_processar.pack(fill=tk.X, padx=10, pady=5)
label_status = tk.Label(aba_upload, text="Status: Aguardando processamento...", anchor="w")
label_status.pack(fill=tk.X, padx=10)

# Aba Relatório
aba_relatorio = ttk.Frame(notebook)
notebook.add(aba_relatorio, text="📊 Relatório")

texto_relatorio = tk.StringVar()
label_relatorio = tk.Label(aba_relatorio, textvariable=texto_relatorio, anchor="w", justify="left")
label_relatorio.pack(fill=tk.BOTH, expand=True, padx=10)

btn_relatorio = tk.Button(aba_relatorio, text="Gerar Relatório Detalhado", command=gerar_relatorio)
btn_relatorio.pack(fill=tk.X, padx=10, pady=5)

# Aba Análise por Classe
aba_classe = ttk.Frame(notebook)
notebook.add(aba_classe, text="🔍 Análise por Classe")

label_classe = tk.Label(aba_classe, text="Selecione uma classe para análise:", anchor="w")
label_classe.pack(fill=tk.X, padx=10)

classes_disponiveis = ["INFO", "WARNING", "ERROR", "CRITICAL", "CANCELADO"]
for classe in classes_disponiveis:
    btn_classe = tk.Button(aba_classe, text=f"Analisar {classe}", command=lambda c=classe: analisar_por_classe(c))
    btn_classe.pack(fill=tk.X, padx=10, pady=2)

# Aba Dashboard
aba_dashboard = ttk.Frame(notebook)
notebook.add(aba_dashboard, text="📈 Dashboard")

btn_dashboard = tk.Button(aba_dashboard, text="Gerar Dashboard", command=abrir_dashboard)
btn_dashboard.pack(fill=tk.X, padx=10, pady=5)

janela.mainloop()
