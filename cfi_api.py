import base64
import os
from pathlib import Path
from urllib.parse import urljoin

import requests

ROOT = Path(__file__).resolve().parent
LEGACY_CREDENTIALS_PATH = ROOT / "credenciais_api_bdnes.env"

BNDES_CFI_API_BASE_URL = os.getenv("BNDES_CFI_API_BASE_URL", "https://apis-gateway.bndes.gov.br").strip().rstrip("/")
BNDES_CFI_API_ENDPOINT = os.getenv("BNDES_CFI_API_ENDPOINT", "/catalogoCFI/v1/itemfinanciavel/buscar").strip()
BNDES_CFI_API_KEY = os.getenv("BNDES_CFI_API_KEY", "").strip()
BNDES_CFI_API_TOKEN = os.getenv("BNDES_CFI_API_TOKEN", "").strip()
BNDES_CFI_API_TIMEOUT = int(os.getenv("BNDES_CFI_API_TIMEOUT", "15"))
BNDES_CFI_API_OAUTH_URL = os.getenv("BNDES_CFI_API_OAUTH_URL", "https://apis-gateway.bndes.gov.br/token").strip()
BNDES_CFI_CONSUMER_KEY = os.getenv("BNDES_CFI_CONSUMER_KEY", "").strip()
BNDES_CFI_CONSUMER_SECRET = os.getenv("BNDES_CFI_CONSUMER_SECRET", "").strip()
BNDES_CFI_OAUTH_USERNAME = os.getenv("BNDES_CFI_OAUTH_USERNAME", "").strip()
BNDES_CFI_OAUTH_PASSWORD = os.getenv("BNDES_CFI_OAUTH_PASSWORD", "").strip()


def _load_legacy_credentials() -> dict:
    credentials = {}
    if not LEGACY_CREDENTIALS_PATH.exists():
        return credentials

    with LEGACY_CREDENTIALS_PATH.open("r", encoding="utf-8") as f:
        lines = f.readlines()

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        i += 1

        if not line or line.startswith("#") or line.startswith("Códigos"):
            continue

        # Verifica se é uma linha de chave
        lower_line = line.lower()
        if "consumer key" in lower_line:
            # Próxima linha deve ter o valor
            if i < len(lines):
                value_line = lines[i].strip()
                if value_line and not value_line.startswith("Consumer"):
                    credentials["consumer_key"] = value_line
                    i += 1
        elif "consumer secret" in lower_line:
            # Próxima linha deve ter o valor
            if i < len(lines):
                value_line = lines[i].strip()
                if value_line and not value_line.startswith("Consumer"):
                    credentials["consumer_secret"] = value_line
                    i += 1
        elif lower_line in {"bndes_cfi_oauth_username", "username"}:
            # Próxima linha deve ter o valor
            if i < len(lines):
                value_line = lines[i].strip()
                if value_line:
                    credentials["oauth_username"] = value_line
                    i += 1
        elif lower_line in {"bndes_cfi_oauth_password", "password"}:
            # Próxima linha deve ter o valor
            if i < len(lines):
                value_line = lines[i].strip()
                if value_line:
                    credentials["oauth_password"] = value_line
                    i += 1

    return credentials


def _resolve_consumer_credentials() -> tuple[str, str]:
    consumer_key = BNDES_CFI_CONSUMER_KEY
    consumer_secret = BNDES_CFI_CONSUMER_SECRET
    if not consumer_key or not consumer_secret:
        legacy = _load_legacy_credentials()
        consumer_key = consumer_key or legacy.get("consumer_key", "")
        consumer_secret = consumer_secret or legacy.get("consumer_secret", "")
    return consumer_key, consumer_secret


def _has_oauth_credentials() -> bool:
    key, secret = _resolve_consumer_credentials()
    # Client Credentials Grant: apenas consumer key/secret
    if key and secret:
        return True
    # Password Grant: consumer key/secret + username/password
    return bool(key and secret and BNDES_CFI_OAUTH_USERNAME and BNDES_CFI_OAUTH_PASSWORD)


def get_cfi_config_errors() -> list[str]:
    errors = []
    if not BNDES_CFI_API_BASE_URL:
        errors.append("BNDES_CFI_API_BASE_URL")

    if not (BNDES_CFI_API_KEY or BNDES_CFI_API_TOKEN or _has_oauth_credentials()):
        errors.append(
            "BNDES_CFI_API_KEY or BNDES_CFI_API_TOKEN or BNDES_CFI_CONSUMER_KEY + BNDES_CFI_CONSUMER_SECRET (para Client Credentials Grant)"
        )

    return errors


def is_cfi_api_configured() -> bool:
    return len(get_cfi_config_errors()) == 0


def _build_headers() -> tuple[dict, dict]:
    headers = {
        "Accept": "application/json",
    }
    auth_meta = {}

    if BNDES_CFI_API_TOKEN:
        headers["Authorization"] = f"Bearer {BNDES_CFI_API_TOKEN}"
    elif BNDES_CFI_API_KEY:
        headers["x-api-key"] = BNDES_CFI_API_KEY
    else:
        token_response = gerar_token_acesso()
        if not token_response.get("success"):
            return headers, {"error": token_response.get("error", "Falha ao gerar token de acesso")}
        headers["Authorization"] = f"Bearer {token_response["access_token"]}"
        auth_meta = token_response.get("meta", {})

    return headers, auth_meta


def gerar_token_acesso() -> dict:
    if BNDES_CFI_API_TOKEN:
        return {"success": True, "access_token": BNDES_CFI_API_TOKEN}

    consumer_key, consumer_secret = _resolve_consumer_credentials()
    if not consumer_key or not consumer_secret:
        return {"success": False, "error": "Credenciais OAuth não configuradas para geração de token"}

    auth_header = base64.b64encode(f"{consumer_key}:{consumer_secret}".encode("utf-8")).decode("utf-8")
    headers = {
        "Authorization": f"Basic {auth_header}",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
    }

    # Determina o fluxo baseado nas credenciais disponíveis
    if BNDES_CFI_OAUTH_USERNAME and BNDES_CFI_OAUTH_PASSWORD:
        # Password Grant
        payload = {
            "grant_type": "password",
            "username": BNDES_CFI_OAUTH_USERNAME,
            "password": BNDES_CFI_OAUTH_PASSWORD,
        }
    else:
        # Client Credentials Grant
        payload = {
            "grant_type": "client_credentials",
        }

    try:
        response = requests.post(
            BNDES_CFI_API_OAUTH_URL,
            data=payload,
            headers=headers,
            timeout=BNDES_CFI_API_TIMEOUT,
            verify=True,
        )
        response.raise_for_status()
        data = response.json()
        if "access_token" not in data:
            return {"success": False, "error": "Resposta do token não contém access_token", "raw": data}
        return {"success": True, "access_token": data["access_token"], "meta": data}
    except requests.exceptions.RequestException as exc:
        return {"success": False, "error": str(exc), "status_code": getattr(exc.response, "status_code", None)}


def buscar_produto_cfi(
    ncm: str = None,
    cfi: str = None,
    nome: str = None,
    modelo: str = None,
    marca: str = None,
    cnpj: str = None,
):
    """
    Consulta o catálogo CFI do BNDES usando busca por keyword.
    
    Baseado no modelo FNE_v6, a API BNDES aceita um parâmetro 'keyword'
    que pode ser:
    - Nome do produto (ex: "motor")
    - CNPJ do fabricante (ex: "12345678000190")
    - Código CFI/Finame (ex: "03447782")
    
    Args:
        ncm, cfi, nome, modelo, marca, cnpj: Parâmetros de busca
        
    Returns:
        dict: {"success": bool, "data": [...], "error": str, ...}
    """
    if not BNDES_CFI_API_BASE_URL:
        return {"success": False, "error": "BNDES_CFI_API_BASE_URL não configurada"}

    # Construir keyword a partir dos parâmetros disponíveis
    # Prioridade: CFI > NCM > CNPJ > Nome
    keyword = None
    if cfi:
        keyword = cfi.strip()
    elif ncm:
        keyword = ncm.strip()
    elif cnpj:
        keyword = cnpj.strip()
    elif nome:
        keyword = nome.strip()
    else:
        return {"success": False, "error": "Informe ao menos um parâmetro: CFI, NCM, CNPJ ou Nome"}

    # Construir URL corretamente
    # URL base: https://apis-gateway.bndes.gov.br
    # Endpoint: /catalogoCFI/v1/itemfinanciavel/buscar
    url = f"{BNDES_CFI_API_BASE_URL}{BNDES_CFI_API_ENDPOINT}"

    headers, auth_meta = _build_headers()
    if "error" in auth_meta:
        return {"success": False, "error": auth_meta["error"], "status_code": auth_meta.get("status_code")}

    # Parâmetros da query (conforme modelo)
    params = {
        "keyword": keyword,
        "quantidade": 30  # Limite de resultados
    }

    try:
        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=BNDES_CFI_API_TIMEOUT,
            verify=False  # SSL pode ser problema em ambiente corporativo
        )
        
        if response.status_code == 200:
            data = response.json()
            # A API retorna os itens na chave 'entidades'
            itens = data.get("entidades", [])
            result = {
                "success": True,
                "data": itens,
                "quantidade": len(itens),
                "status_code": response.status_code,
                "keyword": keyword,
                "url": url
            }
            if auth_meta:
                result["auth_meta"] = auth_meta
            return result
        else:
            # Erro HTTP
            try:
                error_data = response.json()
                error_msg = error_data.get("mensagem", response.text)
            except:
                error_msg = response.text
            
            return {
                "success": False,
                "error": error_msg,
                "status_code": response.status_code,
                "url": url,
                "keyword": keyword
            }
            
    except requests.exceptions.RequestException as exc:
        return {
            "success": False,
            "error": str(exc),
            "status_code": getattr(exc.response, "status_code", None),
            "url": url,
            "keyword": keyword
        }
