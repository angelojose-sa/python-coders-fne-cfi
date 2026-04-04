#!/usr/bin/env python3
"""
Script de teste para verificar a configuração da API CFI do BNDES.
Execute este script para testar se as credenciais estão funcionando.
"""

import os
import sys
from pathlib import Path

# Adiciona o diretório atual ao path para importar os módulos locais
sys.path.insert(0, str(Path(__file__).parent))

from cfi_api import (
    is_cfi_api_configured,
    get_cfi_config_errors,
    gerar_token_acesso,
    _load_legacy_credentials,
    _resolve_consumer_credentials,
    _has_oauth_credentials,
)

def test_config():
    print("=== Teste de Configuração da API CFI BNDES ===\n")

    # Verifica se está configurado
    configured = is_cfi_api_configured()
    print(f"API configurada: {configured}")

    if not configured:
        errors = get_cfi_config_errors()
        print("Variáveis faltantes:")
        for error in errors:
            print(f"  - {error}")
        print()
        return False

    # Mostra credenciais carregadas
    print("Credenciais encontradas:")
    consumer_key, consumer_secret = _resolve_consumer_credentials()
    if consumer_key:
        print(f"  - Consumer Key: {consumer_key[:10]}...")
    if consumer_secret:
        print(f"  - Consumer Secret: {consumer_secret[:10]}...")
    if os.getenv("BNDES_CFI_OAUTH_USERNAME"):
        print(f"  - Username: {os.getenv('BNDES_CFI_OAUTH_USERNAME')}")
    if os.getenv("BNDES_CFI_OAUTH_PASSWORD"):
        print("  - Password: configurado")
    if os.getenv("BNDES_CFI_API_TOKEN"):
        print("  - Token Bearer: configurado")
    if os.getenv("BNDES_CFI_API_KEY"):
        print("  - API Key: configurado")
    print()

    # Testa geração de token
    print("Testando geração de token...")
    token_result = gerar_token_acesso()
    if token_result.get("success"):
        print("✅ Token gerado com sucesso!")
        print(f"   Token: {token_result['access_token'][:20]}...")
        if "meta" in token_result:
            print(f"   Meta: {token_result['meta']}")
    else:
        print("❌ Falha ao gerar token:")
        print(f"   Erro: {token_result.get('error', 'desconhecido')}")
        if "status_code" in token_result:
            print(f"   Status Code: {token_result['status_code']}")
        if "raw" in token_result:
            print(f"   Resposta bruta: {token_result['raw']}")

    print("\n=== Fim do Teste ===")
    return token_result.get("success", False)

if __name__ == "__main__":
    success = test_config()
    sys.exit(0 if success else 1)