# Ponto Kairos Scraper

Este projeto utiliza **Scrapy** para automatizar a raspagem de dados de ponto no sistema DIMEP Kairos e, em seguida, processar e exportar o relatório para um arquivo Parquet no SharePoint via Microsoft Graph API.

---

## 📋 Objetivo

- Fazer autenticação no portal DIMEP Kairos  
- Gerar relatório de ponto do colaborador para os últimos 60 dias  
- Normalizar e enriquecer o JSON retornado  
- Salvar o resultado em um arquivo Parquet  
- Fazer upload automático desse arquivo para uma biblioteca “Documentos” no SharePoint

---

## 🔧 Configurações

1. **Variáveis de ambiente** (usar `.env`):
   ```text
   username=<SEU_USUÁRIO_KAIROS>
   password=<SUA_SENHA_KAIROS>
   CLIENT_ID=<ID_DO_APP_MSAL>
   CLIENT_SECRET=<SEGREDO_DO_APP_MSAL>
   TENANT_ID=<TENANT_AZURE_AD>
   GRAPH_API=https://graph.microsoft.com/v1.0
   SITE_URL=<SEU_SITE_SHAREPOINT>
   SITE_PATH=<CAMINHO_DO_SITE_SHAREPOINT>
   general=<ID_PASTA_GENERAL>
   folder_id=<ID_PASTA_DESTINO_PARQUET>
