import os
import streamlit as st
from scrapy.crawler import CrawlerProcess
from chamandoPonto import PontoSpiderComResultado
from dotenv import load_dotenv
import sys

def load_env():
    load_dotenv(override=True)
import subprocess

def run_spider_via_subprocess(user, senha,pep):
    os.environ["username"] = user
    os.environ["password"] = senha
    subprocess.run([sys.executable, r"chamandoPonto.py"], check=True)

# Streamlit UI
def main():
    st.title("Ponto Kairos - Gerador de Relatório")

    st.markdown("Informe suas credenciais do Kairos:")
    user = st.text_input("Usuario Kairos", type="default")
    senha = st.text_input("Senha Kairos", type="password")
    pep = st.text_input('Escreva seu pep, no modelo P.0 ou F.0',type="default")
    pep = pep.strip().upper()
    if len(pep)!=7:
        st.error(f"Erro ao gerar relatório, digite o PEP como no exemplo P.02073")
    if st.button("Gerar Relatório"):  # Ao clicar, executa
        if not user or not (senha , pep):
            st.error("Por favor, preencha username e senha.")
        else:
            with st.spinner("Executando spider e gerando relatório..."):
                try:
                    run_spider_via_subprocess(user, senha,pep)
                    st.success("Relatório gerado e enviado com sucesso!")
                except Exception as e:
                    st.error(f"Erro ao gerar relatório: {e}")

if __name__ == '__main__':
    main()