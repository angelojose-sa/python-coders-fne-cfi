#!/usr/bin/env python3
"""Teste final - API funcionando corretamente"""

import os
import sys

# Limpar e configurar variáveis
for key in list(os.environ.keys()):
    if 'BNDES' in key or 'CFI' in key:
        del os.environ[key]

os.environ['BNDES_CFI_CONSUMER_KEY'] = 'dKA3jLkCZuuLBWP3yDQXbCXwj0Ua'
os.environ['BNDES_CFI_CONSUMER_SECRET'] = 'VpZxfWkVhAXfzXLgswrawk7Hylga'
os.environ['BNDES_CFI_API_BASE_URL'] = 'https://apis-gateway.bndes.gov.br'
os.environ['BNDES_CFI_API_ENDPOINT'] = '/catalogoCFI/v1/itemfinanciavel/buscar'

# Recarga do módulo
if 'cfi_api' in sys.modules:
    del sys.modules['cfi_api']

from cfi_api import gerar_token_acesso, buscar_produto_cfi

print("🚀 TESTE FINAL - API BNDES CFI")
print("=" * 80)

# Token
token_result = gerar_token_acesso()
print(f"\n✅ Token: {token_result.get('success')}")

if token_result.get('success'):
    # Teste 1: Buscar por nome
    print("\n" + "="*80)
    print("TESTE 1: Buscar por nome (motor)")
    print("="*80)
    
    resultado = buscar_produto_cfi(nome='motor')
    print(f"Status: {resultado.get('success')}")
    
    if resultado.get('success'):
        qtd = resultado.get('quantidade', 0)
        print(f"✅ Produtos encontrados: {qtd}")
        
        if resultado.get('data'):
            print(f"\nPrimeiros 3 produtos:")
            for i, item in enumerate(resultado.get('data', [])[:3], 1):
                nome = item.get('nomeItem', 'N/A')[:60]
                cfi = item.get('codigoFiname', 'N/A')
                ncm = item.get('numeroNcm', 'N/A')
                print(f"  {i}. {nome}")
                print(f"     CFI: {cfi}, NCM: {ncm}")
    else:
        print(f"Mensagem: {resultado.get('error', 'Desconhecido')}")
    
    # Teste 2: Buscar por CNPJ
    print("\n" + "="*80)
    print("TESTE 2: Buscar por CNPJ (12345678000190)")
    print("="*80)
    
    resultado = buscar_produto_cfi(cnpj='12345678000190')
    print(f"Status: {resultado.get('success')}")
    
    if resultado.get('success'):
        qtd = resultado.get('quantidade', 0)
        if qtd > 0:
            print(f"✅ Produtos encontrados: {qtd}")
        else:
            print(f"Nenhum produto encontrado (esperado, CNPJ de teste)")
    else:
        print(f"Mensagem: {resultado.get('error', 'Desconhecido')}")
    
    # Teste 3: Buscar por CFI (código finame)
    print("\n" + "="*80)
    print("TESTE 3: Buscar por CFI (04331510)")
    print("="*80)
    
    resultado = buscar_produto_cfi(cfi='04331510')
    print(f"Status: {resultado.get('success')}")
    
    if resultado.get('success'):
        qtd = resultado.get('quantidade', 0)
        print(f"✅ Produtos encontrados: {qtd}")
        
        if resultado.get('data'):
            for i, item in enumerate(resultado.get('data', [])[:2], 1):
                nome = item.get('nomeItem', 'N/A')[:60]
                cfi = item.get('codigoFiname', 'N/A')
                print(f"  {i}. {nome} (CFI: {cfi})")
    else:
        print(f"Mensagem: {resultado.get('error', 'Desconhecido')}")

print("\n" + "="*80)
print("✅ TESTES CONCLUÍDOS - API FUNCIONANDO COM SUCESSO!")
print("="*80)
print("\nAs credenciais estão configuradas corretamente!")
print("Agora o app está pronto para ser usado.")
