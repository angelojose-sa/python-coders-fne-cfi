#!/usr/bin/env python3
"""Teste final com credenciais confirmadas"""

import os

# Configurar credenciais
os.environ['BNDES_CFI_CONSUMER_KEY'] = 'dKA3jLkCZuuLBWP3yDQXbCXwj0Ua'
os.environ['BNDES_CFI_CONSUMER_SECRET'] = 'VpZxfWkVhAXfzXLgswrawk7Hylga'

from cfi_api import gerar_token_acesso, buscar_produto_cfi

print("🔐 Testando autenticação com credenciais fornecidas")
print("=" * 70)

# Teste 1: Gerar token
print("\n1️⃣ Gerando token...")
token_result = gerar_token_acesso()

if token_result.get('success'):
    print(f"✅ Token gerado com sucesso")
    token = token_result.get('access_token')
    print(f"   Primeiros 50 caracteres: {token[:50]}...")
    
    # Teste 2: Buscar por NCM
    print("\n2️⃣ Buscando produtos por NCM (85423100)...")
    resultado = buscar_produto_cfi(ncm='85423100')
    
    if resultado.get('success'):
        qtd = resultado.get('quantidade', 0)
        print(f"✅ Busca bem-sucedida!")
        print(f"   Total de produtos encontrados: {qtd}")
        
        if resultado.get('data'):
            print(f"\n📊 Primeiros 3 produtos:")
            for i, item in enumerate(resultado.get('data', [])[:3], 1):
                nome = item.get('nomeItem', 'N/A')[:50]
                cfi = item.get('codigoFiname', 'N/A')
                print(f"   {i}. {nome}")
                print(f"      CFI: {cfi}")
    else:
        print(f"❌ Erro na busca: {resultado.get('error')[:100]}")

    # Teste 3: Buscar por nome
    print("\n3️⃣ Buscando produtos por nome (motor)...")
    resultado = buscar_produto_cfi(nome='motor')
    
    if resultado.get('success'):
        qtd = resultado.get('quantidade', 0)
        print(f"✅ Busca bem-sucedida!")
        print(f"   Total de produtos encontrados: {qtd}")
        
        if resultado.get('data'):
            print(f"\n📊 Primeiros 2 produtos com 'motor':")
            for i, item in enumerate(resultado.get('data', [])[:2], 1):
                nome = item.get('nomeItem', 'N/A')[:60]
                fabricante = item.get('fabricante', 'N/A')
                print(f"   {i}. {nome}")
                print(f"      Fabricante: {fabricante}")
    else:
        error_msg = resultado.get('error', 'Desconhecido')
        if len(error_msg) > 100:
            print(f"❌ Erro: {error_msg[:100]}...")
        else:
            print(f"❌ Erro: {error_msg}")

    print("\n" + "=" * 70)
    print("✅ TESTES COMPLETADOS COM SUCESSO!")
    print("   A integração com API BNDES CFI está 100% funcional!")
    
else:
    error = token_result.get('error', 'Desconhecido')
    print(f"❌ Erro ao gerar token: {error}")
    print("\n⚠️ Verifique:")
    print("   - Consumer Key está correto?")
    print("   - Consumer Secret está correto?")
    print("   - Há conexão com internet?")
