import requests
import msal
import os
from ponto.spiders import ponto
from dotenv import load_dotenv
import subprocess
load_dotenv(override=True)
from scrapy.crawler import CrawlerProcess
from ponto.spiders.ponto import PontoSpider
from pandas import json_normalize
import json
import pandas as pd
import io
import pyarrow.parquet as pq

resultados = []

class PontoSpiderComResultado(PontoSpider):
    def salvar_relatorio(self, response):
        

        data = json.loads(response.text)

        self.logger.info(f"HTML do relatório recebido (dentro de JSON)")
        df = json_normalize(
                data,
                record_path='Entradas',
                meta=['InfoEmpresa', 'InfoFuncionario']
            )
        # Expandir 'InfoEmpresa'
        empresa_df = pd.json_normalize(df['InfoEmpresa'])
        empresa_df.columns = [f'Empresa_{col}' for col in empresa_df.columns]

        # Expandir 'InfoFuncionario'
        funcionario_df = pd.json_normalize(df['InfoFuncionario'])
        funcionario_df.columns = [f'Funcionario_{col}' for col in funcionario_df.columns]

        # Concatenar os DataFrames
        df_final = pd.concat([df.drop(['InfoEmpresa', 'InfoFuncionario'], axis=1), empresa_df, funcionario_df], axis=1)

        # Salvar o DataFrame em um arquivo CSV
        CLIENT_ID = os.getenv("CLIENT_ID")
        CLIENT_SECRET = os.getenv("CLIENT_SECRET")
        TENANT_ID = os.getenv("TENANT_ID")
        SITE_URL = os.getenv("SITE_URL")

        # 🔹 Configurações do Microsoft Graph
        AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
        GRAPH_API = os.getenv("GRAPH_API")
        SITE_PATH = os.getenv("SITE_PATH")

        self.logger.debug(f"Tipo de data: {df_final.head()}")
        # # 🔹 Autenticação no Microsoft Graph
        app = msal.ConfidentialClientApplication(CLIENT_ID, authority=AUTHORITY, client_credential=CLIENT_SECRET)
        token_response = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])

        if "access_token" not in token_response:
            print("❌ Erro ao obter token:", token_response.get("error_description", "Desconhecido"))
            exit()

        access_token = token_response["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}

        # 🔹 Obtém o ID do site SharePoint
        site_response = requests.get(f"{GRAPH_API}/sites/{SITE_URL}:{SITE_PATH}", headers=headers)

        if site_response.status_code != 200:
            print("❌ Erro ao obter ID do site:", site_response.text)
            exit()

        site_id = site_response.json()["id"]

        # 🔹 Obtém o ID da Biblioteca "Documentos"
        drive_list_response = requests.get(
            f"{GRAPH_API}/sites/{site_id}/drives",
            headers=headers
        )

        if drive_list_response.status_code == 200:
            drives = drive_list_response.json().get("value", [])
            for drive in drives:
                if drive["name"].lower() == "documentos":
                    drive_id = drive["id"]
                    print(f"📂 Biblioteca 'Documentos' encontrada | ID: {drive_id}")
        else:
            print("❌ Erro ao listar drives:", drive_list_response.text)
            exit()

        # 🔹 Listar pastas dentro de "Documentos"
        folders_response = requests.get(
            f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root/children",
            headers=headers
        )

        if folders_response.status_code == 200:
            folders = folders_response.json().get("value", [])
            print("\n📂 Pastas dentro de 'Documentos':")
            for folder in folders:
                if folder["folder"]:  # Verifica se é uma pasta
                    print(f"📂 Nome: {folder['name']} | ID: {folder['id']}")
        else:
            print("❌ Erro ao listar pastas:", folders_response.text)

        # 🔹 ID da pasta "General"
        general_folder_id = os.getenv("general")

        # 🔹 Listar pastas e arquivos dentro de "General"
        general_contents_response = requests.get(
            f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{general_folder_id}/children",
            headers=headers
        )

        if general_contents_response.status_code == 200:
            general_contents = general_contents_response.json().get("value", [])
            print("\n📂 Itens dentro da pasta 'General':")
            for item in general_contents:
                item_type = "📂 Pasta" if "folder" in item else "📄 Arquivo"
                print(f"{item_type}: {item['name']} | ID: {item['id']}")
        else:
            print("❌ Erro ao listar itens em 'General':", general_contents_response.text)

        # 🔹 Nome do arquivo que será salvo
        file_name = "Ponto.parquet"

        # 🔹 Converte o DataFrame para um arquivo Excel em memória
        output = io.BytesIO()
        df_final.fillna("").to_parquet(output, index=False, engine='pyarrow')
        output.seek(0)  # Retorna ao início do arquivo em memória

        # 🔹 ID da pasta onde o arquivo será salvo
        folder_id = os.getenv("folder_id")

        # 🔹 Enviar o arquivo para o SharePoint
        upload_url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{folder_id}:/{file_name}:/content"
        upload_headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        }

        response = requests.put(upload_url, headers=upload_headers, data=output.getvalue())

        if response.status_code in [200, 201]:
            print(f"✅ Arquivo '{file_name}' enviado com sucesso para a pasta SharePoint!")
        else:
            print(f"❌ Erro ao enviar o arquivo: {response.text}")

process = CrawlerProcess()
process.crawl(PontoSpiderComResultado)
process.start()


# def rodar_spider():
#     subprocess.run(["scrapy", "crawl", "ponto"], check=True)

# rodar_spider()

# 🔹 Configurações de Autenticação




# print(f"Arquivo '{file_name}' enviado com sucesso para a pasta SharePoint '{folder_id}'.")

    