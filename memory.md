# Memória do Projeto - FNE + CFI

## Últimas mudanças
- 2026-04-06: Corrigido erro `FPDFException: Not enough horizontal space to render a single character` em [report.py](report.py), ajustando posicionamento horizontal e largura explícita na renderização de linhas (`_linha_campo`).
- 2026-04-06: Relatórios PDF melhorados em [report.py](report.py) com identidade visual BNB (paleta Pantone 194C/151C/425C), cabeçalho institucional, tentativa de uso do logotipo oficial do app e seção de dados do(s) bem(ns) selecionado(s).
- 2026-04-06: Fluxos de conclusão atualizados em [app.py](app.py) para salvar no resultado final os dados estruturados dos itens selecionados (`itens_selecionados` e `quantidade_itens_confirmados`) para uso no relatório PDF.
- 2026-04-06: Atualizada confirmação de correspondência em resultados com múltiplos itens em [app.py](app.py): o usuário agora pode selecionar um ou mais itens específicos que correspondem ao bem analisado (fluxos de Consulta por NCM, Consulta direta por CFI e refinamento).
- 2026-04-06: Ajustado filtro individual da consulta direta por CFI em [app.py](app.py): removida a opção de pesquisa por fabricante e padronizados os rótulos das opções com inicial maiúscula (Nome, Modelo, Marca, CNPJ), mantendo busca global sem limitação por NCM.
- 2026-04-06: Atualizado fluxo de "Consulta direta por CFI" em [app.py](app.py): após consulta infrutífera ou sem correspondência, o app agora oferece duas opções de continuidade: (1) pesquisar todos os bens pelo mesmo NCM identificado no resultado do CFI e (2) pesquisar por um único filtro individual à escolha do usuário (`nome`, `modelo`, `fabricante`, `marca` ou `cnpj`).
- 2026-04-05: Implementado fluxo completo de "Consulta direta por CFI" em [app.py](app.py), com busca na API CFI, confirmação de correspondência, conclusão da análise, geração de PDF e registro no histórico.
- 2026-04-05: Ajustado aviso de depreciação do Streamlit em [app.py](app.py), trocando `use_container_width=True` por `width='stretch'` em dataframes.
- 2026-04-05: Notebook de modelo [modelos/FNE_v6 (10) (1).ipynb](modelos/FNE_v6%20(10)%20(1).ipynb) marcado para não entrar em commits locais (skip-worktree), sem impacto no app.
- 2026-04-04: Removida exibição direta do JSON da análise e substituída por detalhes amigáveis em expansor no [app.py](app.py).
- 2026-04-04: Reduzido tamanho do logotipo no cabeçalho para proporção adequada e responsiva em [app.py](app.py).
- 2026-04-04: Atualizado visual do app com logotipo do Banco do Nordeste e tema Pantone 194C/151C/425C em [app.py](app.py).
- 2026-04-04: Seção de memória do projeto criada e preenchida com contexto retroativo.
- 2026-04-04: Confirmado uso do arquivo local memory.md como registro permanente no workspace.
- 2026-04-04: Definido processo de atualização contínua desta seção a cada avanço relevante.

## Contexto retroativo
- Objetivo: app Python (Streamlit) para analisar financiabilidade FNE.
- Base de regras: [regras_de_analise.md](regras_de_analise.md).
- Fonte principal de NCM passível: [NCMspassíveisdeCFI.csv](NCMspassíveisdeCFI.csv).

## O que já foi implementado
- Validação de NCM e decisão inicial de financiabilidade.
- Histórico local de consultas.
- Geração de relatório PDF.
- Integração com API CFI do BNDES em [cfi_api.py](cfi_api.py).
- Interface de uso no navegador em [app.py](app.py).

## Integração CFI/BNDES
- Autenticação OAuth2 com consumer key/secret.
- Endpoint de busca utilizado: `https://apis-gateway.bndes.gov.br/catalogoCFI/v1/itemfinanciavel/buscar`.
- Parâmetro de busca principal: `keyword`.
- Risco já identificado: variáveis de ambiente antigas podem duplicar URL e causar 404.

## Credenciais e configuração
- Credenciais em [credenciais_api_bdnes.env](credenciais_api_bdnes.env).
- Se houver erro 404 inesperado, validar `BNDES_CFI_API_BASE_URL` e `BNDES_CFI_API_ENDPOINT` no ambiente ativo.

## Estado atual
- Token OAuth gera com sucesso.
- Busca na API funciona quando a URL é montada sem duplicação.
- Projeto está pronto para uso e evolução das regras finais (CFI/CST/exceções).

## Preferência do usuário
- Manter registro de contexto retroativo e contínuo.
