#!/usr/bin/env python3
"""Debug - Ver qual URL está sendo construída"""

import os

os.environ['BNDES_CFI_CONSUMER_KEY'] = 'dKA3jLkCZuuLBWP3yDQXbCXwj0Ua'
os.environ['BNDES_CFI_CONSUMER_SECRET'] = 'VpZxfWkVhAXfzXLgswrawk7Hylga'

from cfi_api import (
    BNDES_CFI_API_BASE_URL,
    BNDES_CFI_API_ENDPOINT,
    gerar_token_acesso,
    buscar_produto_cfi
)

print("Debug - Configuração de URLs:")
print("=" * 70)
print(f"BNDES_CFI_API_BASE_URL: {BNDES_CFI_API_BASE_URL}")
print(f"BNDES_CFI_API_ENDPOINT: {BNDES_CFI_API_ENDPOINT}")

url_final = f"{BNDES_CFI_API_BASE_URL}{BNDES_CFI_API_ENDPOINT}"
print(f"URL Final: {url_final}")
print("=" * 70)

# Testar token
print("\nGerando token...")
token_result = gerar_token_acesso()
print(f"Token: {token_result.get('success')}")

if token_result.get('success'):
    # Fazer requisição direta para debug
    import requests
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    token = token_result.get('access_token')
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json'
    }
    
    print(f"\nTestando URL: {url_final}")
    print("Com parâmetro: keyword=motor")
    
    r = requests.get(
        url_final,
        params={'keyword': 'motor', 'quantidade': '5'},
        headers=headers,
        timeout=15,
        verify=False
    )
    
    print(f"Status HTTP: {r.status_code}")
    print(f"Tipo de conteúdo: {r.headers.get('Content-Type', 'N/A')}")
    print(f"Resposta (primeiros 200 chars): {r.text[:200]}")
