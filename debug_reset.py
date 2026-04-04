#!/usr/bin/env python3
"""Debug - Limpar variables e testar"""

import os
import sys

# Limpar variáveis anteriores
for key in list(os.environ.keys()):
    if 'BNDES' in key or 'CFI' in key:
        del os.environ[key]

# Configurar as credenciais CORRETAS
os.environ['BNDES_CFI_CONSUMER_KEY'] = 'dKA3jLkCZuuLBWP3yDQXbCXwj0Ua'
os.environ['BNDES_CFI_CONSUMER_SECRET'] = 'VpZxfWkVhAXfzXLgswrawk7Hylga'
os.environ['BNDES_CFI_API_BASE_URL'] = 'https://apis-gateway.bndes.gov.br'
os.environ['BNDES_CFI_API_ENDPOINT'] = '/catalogoCFI/v1/itemfinanciavel/buscar'

# Remover o módulo do cache para forçar recarga
if 'cfi_api' in sys.modules:
    del sys.modules['cfi_api']

from cfi_api import (
    BNDES_CFI_API_BASE_URL,
    BNDES_CFI_API_ENDPOINT,
    gerar_token_acesso,
    buscar_produto_cfi
)

print("Debug - URLs após reset:")
print("=" * 70)
print(f"BNDES_CFI_API_BASE_URL: {BNDES_CFI_API_BASE_URL}")
print(f"BNDES_CFI_API_ENDPOINT: {BNDES_CFI_API_ENDPOINT}")
print("=" * 70)

# Testar token
print("\nGerando token...")
token_result = gerar_token_acesso()
print(f"Token sucesso: {token_result.get('success')}")

if token_result.get('success'):
    # Testar busca
    print("\nBuscando produtos por NCM 85423100...")
    resultado = buscar_produto_cfi(ncm='85423100')
    print(f"Sucesso: {resultado.get('success')}")
    print(f"Quantidade: {resultado.get('quantidade', 0)}")
    
    if resultado.get('data'):
        print(f"\n✅ Primeiros 2 produtos encontrados:")
        for i, item in enumerate(resultado.get('data', [])[:2], 1):
            print(f"   {i}. {item.get('nomeItem', 'N/A')}")
    elif resultado.get('error'):
        print(f"Erro: {resultado.get('error')[:100]}")
