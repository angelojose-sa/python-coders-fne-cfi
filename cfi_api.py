import requests

# Placeholder para integração futura com API CFI/BNDES
BNDES_CFI_BASE_URL = "https://www.bndes.gov.br/cfi-api"  # ajustar conforme documentação real


def buscar_produto_cfi(ncm: str = None, cfi: str = None, nome: str = None):
    """Busca produto na API CFI (mock). Retorna dict com status e dados.

    Ainda não implementado em produção; usar como stub até credenciais e endpoints reais.
    """
    if not ncm and not cfi and not nome:
        return {"success": False, "error": "Pelo menos um parâmetro deve ser fornecido"}

    # Exemplo de chamada real (falta endpoint/autenticação):
    # url = f"{BNDES_CFI_BASE_URL}/produtos"
    # params = {"ncm": ncm, "cfi": cfi, "nome": nome}
    # r = requests.get(url, params=params, timeout=10)
    # r.raise_for_status()
    # return r.json()

    return {"success": False, "error": "Integração com API CFI não configurada"}
