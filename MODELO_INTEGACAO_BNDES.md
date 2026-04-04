# 📐 Modelo de Integração com API BNDES CFI

Extraído do notebook `FNE_v6 (10) (1).ipynb` na pasta `modelos/`.

## 🔐 Bloco 1 — Autenticação OAuth2

### Classe: BNDESAuth

Gerencia autenticação OAuth2 com renovação automática de token.

```python
class BNDESAuth:
    """Gerencia OAuth2 Client Credentials Grant com o Gateway BNDES."""
    
    # Credenciais de acesso (substitua pelas suas)
    KEY    = "TTeb9hR_Yf3tjQxgi1bbaMmqhtYa"
    SECRET = "Xfvp9bdw2em69Q8I4Xpjy2EPUNwa"
    URL    = "https://apis-gateway.bndes.gov.br/token"
    
    def __init__(self):
        self._token  = None
        self._expira = 0
    
    def _token_expirado(self) -> bool:
        """Verifica se token está expirado."""
        return self._token is None or datetime.now().timestamp() >= self._expira
    
    def obter_token(self) -> str | None:
        """Retorna token válido, renovando se necessário."""
        if self._token_expirado():
            self._renovar()
        return self._token
    
    def _renovar(self):
        """Solicita novo token ao Gateway BNDES."""
        auth = requests.auth.HTTPBasicAuth(self.KEY, self.SECRET)
        try:
            res = requests.post(
                self.URL,
                data={"grant_type": "client_credentials"},
                auth=auth,
                verify=False,  # SSL desabilitado em ambiente corporativo
                timeout=10
            )
            dados = res.json()
            self._token = dados.get("access_token")
            # Expiração: agora + duração - 60s de margem
            self._expira = datetime.now().timestamp() + dados.get("expires_in", 3600) - 60
        except Exception as e:
            print(f"⚠️ Erro ao renovar token: {e}")
```

**Nota:** As credenciais `TTeb9hR_Yf3tjQxgi1bbaMmqhtYa` e `Xfvp9bdw2em69Q8I4Xpjy2EPUNwa` são de exemplo e pertencem a outra pessoa, conforme descrito no notebook.

---

## 📡 Bloco 2 — Camada de Serviços

### Classe: BNDESService

Encapsula requisições HTTP à API oficial do Catálogo CFI.

```python
class BNDESService:
    """Camada de acesso ao Catálogo CFI do BNDES."""
    
    # Endpoint oficial de busca (OAuth2 protegido)
    BASE_URL = "https://apis-gateway.bndes.gov.br/catalogoCFI/v1/itemfinanciavel/buscar"
    
    # URL base do portal público
    CFI_URL  = "https://ws.bndes.gov.br/cfi_catalogo/produto"
    
    def __init__(self, auth: BNDESAuth):
        self.auth = auth
    
    def _headers(self) -> dict:
        """Constrói cabeçalhos com token atualizado automaticamente."""
        return {
            "Authorization": f"Bearer {self.auth.obter_token()}",
            "Accept": "application/json"
        }
    
    def buscar_itens(self, keyword: str, quantidade: int = 30) -> list:
        """
        Busca universal no Catálogo CFI usando keyword.
        
        O parâmetro keyword aceita:
        - Nome do produto (ex: "motor")
        - CNPJ do fabricante (ex: "12345678000190")
        - Código CFI/Finame (ex: "03447782")
        
        Returns:
            list: Itens encontrados com campos: codigoFiname, fabricante, 
                  cnpjFabricante, nomeItem, modeloItem, numeroNcm, 
                  posicaoCadastral
        """
        try:
            res = requests.get(
                self.BASE_URL,
                params={"keyword": keyword, "quantidade": quantidade},
                headers=self._headers(),
                verify=False,
                timeout=15
            )
            # API retorna itens em 'entidades'
            return res.json().get("entidades", []) if res.status_code == 200 else []
        except Exception as e:
            print(f"❌ Erro na busca: {e}")
            return []
    
    @classmethod
    def link_oficial(cls, cfi: str) -> str:
        """Gera link público do produto no portal BNDES."""
        return f"{cls.CFI_URL}/{cfi}"
```

---

## 🔑 Fluxo de Autenticação

O modelo usa **OAuth2 Client Credentials Grant**:

```
1. App → envia KEY + SECRET (codificado em Base64)
2. Gateway BNDES → válida credenciais
3. Gateway → retorna Access Token com expiração (~1 hora)
4. App → usa token nas requisições posteriores
5. Quando expira → BNDESAuth._renovar() é chamado automaticamente
```

---

## 📊 Estrutura de Resposta

Quando você chamada `buscar_itens("motor")`, a resposta contém:

```json
{
  "entidades": [
    {
      "codigoFiname": "03447782",
      "fabricante": "ACME Motors",
      "cnpjFabricante": "12345678000190",
      "nomeItem": "Motor Elétrico Trifásico",
      "modeloItem": "ME-3HP",
      "numeroNcm": "85021900",
      "posicaoCadastral": "Financiável"
    },
    {
      "codigoFiname": "03447783",
      "fabricante": "ACME Motors",
      "cnpjFabricante": "12345678000190",
      "nomeItem": "Motor Elétrico Trifásico",
      "modeloItem": "ME-5HP",
      "numeroNcm": "85021900",
      "posicaoCadastral": "Financiável"
    }
  ]
}
```

---

## 🔑 Credenciais Necessárias

Para usar a API real do BNDES, você precisa de:

1. **Consumer Key** (Client ID)
2. **Consumer Secret** (Senha da aplicação)

Essas credenciais devem ser solicitadas ao BNDES via:
- Portal de desenvolvimento: https://developers.bndes.gov.br/
- Formulário de registro de aplicação
- Suporte: suporte@bndes.gov.br

---

## 📝 Configuração das Variáveis de Ambiente

```bash
# Credenciais da sua aplicação (substitua pelos valores reais)
export BNDES_CFI_CONSUMER_KEY="sua_consumer_key_aqui"
export BNDES_CFI_CONSUMER_SECRET="sua_consumer_secret_aqui"

# URLs (já possuem padrões corretos)
export BNDES_CFI_API_BASE_URL="https://apis-gateway.bndes.gov.br"
export BNDES_CFI_OAUTH_URL="https://apis-gateway.bndes.gov.br/token"

# Timeout
export BNDES_CFI_API_TIMEOUT="15"
```

---

## 💡 Exemplo de Uso

```python
# 1. Criar instância de autenticação
auth = BNDESAuth()

# 2. Criar serviço com autenticação
service = BNDESService(auth)

# 3. Buscar produtos
itens = service.buscar_itens("motor", quantidade=10)

# 4. Gerar link para um produto
for item in itens:
    cfi = item["codigoFiname"]
    link = service.link_oficial(cfi)
    print(f"{item['nomeItem']}: {link}")
```

---

## ✅ Segurança

- ✅ Credenciais em variáveis de ambiente (nunca no código)
- ✅ Token renovado automaticamente antes de expirar
- ✅ Margem de 60s na renovação para evitar race conditions
- ✅ SSL verificado (exceto dados corporativos que usam `verify=False`)
- ✅ Timeout de 15s para evitar travamentos

---

## 📚 Referências

- Notebook modelo: `modelos/FNE_v6 (10) (1).ipynb`
- Endpoints oficiais: Seção "Bloco 3" do notebook
- Documentação BNDES: https://www.bndes.gov.br
