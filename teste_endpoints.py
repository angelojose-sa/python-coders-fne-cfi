#!/usr/bin/env python3
"""Testar diferentes variações de endpoints"""

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from cfi_api import gerar_token_acesso, _resolve_consumer_credentials

# Verificar credenciais carregadas
key, secret = _resolve_consumer_credentials()
print(f"Consumer Key configurado: {'Sim' if key else 'Nao'}")
print(f"Consumer Secret configurado: {'Sim' if secret else 'Nao'}")

# Testar geração de token
print("\nGerando token...")
token_result = gerar_token_acesso()
print(f"Token gerado: {token_result.get('success')}")

if token_result.get('success'):
    token = token_result.get('access_token')
    print(f"Token recebido: {len(token)} caracteres")
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json'
    }
    
    # Diferentes variações de endpoints
    endpoints = [
        'https://apis-gateway.bndes.gov.br/catalogoCFI/v1/itemfinanciavel/buscar',
        'https://apis-gateway.bndes.gov.br/catalogoCFI/itemfinanciavel/buscar',
        'https://apis-gateway.bndes.gov.br/catalogoCFI/v1/buscar',
        'https://apis-gateway.bndes.gov.br/cfi-catalogo/api/v1/buscar',
        'https://apis-gateway.bndes.gov.br/v1/cfi/buscar',
    ]
    
    print("\n" + "="*70)
    print("Testando endpoints com keyword='motor':")
    print("="*70)
    
    for endpoint in endpoints:
        try:
            r = requests.get(
                endpoint,
                params={'keyword': 'motor', 'quantidade': '5'},
                headers=headers,
                timeout=10,
                verify=False
            )
            print(f"\n{endpoint.split('//')[-1]}")
            print(f"  Status: {r.status_code}")
            if r.status_code == 200:
                print(f"  ✅ SUCESSO!")
                data = r.json()
                print(f"  Resposta: {str(data)[:200]}...")
                break
            elif r.status_code == 404:
                print(f"  ❌ 404 - Endpoint não existe")
            else:
                print(f"  ⚠️ Erro: {r.status_code}")
                
        except Exception as e:
            print(f"\n{endpoint.split('//')[-1]}")
            print(f"  ❌ Erro de conexão: {str(e)[:50]}")
else:
    print(f"Erro ao gerar token: {token_result.get('error')}")
