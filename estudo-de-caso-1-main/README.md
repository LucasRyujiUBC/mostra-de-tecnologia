# Análise de Logs com IA

## Descrição

Este projeto visa automatizar a análise de logs de sistemas para detectar e classificar eventos, como erros, avisos e falhas críticas, utilizando técnicas de aprendizado de máquina. O objetivo é identificar padrões e anomalias nos logs, gerar alertas automáticos e produzir relatórios detalhados para análise posterior.

## Instruções de Instalação / Configuração

### 1. Crie um ambiente virtual (opcional, mas recomendado)

Recomenda-se criar um ambiente virtual para manter as dependências do projeto isoladas. Para isso, execute o seguinte comando:

python -m venv venv

### 2. Ative o ambiente virtual

- No Windows:

  venv\Scripts\activate

- No Linux/macOS:

  source venv/bin/activate

### 3. Instale as dependências

Após ativar o ambiente virtual, instale todas as dependências do projeto executando o seguinte comando:

pip install -r requirements.txt

Isso instalará as bibliotecas necessárias, incluindo:

- pandas: Para manipulação de dados.
- scikit-learn: Para a criação do modelo de aprendizado de máquina (RandomForestClassifier).
- matplotlib: Para geração de gráficos.
- seaborn: Para visualizações mais avançadas.

### 4. Configuração do Caminho de Logs

No script Python, o caminho do arquivo de log deve ser configurado para o local correto onde seus logs estão armazenados. Verifique o seguinte no código:

caminho_logs = r"C:\caminho\para\seu\log.txt"

Substitua o caminho pelo local onde os logs estão salvos em sua máquina.

### 5. Executando o Projeto

Após configurar o caminho do arquivo de log, execute o script principal para iniciar a análise:

python programa.py

### 6. Resultados

- O relatório gerado será salvo no diretório especificado no código, com o nome relatorio.txt.
- Gráficos gerados serão exibidos em uma janela interativa.

## Dependências

As dependências para rodar o projeto estão listadas no arquivo requirements.txt. Caso queira instalar manualmente as bibliotecas, pode usar o seguinte comando:

pip install pandas scikit-learn matplotlib seaborn

## Autores

Lucas Ryuji Fujimoto
Britney Brevio dos Santos Lima
Thiago Vinicius Araújo

## Considerações finais

Este projeto foi desenvolvido com o objetivo de fornecer uma solução automatizada para análise de logs e detecção de eventos anômalos, melhorando a eficiência no monitoramento de sistemas.
