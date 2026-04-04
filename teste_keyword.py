#!/usr/bin/env python3
"""Teste da nova implementação com parâmetro keyword"""

from cfi_api import buscar_produto_cfi

print("🧪 Testando nova implementação com parâmetro keyword")
print("=" * 60)

# Teste 1: Buscar por NCM
print("\n1️⃣ Buscando por NCM (85423100):")
resultado = buscar_produto_cfi(ncm='85423100')
print(f"   Status: {resultado.get('success')}")
print(f"   Quantidade: {resultado.get('quantidade', 0)}")
if resultado.get('error'):
    print(f"   Erro: {resultado.get('error')}")
if resultado.get('status_code'):
    print(f"   HTTP Status: {resultado.get('status_code')}")

# Teste 2: Buscar por nome
print("\n2️⃣ Buscando por nome (motor):")
resultado = buscar_produto_cfi(nome='motor')
print(f"   Status: {resultado.get('success')}")
print(f"   Quantidade: {resultado.get('quantidade', 0)}")
if resultado.get('error'):
    error_msg = resultado.get('error')
    if len(error_msg) > 100:
        print(f"   Erro: {error_msg[:100]}...")
    else:
        print(f"   Erro: {error_msg}")
if resultado.get('status_code'):
    print(f"   HTTP Status: {resultado.get('status_code')}")

# Teste 3: Buscar por CFI
print("\n3️⃣ Buscando por CFI (03447782):")
resultado = buscar_produto_cfi(cfi='03447782')
print(f"   Status: {resultado.get('success')}")
print(f"   Quantidade: {resultado.get('quantidade', 0)}")
if resultado.get('data'):
    print(f"   ✅ Primeiros resultados encontrados:")
    for item in resultado.get('data', [])[:2]:
        print(f"     - {item.get('nomeItem', 'N/A')} ({item.get('codigoFiname', 'N/A')})")
elif resultado.get('error'):
    error_msg = resultado.get('error')
    if len(error_msg) > 100:
        print(f"   Erro: {error_msg[:100]}...")
    else:
        print(f"   Erro: {error_msg}")
if resultado.get('status_code'):
    print(f"   HTTP Status: {resultado.get('status_code')}")

print("\n" + "=" * 60)
print("✅ Teste concluído!")
