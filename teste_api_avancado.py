#!/usr/bin/env python3
"""
Script avançado para testar parâmetros da API CFI BNDES
"""
import json
import os
import sys
from urllib.parse import urljoin

import requests

# Adicionar diretório raiz ao path para importar cfi_api
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

from cfi_api import (
    BNDES_CFI_API_BASE_URL,
    BNDES_CFI_API_ENDPOINT,
    BNDES_CFI_API_TIMEOUT,
    _build_headers,
    _load_legacy_credentials,
    gerar_token_acesso,
)


def testar_endpoint_variacoes():
    """Testa diferentes variações do endpoint"""
    print("=== TESTANDO VARIAÇÕES DO ENDPOINT ===")

    base_urls = [
        "https://ws.bndes.gov.br/cfi_catalogo/",
        "https://ws.bndes.gov.br/cfi_catalogo",
        "https://ws.bndes.gov.br/cfi-catalogo/",
        "https://ws.bndes.gov.br/cfi-catalogo",
    ]

    endpoints = [
        "buscar",
        "/buscar",
        "buscar/",
        "/buscar/",
        "search",
        "/search",
        "search/",
        "/search/",
        "consulta",
        "/consulta",
        "consulta/",
        "/consulta/",
    ]

    headers, auth_meta = _build_headers()
    if "error" in auth_meta:
        print(f"Erro na autenticação: {auth_meta['error']}")
        return

    for base in base_urls:
        for endpoint in endpoints:
            url = urljoin(base + "/", endpoint.lstrip("/"))
            print(f"\nTestando: {url}")

            try:
                # Teste GET sem parâmetros
                response = requests.get(url, headers=headers, timeout=BNDES_CFI_API_TIMEOUT)
                print(f"  Status: {response.status_code}")
                if response.status_code == 200:
                    print("  ✅ Endpoint encontrado!")
                    try:
                        data = response.json()
                        print(f"  Resposta: {json.dumps(data, indent=2)[:500]}...")
                    except:
                        print(f"  Resposta (texto): {response.text[:500]}...")
                    return url  # Retorna o primeiro endpoint que funciona
                elif response.status_code == 400:
                    print("  ⚠️  400 Bad Request - endpoint existe mas parâmetros incorretos")
                elif response.status_code == 401:
                    print("  ❌ 401 Unauthorized - problema de autenticação")
                elif response.status_code == 403:
                    print("  ❌ 403 Forbidden - acesso negado")
                elif response.status_code == 404:
                    print("  ❌ 404 Not Found - endpoint não existe")
                else:
                    print(f"  ❌ Status inesperado: {response.status_code}")

            except Exception as e:
                print(f"  ❌ Erro: {e}")

    return None


def testar_parametros_get(endpoint_url):
    """Testa diferentes combinações de parâmetros GET"""
    print(f"\n=== TESTANDO PARÂMETROS GET: {endpoint_url} ===")

    headers, auth_meta = _build_headers()
    if "error" in auth_meta:
        print(f"Erro na autenticação: {auth_meta['error']}")
        return

    # Diferentes conjuntos de parâmetros baseados em documentação comum
    param_sets = [
        # Parâmetros básicos
        {"ncm": "85423100"},
        {"codigoNcm": "85423100"},
        {"numeroNcm": "85423100"},
        {"ncm": "85423100", "ativo": "true"},
        {"ncm": "85423100", "status": "ativo"},
        {"codigoNcm": "85423100", "ativo": "true"},
        {"numeroNcm": "85423100", "status": "ativo"},

        # Parâmetros de produto
        {"nome": "computador"},
        {"marca": "dell"},
        {"modelo": "inspiron"},
        {"cfi": "123456"},

        # Combinações
        {"ncm": "85423100", "nome": "computador"},
        {"ncm": "85423100", "cfi": "123456"},
        {"nome": "computador", "marca": "dell"},
    ]

    for i, params in enumerate(param_sets, 1):
        print(f"\nTeste {i}: {params}")
        try:
            response = requests.get(endpoint_url, params=params, headers=headers, timeout=BNDES_CFI_API_TIMEOUT)
            print(f"  Status: {response.status_code}")

            if response.status_code == 200:
                print("  ✅ Sucesso!")
                try:
                    data = response.json()
                    print(f"  Resposta: {json.dumps(data, indent=2)[:1000]}...")
                except:
                    print(f"  Resposta (texto): {response.text[:1000]}...")
                return params  # Retorna os parâmetros que funcionaram
            elif response.status_code == 400:
                try:
                    error_data = response.json()
                    print(f"  ⚠️  400 - Detalhes: {error_data}")
                except:
                    print(f"  ⚠️  400 - Mensagem: {response.text}")
            else:
                print(f"  ❌ Status: {response.status_code}")

        except Exception as e:
            print(f"  ❌ Erro: {e}")

    return None


def testar_metodo_post(endpoint_url):
    """Testa método POST com diferentes formatos"""
    print(f"\n=== TESTANDO MÉTODO POST: {endpoint_url} ===")

    headers, auth_meta = _build_headers()
    if "error" in auth_meta:
        print(f"Erro na autenticação: {auth_meta['error']}")
        return

    # Headers para JSON
    json_headers = headers.copy()
    json_headers["Content-Type"] = "application/json"

    # Dados de teste
    test_data = [
        {"ncm": "85423100"},
        {"codigoNcm": "85423100"},
        {"numeroNcm": "85423100"},
        {"query": {"ncm": "85423100"}},
        {"filtro": {"ncm": "85423100"}},
        {"parametros": {"ncm": "85423100"}},
    ]

    for i, data in enumerate(test_data, 1):
        print(f"\nTeste POST {i}: {data}")
        try:
            response = requests.post(endpoint_url, json=data, headers=json_headers, timeout=BNDES_CFI_API_TIMEOUT)
            print(f"  Status: {response.status_code}")

            if response.status_code == 200:
                print("  ✅ Sucesso!")
                try:
                    resp_data = response.json()
                    print(f"  Resposta: {json.dumps(resp_data, indent=2)[:1000]}...")
                except:
                    print(f"  Resposta (texto): {response.text[:1000]}...")
                return data
            elif response.status_code == 400:
                try:
                    error_data = response.json()
                    print(f"  ⚠️  400 - Detalhes: {error_data}")
                except:
                    print(f"  ⚠️  400 - Mensagem: {response.text}")
            else:
                print(f"  ❌ Status: {response.status_code}")

        except Exception as e:
            print(f"  ❌ Erro: {e}")

    return None


def main():
    print("🔍 TESTE AVANÇADO - API CFI BNDES")
    print("=" * 50)

    # Verificar configuração
    print("\n📋 Verificando configuração...")
    try:
        creds = _load_legacy_credentials()
        if "error" in creds:
            print(f"❌ Erro nas credenciais: {creds['error']}")
            return

        token = gerar_token_acesso()
        if "error" in token:
            print(f"❌ Erro no token: {token['error']}")
            return

        print("✅ Configuração OK - Token gerado com sucesso")
    except Exception as e:
        print(f"❌ Erro na configuração: {e}")
        return

    # Testar endpoints
    endpoint_funcionando = testar_endpoint_variacoes()
    if not endpoint_funcionando:
        print("\n❌ Nenhum endpoint básico funcionou. Abortando testes de parâmetros.")
        return

    # Testar parâmetros GET
    params_get = testar_parametros_get(endpoint_funcionando)
    if params_get:
        print(f"\n🎉 SUCESSO! Parâmetros GET funcionaram: {params_get}")
        return

    # Testar método POST
    params_post = testar_metodo_post(endpoint_funcionando)
    if params_post:
        print(f"\n🎉 SUCESSO! Parâmetros POST funcionaram: {params_post}")
        return

    print("\n❌ Nenhum parâmetro testado funcionou. Pode ser necessário:")
    print("   - Consultar documentação oficial da API BNDES")
    print("   - Verificar se há endpoints diferentes para diferentes tipos de busca")
    print("   - Testar autenticação com diferentes escopos")


if __name__ == "__main__":
    main()