#!/usr/bin/env python3
"""
TESTE RÁPIDO - Validar que API BNDES CFI está funcionando
Execute este script para confirmar que tudo está configurado corretamente
"""

import os
import sys

print("\n" + "="*70)
print("TESTE RÁPIDO - API BNDES CFI")
print("="*70 + "\n")

# Carregar módulo
try:
    from cfi_api import gerar_token_acesso, buscar_produto_cfi
    print("[✓] Módulo cfi_api importado")
except Exception as e:
    print(f"[✗] Erro ao importar: {e}")
    sys.exit(1)

# Gerar token
try:
    result = gerar_token_acesso()
    if result.get('success'):
        print("[✓] Token gerado com sucesso")
    else:
        print(f"[✗] Erro ao gerar token: {result.get('error')}")
        print("\nDica: Verifique as credenciais em credenciais_api_bdnes.env")
        sys.exit(1)
except Exception as e:
    print(f"[✗] Erro: {e}")
    sys.exit(1)

# Testar busca
try:
    print("\nTestando busca por 'motor'...")
    resultado = buscar_produto_cfi(nome='motor')
    
    if resultado.get('success'):
        qtd = resultado.get('quantidade', 0)
        print(f"[✓] Busca bem-sucedida: {qtd} produtos encontrados")
        
        if resultado.get('data') and len(resultado['data']) > 0:
            primeiro = resultado['data'][0]
            print(f"    Exemplo: {primeiro.get('nomeItem', 'N/A')}")
    else:
        error = resultado.get('error', 'Erro desconhecido')
        print(f"[✗] Erro na busca: {error[:80]}")
        sys.exit(1)
except Exception as e:
    print(f"[✗] Erro: {e}")
    sys.exit(1)

print("\n" + "="*70)
print("RESULTADO: ✓ TUDO FUNCIONANDO!")
print("="*70)
print("\nAgora você pode rodar o app:")
print("  python -m streamlit run app.py --server.port 8505")
print("\nOu execute:")
print("  iniciar_app_credenciais.bat")
print()
