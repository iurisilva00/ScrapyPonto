import scrapy

from dotenv import load_dotenv

import os

import json

from scrapy import Selector

import pandas as pd

from pandas import json_normalize

import re

import datetime

import requests

import msal

from datetime import datetime, timedelta

load_dotenv(override=True)


class PontoSpider(scrapy.Spider):



    name = "ponto"

    allowed_domains = ["dimepkairos.com.br"]

    start_urls = ["https://www.dimepkairos.com.br/Dimep/Account/LogOn?ReturnUrl=%2F"]

    custom_settings = {

        'DOWNLOAD_TIMEOUT': 600,  # 10 minutos

        'RETRY_TIMES': 10,

        'LOG_LEVEL': 'DEBUG',

    }
    def __init__(self, user, senha, **kwargs):
        super().__init__(**kwargs)
        self.user = os.getenv("username")
        self.senha = os.getenv("password")

        self.data_fim = (datetime.now() - timedelta(days=1)).strftime('%d/%m/%Y')
        self.data_inicio = (datetime.now() - timedelta(days=61)).strftime('%d/%m/%Y')



    def parse(self, response):

        return scrapy.FormRequest.from_response(

            response,

            formdata={

                'LogOnModel.UserName': self.user,

                'LogOnModel.Password': self.senha

            },

            callback=self.after_login

        )



    def after_login(self, response):

        if "usuário ou senha inválidos" in response.text.lower():

            self.logger.error("Login falhou.")

            return



        self.logger.info("Login bem-sucedido, já estamos na página de ponto.")



        # Já processa direto aqui!

        return self.parse_ponto(response)





    # def parse_ponto(self, response):

    #     self.logger.info("Salvando HTML da página de ponto")

    #     yield {

    #         "pagina_html": response.xpath('//*[@id="Tab8"]').get()

    #     }



    def parse_ponto(self, response):

        self.logger.info("Na página de ponto, agora indo para Relatórios")



        yield scrapy.Request(

            url='https://www.dimepkairos.com.br/Dimep/Relatorios/PontoFuncionario',

            callback=self.parse_relatorio

        )



    def parse_relatorio(self, response):

        # self.logger.info("Página de relatório acessada. Iniciando requisição de progresso.")



        # yield scrapy.Request(

        #     url='https://www.dimepkairos.com.br/Dimep/Relatorios/GetProgressRelatorio',

        #     method='POST',

        #     headers={

        #         'Content-Type': 'application/json; charset=UTF-8',

        #         'X-Requested-With': 'XMLHttpRequest'

        #     },

        #     body=json.dumps({"idRelatorio": "142", "zerarProgressao": True}),

        #     callback=self.gerar_relatorio,

           

        # )

        self.logger.info(f"Página de relatório acessada. Capturando IDs...")



        # Captura o valor do input AllIds

        all_ids = response.xpath('//*[@id="AllIds"]/@value').get()



        if not all_ids:

            self.logger.error("Não foi possível encontrar o campo AllIds na página.")

            return



       



        # Agora continue normalmente com a requisição POST

        yield scrapy.Request(

            url='https://www.dimepkairos.com.br/Dimep/Relatorios/GetProgressRelatorio',

            method='POST',

            headers={

                'Content-Type': 'application/json; charset=UTF-8',

                'X-Requested-With': 'XMLHttpRequest'

            },

            body=json.dumps({"idRelatorio": "142", "zerarProgressao": True}),

            callback=self.gerar_relatorio,

            cb_kwargs={'id_pessoas': all_ids}

        )

           



    def gerar_relatorio(self, response,id_pessoas):

        self.logger.info("Etapa 1: Progresso reiniciado. Gerando relatório...")

        self.logger.info(f"IDs capturados: {id_pessoas}")

        body = {

            "idRelatorio": "142",

            "json": json.dumps({

                "DataInicio": self.data_inicio,

                "DataFim": self.data_fim,


                "idPessoas": id_pessoas,

                "IdPeriodo": "0",

                "AgruparPorPessoas": False,

                "Ordenacao": "MTDT",

                "RelCentesimal": False

            })

        }



        yield scrapy.Request(

            url='https://www.dimepkairos.com.br/Dimep/Relatorios/GerarRelatorio',

            method='POST',

            headers={

                'Content-Type': 'application/json; charset=UTF-8',

                'X-Requested-With': 'XMLHttpRequest'

            },

            body=json.dumps(body),

            callback=self.retornar_relatorio

        )

   

    def retornar_relatorio(self, response):

        self.logger.info("Etapa 2: Relatório gerado. Recuperando HTML...: ")



        yield scrapy.Request(

            url='https://www.dimepkairos.com.br/Dimep/Relatorios/RetornarRelatorio',

            method='POST',

            headers={

                'Content-Type': 'application/json; charset=UTF-8',

                'X-Requested-With': 'XMLHttpRequest'

            },

            body=json.dumps({"idRelatorio": "142"}),

            callback=self.salvar_relatorio

        )



    def salvar_relatorio(self, response):
        self.logger.info("⚠️ Método salvar_relatorio não implementado na classe base.")
        pass  # Só define pra não dar erro




    #     data = json.loads(response.text)

       

    #     df = json_normalize(

    #             data,

    #             record_path='Entradas',

    #             meta=['InfoEmpresa', 'InfoFuncionario']

    #         )

    #     # Expandir 'InfoEmpresa'

    #     empresa_df = pd.json_normalize(df['InfoEmpresa'])

    #     empresa_df.columns = [f'Empresa_{col}' for col in empresa_df.columns]



    #     # Expandir 'InfoFuncionario'

    #     funcionario_df = pd.json_normalize(df['InfoFuncionario'])

    #     funcionario_df.columns = [f'Funcionario_{col}' for col in funcionario_df.columns]



    #     # Concatenar os DataFrames

    #     df_final = pd.concat([df.drop(['InfoEmpresa', 'InfoFuncionario'], axis=1), empresa_df, funcionario_df], axis=1)



    #     # Salvar o DataFrame em um arquivo CSV





    #     self.logger.info("Relatório salvo como 'relatorio.csv'")



    #     self.logger.debug(f"Tipo de data: {df_final.head()}")

