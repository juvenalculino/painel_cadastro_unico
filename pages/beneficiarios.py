import streamlit as st
import json
import os
import pandas as pd
from pathlib import Path
import locale


# Tentar configurar o locale para pt_BR.UTF-8, com fallback para configuração padrão
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except locale.Error:
    locale.setlocale(locale.LC_ALL, '')  # Usa o padrão do sistema se pt_BR não estiver disponível
    st.warning("Locale 'pt_BR.UTF-8' não disponível. Usando configuração padrão do sistema.")

# Caminho para os arquivos Parquet
parquet_dir = os.path.join(Path(__file__).parent.parent, './dados/dados_por_municipio/')

# Caminho para o arquivo de municípios
caminho_arquivo = os.path.join(Path(__file__).parent.parent, 'dados', 'municipios.json')

# Função para carregar os municípios do JSON
def carregar_municipios():
    with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
        municipios = json.load(arquivo)
    return municipios['data']

# Filtra municípios por estado
def filtrar_municipios_por_estado(municipios, estado):
    return [m for m in municipios if m['Uf'] == estado]

# Obtém o código do município pelo nome
def get_codigo_municipio(nome_municipio, municipios):
    for municipio in municipios:
        if municipio['Nome'].lower() == nome_municipio.lower():
            return municipio['Codigo']
    return None

# Função para carregar beneficiários de um arquivo Parquet
def carregar_beneficiarios_parquet(codigo_municipio):
    arquivo_parquet = os.path.join(parquet_dir, f"{codigo_municipio}.parquet")
    
    if os.path.exists(arquivo_parquet):
        df = pd.read_parquet(arquivo_parquet)
        
        # Renomear colunas para facilitar o uso
        df = df.rename(columns={
            "NIS FAVORECIDO": "Nis",
            "NOME FAVORECIDO": "Nome",
            "VALOR PARCELA": "Parcela"
        })
        
        # Garantir que "Parcela" seja float e substituir NaN por 0.0
        df["Parcela"] = pd.to_numeric(df["Parcela"], errors='coerce').fillna(0.0)
        
        return df
    else:
        return None

# Função para exibir os beneficiários no Streamlit
def exibir_beneficiarios(df):
    if df is not None and not df.empty:
        st.subheader("Beneficiários do Bolsa Família")
        st.write(f"Total de registros encontrados: {len(df)}")
        
        # Criar uma coluna formatada como moeda brasileira para exibição
        df["Parcela_formatada"] = df["Parcela"].map(lambda x: locale.currency(x, grouping=True, symbol=True))
        
        # Ordenar pelo valor numérico original
        df = df.sort_values(by="Parcela", ascending=True)
        
        # Criar duas colunas para exibir gráfico e tabela lado a lado
        col1, col2 = st.columns(2)
        
        # Coluna 1: Gráfico de barras
        with col1:
            st.subheader("Distribuição por Valor da Parcela")
            # Calcular quantidade de beneficiários abaixo e acima de 600
            abaixo_600 = len(df[df["Parcela"] <= 599])
            acima_600 = len(df[df["Parcela"] >= 600])
            
            # Criar um DataFrame para o gráfico
            dados_grafico = pd.DataFrame({
                "Categoria": ["Abaixo de R$ 600", "Acima de R$ 600"],
                "Quantidade": [abaixo_600, acima_600]
            })
            
            # Exibir o gráfico de barras
            st.bar_chart(dados_grafico.set_index("Categoria")["Quantidade"])
        
        # Coluna 2: Tabela de dados
        with col2:
            st.subheader("Lista de Beneficiários")
            #st.table(df[["Nome", "Nis", "Parcela_formatada"]].rename(columns={"Parcela_formatada": "Parcela"}))
            #st.dataframe(df[["nome", "nis", "Parcela_formatada"]].rename(columns={"Parcela_formatada": "Parcela"}))
            st.dataframe(df[['Nome', 'Nis', 'Parcela_formatada']].rename(columns={'Parcela_formatada': 'Parcela'}), use_container_width=True, hide_index=True)
    else:
        st.error("Nenhum beneficiário encontrado para este município.")

# Interface principal
def show_pbf():
    municipios = carregar_municipios()
    
    st.write("---")
    st.write("### Buscar Beneficiários por Município")
    estados = sorted(set(m['Uf'] for m in municipios))
    estado_selecionado = st.selectbox("Escolha um estado:", estados)
    municipios_filtrados = filtrar_municipios_por_estado(municipios, estado_selecionado)
    nomes_municipios = [m['Nome'] for m in municipios_filtrados]
    municipio_selecionado = st.selectbox("Escolha um município:", nomes_municipios)
    
    if st.button("Buscar Beneficiários"):
        codigo = get_codigo_municipio(municipio_selecionado, municipios_filtrados)
        if codigo:
            df_beneficiarios = carregar_beneficiarios_parquet(codigo)
            exibir_beneficiarios(df_beneficiarios)
        else:
            st.error("Município não encontrado.")

if __name__ == "__main__":
    show_pbf()