import streamlit as st
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

# Caminho para o diretório principal dos dados
dados_dir = os.path.join(Path(__file__).parent.parent, 'dados', 'dados_separados')

# Função para listar os estados (UFs) a partir das pastas
def listar_estados():
    if os.path.exists(dados_dir):
        return [nome for nome in os.listdir(dados_dir) if os.path.isdir(os.path.join(dados_dir, nome))]
    else:
        st.error(f"Diretório de dados não encontrado: {dados_dir}")
        return []

# Função para listar os municípios de um estado (UF)
def listar_municipios_por_estado(uf):
    pasta_uf = os.path.join(dados_dir, uf)
    if os.path.exists(pasta_uf):
        return [nome.replace('.parquet', '') for nome in os.listdir(pasta_uf) if nome.endswith('.parquet')]
    else:
        return []

# Função para carregar beneficiários de um arquivo Parquet baseado em UF e nome do município
def carregar_beneficiarios_parquet(uf, nome_municipio):
    arquivo_parquet = os.path.join(dados_dir, uf, f"{nome_municipio}.parquet")
    
    if os.path.exists(arquivo_parquet):
        df = pd.read_parquet(arquivo_parquet)
        
        # Renomear colunas para facilitar o uso (ajustar conforme colunas disponíveis)
        df = df.rename(columns={
            "NIS FAVORECIDO": "Nis",
            "NOME FAVORECIDO": "Nome",
            'CPF FAVORECIDO': 'Cpf',
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
            st.dataframe(df[['Nome', 'Nis', 'Cpf', 'Parcela_formatada']].rename(columns={'Parcela_formatada': 'Parcela'}), 
                         use_container_width=True, hide_index=True)
    else:
        st.error("Nenhum beneficiário encontrado para este município.")

# Interface principal
def show_pbf():
    st.write("---")
    st.write("### Buscar Beneficiários por Município")
    
    # Listar estados (UFs) a partir das pastas
    estados = sorted(listar_estados())
    if not estados:
        st.error("Nenhum estado encontrado no diretório de dados.")
        return
    
    estado_selecionado = st.selectbox("Escolha um estado:", estados)
    
    # Listar municípios para o estado selecionado
    municipios = listar_municipios_por_estado(estado_selecionado)
    if not municipios:
        st.error(f"Nenhum município encontrado para o estado {estado_selecionado}.")
        return
    
    municipio_selecionado = st.selectbox("Escolha um município:", municipios)
    
    if st.button("Buscar Beneficiários"):
        df_beneficiarios = carregar_beneficiarios_parquet(estado_selecionado, municipio_selecionado)
        exibir_beneficiarios(df_beneficiarios)

if __name__ == "__main__":
    show_pbf()