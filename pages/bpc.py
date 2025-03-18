import streamlit as st
import pandas as pd
from pathlib import Path


# Função para listar os estados (pastas) no diretório
def listar_estados(diretorio_base):
    """Retorna uma lista de estados (pastas) no diretório especificado."""
    caminho = Path(diretorio_base)
    if not caminho.exists():
        st.error(f"Diretório {diretorio_base} não encontrado.")
        return []
    estados = [pasta.name for pasta in caminho.iterdir() if pasta.is_dir()]
    return sorted(estados)

# Função para listar os municípios (arquivos Parquet) em um estado
def listar_municipios(diretorio_estado):
    """Retorna uma lista de municípios (arquivos Parquet) no diretório do estado."""
    caminho = Path(diretorio_estado)
    if not caminho.exists():
        st.error(f"Diretório {diretorio_estado} não encontrado.")
        return []
    municipios = [arquivo.stem for arquivo in caminho.glob("*.parquet")]
    return sorted(municipios)


# Função para calcular menores de 16 anos a partir do CSV original
def calcular_menores_16_parquet(df):
    """
    Calcula a quantidade de titulares menores de 16 anos no DataFrame do Parquet.
    No CSV original, menores têm 'NOME BENEFICIÁRIO' como '*** TITULAR MENOR DE 16 ANOS ***'.
    No Parquet, esse valor foi substituído por 'responsavel', então contamos onde 'nome' = 'responsavel'.
    """
    menores_16 = len(df[df['nome'] == "*** TITULAR MENOR DE 16 ANOS ***"])
    total_beneficiarios = len(df)
    return menores_16, total_beneficiarios




# Função para carregar o arquivo Parquet de um município
def carregar_dados_parquet(caminho_parquet):
    """Carrega e retorna os dados de um arquivo Parquet."""
    try:
        df = pd.read_parquet(caminho_parquet)
        return df
    except Exception as e:
        st.error(f"Erro ao carregar o arquivo {caminho_parquet}: {e}")
        return None

def show_bpc():
    st.title("BPC POR ESTADO E MUUNICIPIO")

    # Diretório base onde estão os arquivos Parquet
    diretorio_base = "./dados/dados_por_municipio/"

    # Listar estados disponíveis
    estados = listar_estados(diretorio_base)
    if not estados:
        st.warning("Nenhum estado encontrado no diretório especificado.")
        return

    # Dropdown para selecionar o estado
    estado_selecionado = st.selectbox("Selecione o Estado (UF):", ["Selecione"] + estados)

    if estado_selecionado != "Selecione":
        # Diretório do estado selecionado
        diretorio_estado = Path(diretorio_base) / estado_selecionado

        # Listar municípios disponíveis no estado
        municipios = listar_municipios(diretorio_estado)
        if not municipios:
            st.warning(f"Nenhum município encontrado para o estado {estado_selecionado}.")
            return

        # Dropdown para selecionar o município
        municipio_selecionado = st.selectbox("Selecione o Município:", ["Selecione"] + municipios)

        if municipio_selecionado != "Selecione":
            # Caminho do arquivo Parquet correspondente
            caminho_parquet = diretorio_estado / f"{municipio_selecionado}.parquet"

            # Carregar os dados do Parquet
            df = carregar_dados_parquet(caminho_parquet)
            if df is not None:
                # Exibir os dados em uma tabela interativa
                st.write(f"Dados para {estado_selecionado}/{municipio_selecionado}:")
                st.dataframe(df, use_container_width=True, hide_index=True)

                col1, col2 = st.columns(2)
                
                with col1:
                    # Calcular menores de 16 anos a partir do Parquet
                    menores_16, total_beneficiarios = calcular_menores_16_parquet(df)
                    outros = total_beneficiarios - menores_16
                    
                    # Criar um DataFrame para o gráfico
                    dados_grafico = pd.DataFrame({
                        "Categoria": ["Menores de 16 anos", "Outros"],
                        "Quantidade": [menores_16, outros]
                    })
                    
                    # Exibir o gráfico de barras
                    st.bar_chart(dados_grafico.set_index("Categoria")["Quantidade"])
                
                with col2:
                    # Exibir estatísticas
                    st.write(f"**Total de beneficiários:** {total_beneficiarios}")
                    st.write(f"**Valor total das parcelas:** R$ {df['valor'].sum():,.2f}")
                    st.write(f"**Titulares menores de 16 anos:** {menores_16}")
                    st.write(f"**Outros beneficiários:** {outros}")

                

if __name__ == "__main__":
    show_bpc()