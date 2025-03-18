import streamlit as st
import json
import os
from pathlib import Path
import requests
from datetime import datetime
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv

load_dotenv()




caminho_arquivo = os.path.join(Path(__file__).parent.parent, 'dados', 'municipios.json')
base_url = "https://api.portaldatransparencia.gov.br"

api_key = os.getenv("API_KEY")

print(api_key)


def carregar_municipios():
    with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
        municipios = json.load(arquivo)
    return municipios['data']

def filtrar_municipios_por_estado(municipios, estado):
    return [m for m in municipios if m['Uf'] == estado]

def get_codigo_municipio(nome_municipio, municipios):
    for municipio in municipios:
        if municipio['Nome'].lower() == nome_municipio.lower():
            return municipio['Codigo']
    return None

def consulta_api(endpoint, params=None):
    url = f"{base_url}{endpoint}"
    headers = {
        "accept": "/",
        "chave-api-dados": api_key
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        try:
            return response.json()
        except ValueError:
            st.error("Erro ao decodificar a resposta em JSON.")
            st.text(response.text)
            return None
    else:
        st.error(f"Falha ao acessar a API. Status code: {response.status_code}")
        st.text(response.text)
        return None

def get_datas_consulta():
    data_atual = datetime.now()
    data_mes_passado = data_atual - relativedelta(months=1)
    data_dois_meses_atras = data_atual - relativedelta(months=2)
    data_tres_meses_atras = data_atual - relativedelta(months=3)

    mes_ano_passado = data_mes_passado.strftime("%Y%m")
    mes_ano_dois_meses_atras = data_dois_meses_atras.strftime("%Y%m")
    mes_ano_tres_meses_atras = data_tres_meses_atras.strftime("%Y%m")

    return mes_ano_passado, mes_ano_dois_meses_atras, mes_ano_tres_meses_atras

def consultar_dados_bolsa_familia(codigo):
    mes_ano_passado, mes_ano_dois_meses_atras, mes_ano_tres_meses_atras = get_datas_consulta()
    tentativas = [mes_ano_passado, mes_ano_dois_meses_atras, mes_ano_tres_meses_atras]

    for mes_ano in tentativas:
        endpoint = f'/api-de-dados/novo-bolsa-familia-por-municipio?mesAno={mes_ano}&codigoIbge={codigo}&pagina=1'
        dados = consulta_api(endpoint)
        if dados and isinstance(dados, list) and len(dados) > 0:
            return dados, mes_ano
    return None, None

def consultar_dados_bpc_municipio(codigo):
    mes_ano_passado, mes_ano_dois_meses_atras, mes_ano_tres_meses_atras = get_datas_consulta()
    tentativas = [mes_ano_passado, mes_ano_dois_meses_atras, mes_ano_tres_meses_atras]

    for mes_ano in tentativas:
        endpoint = f'/api-de-dados/bpc-por-municipio?mesAno={mes_ano}&codigoIbge={codigo}&pagina=1'
        dados = consulta_api(endpoint)
        if dados and isinstance(dados, list) and len(dados) > 0:
            return dados, mes_ano
    return None, None

def exibir_dados_bolsa_familia(dados, mes_ano_usado):
    dados_municipio = dados[0]
    valor_total = dados_municipio.get("valor", 0)
    qtd_beneficiados = dados_municipio.get("quantidadeBeneficiados", 0)
    nome_municipio = dados_municipio["municipio"].get("nomeIBGE", "N/A")
    uf = dados_municipio["municipio"]["uf"].get("sigla", "N/A")
    valor_medio = valor_total / qtd_beneficiados if qtd_beneficiados > 0 else 0

    st.subheader(f"BOLSA FAMÍLIA - {nome_municipio} ({uf})")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Quantidade de Beneficiários", f"{qtd_beneficiados:,}")
    col2.metric("Valor Total (R$)", f"{valor_total:,.2f}")
    col3.metric("Valor Médio por Beneficiado (R$)", f"{valor_medio:,.2f}")
    
    st.write(f"Referência: {mes_ano_usado[:4]}-{mes_ano_usado[4:]}")

def exibir_dados_bpc(dados, mes_ano_usado):
    dados_municipio = dados[0]
    valor_total = dados_municipio.get("valor", 0)
    qtd_beneficiados = dados_municipio.get("quantidadeBeneficiados", 0)
    nome_municipio = dados_municipio["municipio"].get("nomeIBGE", "N/A")
    uf = dados_municipio["municipio"]["uf"].get("sigla", "N/A")
    valor_medio = valor_total / qtd_beneficiados if qtd_beneficiados > 0 else 0

    st.subheader(f"BPC - {nome_municipio} ({uf})")
    
    col1, col2 = st.columns(2)
    col1.metric("Quantidade de Beneficiários maiores de 16 anos", f"{qtd_beneficiados:,}")
    col2.metric("Valor Total (R$)", f"{valor_total:,.2f}")
    
    st.write(f"Referência: {mes_ano_usado[:4]}-{mes_ano_usado[4:]}")

def show_home():
    # Definindo município padrão (Fátima, BA - código IBGE: 2910750)
    municipio_padrao = "Fátima"
    codigo_padrao = "2910750"

    # Exibir dados do Bolsa Família
    dados_bolsa, mes_ano_bolsa = consultar_dados_bolsa_familia(codigo_padrao)
    if dados_bolsa:
        exibir_dados_bolsa_familia(dados_bolsa, mes_ano_bolsa)
    else:
        st.error(f"Nenhum dado do Bolsa Família encontrado para {municipio_padrao} nos últimos 3 meses.")

    # Exibir dados do BPC
    dados_bpc, mes_ano_bpc = consultar_dados_bpc_municipio(codigo_padrao)
    if dados_bpc:
        exibir_dados_bpc(dados_bpc, mes_ano_bpc)
    else:
        st.error(f"Nenhum dado do BPC encontrado para {municipio_padrao} nos últimos 3 meses.")

if __name__ == "__main__":
    show_home()