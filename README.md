# Análise de Financiabilidade FNE

Este projeto avalia se um bem é financiável pelo FNE usando a lista de NCMs passíveis de credenciamento no CFI e consulta opcional à API do BNDES.

## Como rodar

### Opção 1: Script automático (recomendado)
Execute o arquivo `iniciar_app.bat` - ele configura tudo automaticamente.

### Opção 2: Terminal manual
1. Abra o PowerShell em:
   `c:\Users\angel\OneDrive\Documentos\FINANCIA FNE\VERSÃO 2.0`
2. Instale dependências:
   `python -m pip install -r requirements.txt`
3. Configure a variável de ambiente:
   `$env:BNDES_CFI_API_BASE_URL = "https://ws.bndes.gov.br/cfi_catalogo/"`
4. Teste a configuração (opcional):
   `python test_cfi_config.py`
5. Execute o app:
   `python -m streamlit run app.py --server.port 8505`
6. Abra o navegador em:
   `http://localhost:8505`

### Opção 3: Comando único
```powershell
cd "c:\Users\angel\OneDrive\Documentos\FINANCIA FNE\VERSÃO 2.0" ; $env:BNDES_CFI_API_BASE_URL = "https://ws.bndes.gov.br/cfi_catalogo/" ; python -m streamlit run app.py --server.port 8505
```

## Configuração da API CFI do BNDES

Para ativar a integração real com a API CFI, defina as variáveis de ambiente abaixo:

- `BNDES_CFI_API_BASE_URL` - URL base da API do BNDES (por exemplo, `https://apis-gateway.bndes.gov.br`).
- `BNDES_CFI_API_ENDPOINT` - endpoint de consulta (por padrão `/produtos`).
- `BNDES_CFI_API_KEY` - chave de API, se exigida pela API.
- `BNDES_CFI_API_TOKEN` - token Bearer direto, se já estiver disponível.
- `BNDES_CFI_API_OAUTH_URL` - URL do token OAuth (por padrão `https://apis-gateway.bndes.gov.br/token`).
- `BNDES_CFI_CONSUMER_KEY` - consumer key do BNDES.
- `BNDES_CFI_CONSUMER_SECRET` - consumer secret do BNDES.
- `BNDES_CFI_OAUTH_USERNAME` - usuário para gerar token via password grant (opcional).
- `BNDES_CFI_OAUTH_PASSWORD` - senha para gerar token via password grant (opcional).
- `BNDES_CFI_API_TIMEOUT` - tempo limite em segundos (padrão `10`).

O código também carrega automaticamente as credenciais `Consumer key` e `Consumer secret` do arquivo local `credenciais_api_bdnes.env` se essas variáveis não estiverem definidas.

### Exemplo usando `BNDES_CFI_API_TOKEN`

```powershell
$env:BNDES_CFI_API_BASE_URL = "https://apis-gateway.bndes.gov.br"
$env:BNDES_CFI_API_TOKEN = "SEU_TOKEN_BEARER"
python -m streamlit run app.py
```

### Exemplo usando Client Credentials Grant (apenas consumer key/secret)

```powershell
$env:BNDES_CFI_API_BASE_URL = "https://apis-gateway.bndes.gov.br"
$env:BNDES_CFI_CONSUMER_KEY = "dKA3jLkCZuuLBWP3yDQXbCXwj0Ua"
$env:BNDES_CFI_CONSUMER_SECRET = "VpZxfWkVhAXfzXLgswrawk7Hylga"
python -m streamlit run app.py
```

### Exemplo usando Password Grant (consumer key/secret + username/password)

```powershell
$env:BNDES_CFI_API_BASE_URL = "https://apis-gateway.bndes.gov.br"
$env:BNDES_CFI_CONSUMER_KEY = "dKA3jLkCZuuLBWP3yDQXbCXwj0Ua"
$env:BNDES_CFI_CONSUMER_SECRET = "VpZxfWkVhAXfzXLgswrawk7Hylga"
$env:BNDES_CFI_OAUTH_USERNAME = "Username"
$env:BNDES_CFI_OAUTH_PASSWORD = "Password"
python -m streamlit run app.py
```

## Campos de consulta no app

- NCM
- CFI
- CST
- Nome do Bem
- Marca
- Modelo
- CNPJ do fabricante

A integração com o CFI busca o produto no catálogo do BNDES quando a API está configurada.

## Próximos Passos para Integração CFI

Para completar a integração com a API CFI:

1. **Documentação da API**: Obter documentação oficial da API BNDES CFI
2. **Credenciais específicas**: Verificar se são necessárias credenciais especiais além do OAuth básico
3. **Parâmetros de consulta**: Identificar o formato correto dos parâmetros de busca
4. **Testes**: Validar consultas reais contra a API

Se você tiver acesso à documentação da API BNDES CFI, entre em contato para implementar a integração completa.
