import streamlit as st
import pandas as pd
import datetime
import plotly.express as px
import warnings
import re

# Suprime avisos irrelevantes
warnings.filterwarnings("ignore", message=".*missing ScriptRunContext.*")

def process_logs(file_content):
    """
    Processa o conteúdo dos logs fornecido como texto.

    Cada linha deve seguir o formato:
      [Timestamp] TIPO: Mensagem

    Exemplo:
      [2025-05-20 19:54:15] INFO: Mensagem de log
    """
    linhas = file_content.splitlines()
    dados = []
    for linha in linhas:
        if not linha.strip():
            continue
        partes = linha.strip().split(" ", 2)
        if len(partes) >= 3:
            timestamp = partes[0] + " " + partes[1]  # Ex: "[2025-05-20 19:54:15]"
            resto = partes[2]
            if ": " in resto:
                tipo, mensagem = resto.split(": ", 1)
                dados.append([timestamp, tipo, mensagem])
    
    df = pd.DataFrame(dados, columns=["Timestamp", "Tipo", "Mensagem"])
    # Converte o timestamp extraindo o valor entre colchetes
    df["Timestamp"] = pd.to_datetime(df["Timestamp"].str.extract(r"\[(.*?)\]")[0], errors="coerce")
    df = df.dropna(subset=["Timestamp"])
    
    # Colunas adicionais: Data, Semana, Dia da Semana, Hora
    df["Data"] = df["Timestamp"].dt.date
    df["Semana"] = df["Timestamp"].dt.isocalendar().week
    df["Dia_Semana"] = df["Timestamp"].dt.day_name()
    df["Hora"] = df["Timestamp"].dt.hour
    
    # Renomeia os tipos para classes de log mais amigáveis
    mapping = {
        "INFO": "Informação",
        "WARNING": "Aviso",
        "ERROR": "Erro",
        "CRITICAL": "Crítico"
    }
    df["Classe"] = df["Tipo"].map(mapping)
    
    # Determina se o log está relacionado a um pedido (buscando a ocorrência da palavra "pedido")
    df["IsPedido"] = df["Mensagem"].str.contains("pedido", case=False, na=False)
    
    return df

def main():
    st.title("Dashboard de Logs - Business Intelligence")
    st.write("Utilize os filtros na barra lateral e explore as métricas e visualizações interativas.")
    
    # Upload do arquivo de logs
    uploaded_file = st.file_uploader("Selecione um arquivo de logs (.txt)", type=["txt"])
    
    if uploaded_file is not None:
        try:
            file_content = uploaded_file.getvalue().decode("utf-8")
        except Exception as e:
            st.error(f"Erro ao ler o arquivo: {e}")
            return
        
        df_logs = process_logs(file_content)
        
        # --- Filtros na barra lateral ---
        st.sidebar.header("Filtros")
        
        # Filtro por intervalo de datas
        if not df_logs.empty:
            min_date = df_logs["Data"].min()
            max_date = df_logs["Data"].max()
        else:
            min_date = max_date = datetime.date.today()
            
        intervalo = st.sidebar.date_input("Intervalo de datas", [min_date, max_date])
        if isinstance(intervalo, list) and len(intervalo) == 2:
            d_inicial, d_final = intervalo
            df_logs = df_logs[(df_logs["Data"] >= d_inicial) & (df_logs["Data"] <= d_final)]
        
        # Filtro por classes (após renomeação)
        classes_disponiveis = df_logs["Classe"].dropna().unique().tolist()
        classes_selecionadas = st.sidebar.multiselect("Selecione as classes:", options=classes_disponiveis, default=classes_disponiveis)
        df_logs = df_logs[df_logs["Classe"].isin(classes_selecionadas)]
        
        # Filtro por texto na mensagem
        termo_busca = st.sidebar.text_input("Buscar texto na mensagem:")
        if termo_busca:
            df_logs = df_logs[df_logs["Mensagem"].str.contains(termo_busca, case=False, na=False)]
        
        # Exibe os logs processados
        st.markdown("### Logs Processados")
        st.dataframe(df_logs.reset_index(drop=True))
        
        st.markdown("## Métricas e Visualizações")
        
        # 1. LOGS POR DIA (por Classe) – Gráfico contínuo ao longo do tempo
        if not df_logs.empty:
            # Agrupa os logs por Data e Classe para obter a contagem diária
            daily_class = df_logs.groupby(["Data", "Classe"]).size().reset_index(name="Count")
            # Adiciona o dia da semana para cada data (apenas como informação adicional)
            daily_class["Dia_Semana"] = pd.to_datetime(daily_class["Data"]).dt.day_name()
            
            fig_line_continuous = px.line(
                daily_class,
                x="Data",
                y="Count",
                color="Classe",
                markers=True,
                title="Logs por Dia (por Classe) – Dias contínuos",
                labels={"Data": "Data", "Count": "Número de Logs"}
            )
            st.plotly_chart(fig_line_continuous, use_container_width=True)
        else:
            st.info("Nenhum log para gerar o gráfico de logs diários.")
        
        # 2. MÉDIA DE LOGS POR CLASSE (Gráfico de Pizza)
        if not df_logs.empty:
            total_dias = df_logs["Data"].nunique()
            media_por_classe = (df_logs.groupby("Classe").size() / total_dias).reset_index(name="Average")
            fig_pie_media_classe = px.pie(
                media_por_classe,
                names="Classe",
                values="Average",
                title="Média de Logs por Classe (por Dia)",
                template="plotly_white"
            )
            st.plotly_chart(fig_pie_media_classe, use_container_width=True)
        else:
            st.info("Nenhum log para mostrar a média por classe.")
        
        # 3. DESEMPENHO E EFICIÊNCIA DE PEDIDOS
        st.markdown("## Desempenho e Eficiência de Pedidos")
        df_pedidos = df_logs[df_logs["IsPedido"]]
        if not df_pedidos.empty:
            total_pedidos = len(df_pedidos)
            sucesso_pedidos = len(df_pedidos[df_pedidos["Tipo"] == "INFO"])
            erro_pedidos = total_pedidos - sucesso_pedidos
            eficiencia = (sucesso_pedidos / total_pedidos * 100) if total_pedidos > 0 else 0
            
            st.write(f"**Total de Pedidos:** {total_pedidos}")
            st.write(f"**Pedidos com Sucesso:** {sucesso_pedidos}")
            st.write(f"**Pedidos com Erro:** {erro_pedidos}")
            st.write(f"**Eficiência de Pedidos:** {eficiencia:.2f}%")
            
            # Gráfico de pizza: Pedidos com Sucesso vs Erro (considerando apenas os pedidos)
            status_df = pd.DataFrame({
                "Status": ["Sucesso", "Erro"],
                "Quantidade": [sucesso_pedidos, erro_pedidos]
            })
            fig_status = px.pie(
                status_df,
                names="Status",
                values="Quantidade",
                title="Pedidos: Sucesso vs Erro",
                template="plotly_white"
            )
            st.plotly_chart(fig_status, use_container_width=True)
            
            # Gráfico de pizza: Detalhamento das Descrições dos Erros
            # Utiliza **todos os logs que não são INFO** para detalhar os erros
            df_erros = df_logs[df_logs["Tipo"] != "INFO"]
            if not df_erros.empty:
                # Função para generalizar a mensagem do erro:
                # Converte para minúsculas, remove dígitos e pontuação e extrai as três primeiras palavras.
                def generalize_error(msg):
                    msg = msg.lower()
                    msg = re.sub(r'\d+', '', msg)        # remove dígitos
                    msg = re.sub(r'[^\w\s]', '', msg)      # remove pontuação
                    words = msg.split()
                    return " ".join(words[:3]) if len(words) >= 3 else " ".join(words)
                
                df_erros = df_erros.copy()  # Para evitar SettingWithCopyWarning
                df_erros["Erro_Generalizado"] = df_erros["Mensagem"].apply(generalize_error)
                erro_desc = df_erros["Erro_Generalizado"].value_counts().reset_index()
                erro_desc.columns = ["Descrição Geral do Erro", "Quantidade"]
                
                fig_error_desc = px.pie(
                    erro_desc,
                    names="Descrição Geral do Erro",
                    values="Quantidade",
                    title="Detalhamento das Descrições dos Erros (todos os logs que não são INFO)",
                    template="plotly_white"
                )
                st.plotly_chart(fig_error_desc, use_container_width=True)
            else:
                st.info("Nenhum log de erro encontrado.")
        else:
            st.info("Nenhum log relacionado a pedidos foi encontrado.")
        
        # 4. DESEMPENHO DE PEDIDOS AO LONGO DO TEMPO
        st.markdown("## Desempenho de Pedidos ao Longo do Tempo")
        if not df_pedidos.empty:
            pedidos_por_dia = df_pedidos.groupby("Data").size().reset_index(name="Pedidos")
            fig_pedidos_linha = px.line(
                pedidos_por_dia,
                x="Data",
                y="Pedidos",
                markers=True,
                title="Número de Pedidos por Dia",
                labels={"Data": "Data", "Pedidos": "Número de Pedidos"},
                template="plotly_white"
            )
            st.plotly_chart(fig_pedidos_linha, use_container_width=True)
        else:
            st.info("Nenhum pedido para exibir o desempenho diário.")
            
        # 5. PICO DE MOVIMENTO: Comparativo de Volume de Pedidos x Erros por Hora
        st.markdown("## Pico de Movimento")
        pedidos_por_hora = df_pedidos.groupby("Hora").size().reset_index(name="Pedidos")
        erros_por_hora = df_logs[df_logs["Tipo"] == "ERROR"].groupby("Hora").size().reset_index(name="Erros")
        pico_df = pd.merge(pedidos_por_hora, erros_por_hora, on="Hora", how="outer").fillna(0)
        pico_df = pico_df.sort_values("Hora")
        fig_pico = px.bar(
            pico_df,
            x="Hora",
            y=["Pedidos", "Erros"],
            title="Comparativo: Pedidos vs Erros por Hora",
            labels={"value": "Volume", "Hora": "Hora do Dia"},
            template="plotly_white"
        )
        fig_pico.update_layout(barmode="group")
        st.plotly_chart(fig_pico, use_container_width=True)
        
    else:
        st.info("Por favor, faça o upload de um arquivo de logs (.txt).")

if __name__ == "__main__":
    main()
