import base64
import json
import os
import re
import unicodedata
from datetime import datetime

import pandas as pd
import streamlit as st

from cfi_api import buscar_produto_cfi, get_cfi_config_errors, is_cfi_api_configured
from report import gerar_relatorio_pdf


ROOT = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(ROOT, "NCMspassíveisdeCFI.csv")
HISTORY_PATH = os.path.join(ROOT, "history.json")
LOGO_PATH = os.path.join(ROOT, "modelos", "Logo_do_Banco_do_Nordeste.svg")


def aplicar_tema_visual():
    # Paleta observada no tema publico oficial do Banco do Nordeste
    vermelho_principal = "#A6193C"
    vermelho_destaque = "#DF2C59"
    laranja_principal = "#F88A27"
    cinza_texto = "#4A4A4A"

    st.markdown(
        f"""
        <style>
            :root {{
                --cor-primaria: {vermelho_principal};
                --cor-primaria-2: {vermelho_destaque};
                --cor-secundaria: {laranja_principal};
                --cor-terciaria: {cinza_texto};
                --superficie: #ffffff;
                --superficie-2: #f8f8f8;
                --texto-claro: #fafafa;
            }}

            .stApp {{
                background:
                    radial-gradient(circle at 8% 10%, rgba(166, 25, 60, 0.08), rgba(166, 25, 60, 0) 30%),
                    radial-gradient(circle at 92% 2%, rgba(248, 138, 39, 0.11), rgba(248, 138, 39, 0) 28%),
                    linear-gradient(180deg, #f6f6f6 0%, #efefef 100%);
                color: var(--cor-terciaria);
            }}

            .main .block-container {{
                max-width: 540px;
                background: var(--superficie);
                padding: 0 !important;
                border-radius: 20px;
                overflow: hidden;
                margin-top: 1rem;
                border: 1px solid rgba(166, 25, 60, 0.12);
                box-shadow: 0 14px 32px rgba(0, 0, 0, 0.13);
            }}

            .app-header {{
                border-radius: 0;
                border: none;
                padding: 0.35rem 0.85rem 0.25rem 0.85rem;
                background: radial-gradient(circle at 82% 6%, rgba(255, 255, 255, 0.24), rgba(255, 255, 255, 0) 36%),
                    linear-gradient(135deg, var(--cor-primaria) 0%, var(--cor-primaria-2) 100%);
                margin-bottom: 0;
                color: #ffffff;
                min-height: 92px;
                display: flex;
                flex-direction: column;
                justify-content: space-between;
                align-items: stretch;
                gap: 0;
            }}

            .header-top {{
                width: 100%;
                min-height: 40%;
                display: flex;
                align-items: flex-start;
                justify-content: flex-start;
            }}

            .header-bottom {{
                width: 100%;
                min-height: 60%;
                display: flex;
                align-items: flex-end;
                justify-content: center;
            }}

            /* Streamlit injeta espaco entre elementos; removemos o gap apos o cabecalho */
            div[data-testid="stVerticalBlock"] > div:has(.app-header) {{
                margin-bottom: 0 !important;
                padding-bottom: 0 !important;
            }}

            div[data-testid="stVerticalBlock"] > div:has(.app-header) + div {{
                margin-top: 0 !important;
                padding-top: 0 !important;
                background: linear-gradient(180deg, #f6f6f6 0%, #efefef 100%) !important;
            }}

            div[data-testid="stVerticalBlock"] > div:has(.app-header) [data-testid="stMarkdownContainer"] {{
                margin-bottom: 0 !important;
                padding-bottom: 0 !important;
            }}

            .title-wrap {{
                width: 90%;
                display: flex;
                justify-content: center;
                align-items: flex-end;
                margin: 0 auto;
                text-align: center;
            }}

            .app-header .app-title {{
                color: var(--texto-claro);
                font-weight: 800;
                letter-spacing: 0.1px;
                margin: 0;
                line-height: 1.15;
                font-size: 1.5rem !important;
                text-wrap: balance;
            }}

            .logo-wrap {{
                width: 20%;
                max-width: 96px;
                display: flex;
                justify-content: flex-start;
                align-items: flex-start;
                margin: 0;
            }}

            .logo-wrap svg {{
                width: 100% !important;
                height: auto !important;
                display: block;
            }}

            .logo-wrap img {{
                width: 100% !important;
                height: auto !important;
                display: block;
            }}

            .content-wrap {{
                padding: 0 1rem 1.2rem 1rem;
                background: linear-gradient(180deg, #f6f6f6 0%, #efefef 100%);
            }}

            .st-key-menu_principal > label {{
                display: none;
            }}

            .st-key-menu_principal {{
                display: flex;
                justify-content: stretch;
                margin: 0 0 0.75rem 0;
                width: 100%;
            }}

            .st-key-menu_principal [role="radiogroup"] {{
                display: flex;
                flex-wrap: nowrap;
                gap: 0.5rem !important;
                border: none;
                overflow: visible;
                background: transparent;
                width: 100%;
                margin: 0 auto;
                justify-content: space-between;
            }}

            .st-key-menu_principal [role="radiogroup"] > label {{
                flex: 1 1 0;
                display: grid;
                place-items: center;
                margin: 0 !important;
                min-height: 46px;
                padding: 0.22rem 0.55rem !important;
                border: 1px solid rgba(166, 25, 60, 0.25);
                border-radius: 999px;
                text-align: center;
                background: var(--superficie);
                box-shadow: 0 2px 6px rgba(0, 0, 0, 0.06);
                transition: all 0.2s ease, transform 0.12s ease;
            }}

            .st-key-menu_principal [role="radiogroup"] > label > div:first-child {{
                display: none;
            }}

            .st-key-menu_principal [role="radiogroup"] > label > div:last-child {{
                display: flex;
                align-items: center;
                justify-content: center;
                width: 100%;
                height: 100%;
                margin: 0 !important;
                padding: 0 !important;
            }}

            .st-key-menu_principal [role="radiogroup"] > label [data-testid="stMarkdownContainer"] {{
                display: flex;
                align-items: center;
                justify-content: center;
                width: 100%;
                height: 100%;
                margin: 0 !important;
                padding: 0 !important;
            }}

            .st-key-menu_principal [role="radiogroup"] > label p {{
                color: var(--cor-primaria);
                font-weight: 700;
                margin: 0 !important;
                width: 100%;
                height: 100%;
                display: flex;
                align-items: center;
                justify-content: center;
                text-align: center;
                white-space: nowrap;
                overflow-wrap: anywhere;
                line-height: 1;
                font-size: 0.9rem;
            }}

            .st-key-menu_principal [role="radiogroup"] > label:has(input:checked) {{
                background: linear-gradient(135deg, var(--cor-primaria) 0%, var(--cor-primaria-2) 100%);
                border-color: transparent;
                box-shadow: 0 6px 14px rgba(166, 25, 60, 0.26);
            }}

            .st-key-menu_principal [role="radiogroup"] > label:has(input:checked) p {{
                color: #ffffff;
            }}

            .st-key-menu_principal [role="radiogroup"] > label:hover {{
                border-color: rgba(166, 25, 60, 0.45);
                background: #fff8fa;
                transform: translateY(-1px);
            }}

            div[data-baseweb="input"] > div,
            .stTextInput > div > div > input {{
                border-color: rgba(74, 74, 74, 0.22) !important;
                border-radius: 10px !important;
                min-height: 46px;
                background: var(--superficie) !important;
                box-shadow: inset 0 1px 1px rgba(0, 0, 0, 0.03);
            }}

            .stTextInput > div > div > input:focus,
            div[data-baseweb="input"] > div:focus-within {{
                border-color: rgba(166, 25, 60, 0.45) !important;
                box-shadow: 0 0 0 3px rgba(166, 25, 60, 0.14) !important;
            }}

            .stButton > button,
            .stDownloadButton > button,
            .stFormSubmitButton > button {{
                background: linear-gradient(135deg, var(--cor-primaria) 0%, var(--cor-primaria-2) 100%) !important;
                color: #ffffff !important;
                border: 1px solid rgba(255, 255, 255, 0.12) !important;
                border-radius: 10px !important;
                font-weight: 700 !important;
                min-height: 44px;
                box-shadow: 0 6px 14px rgba(166, 25, 60, 0.2);
                transition: transform 0.12s ease, box-shadow 0.18s ease;
            }}

            .stButton > button:hover,
            .stDownloadButton > button:hover,
            .stFormSubmitButton > button:hover {{
                background: linear-gradient(135deg, var(--cor-secundaria) 0%, #ff9f4d 100%) !important;
                color: #ffffff !important;
                transform: translateY(-1px);
                box-shadow: 0 8px 16px rgba(248, 138, 39, 0.24);
            }}

            .stAlert {{
                border-radius: 10px;
                border: 1px solid rgba(166, 25, 60, 0.14);
            }}

            h3 {{
                color: var(--cor-terciaria);
                letter-spacing: 0.15px;
                margin-top: 0.15rem;
                margin-bottom: 0.6rem;
            }}

            .stDataFrame, .stTable {{
                border: 1px solid rgba(74, 74, 74, 0.14);
                border-radius: 12px;
                overflow: hidden;
            }}

            @media (max-width: 640px) {{
                .main .block-container {{
                    margin-top: 0.6rem;
                    border-radius: 16px;
                }}

                .app-header {{
                    min-height: 84px;
                    padding: 0.32rem 0.75rem 0.22rem 0.75rem;
                }}

                .logo-wrap {{
                    width: 26%;
                    max-width: 82px;
                }}

                .title-wrap {{
                    width: 90%;
                }}

                .app-header .app-title {{
                    font-size: 1.2rem !important;
                }}

                .content-wrap {{
                    padding: 0 0.8rem 1rem 0.8rem;
                    background: linear-gradient(180deg, #f6f6f6 0%, #efefef 100%);
                }}
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def renderizar_cabecalho():
    logo_html = ""
    if os.path.exists(LOGO_PATH):
        if LOGO_PATH.lower().endswith(".svg"):
            with open(LOGO_PATH, "r", encoding="utf-8") as f:
                logo_html = f.read()
            # Mantem o logo oficial e ajusta apenas os tons de vermelho para branco.
            logo_html = re.sub(r"#A80A35", "#FFFFFF", logo_html, flags=re.IGNORECASE)
            logo_html = re.sub(r"#A6193C", "#FFFFFF", logo_html, flags=re.IGNORECASE)
            logo_html = re.sub(r"#9D2235", "#FFFFFF", logo_html, flags=re.IGNORECASE)
        else:
            with open(LOGO_PATH, "rb") as f:
                logo_b64 = base64.b64encode(f.read()).decode("ascii")
            logo_html = f"<img src='data:image/png;base64,{logo_b64}' alt='Banco do Nordeste'/>"
    else:
        logo_html = "<img src='https://www.bnb.gov.br/o/bnb-dxp-theme/images/logo-bnb-mobile.svg' alt='Banco do Nordeste'/>"

    st.markdown(
        f"""
        <div class="app-header">
            <div class="header-top">
                <div class="logo-wrap">{logo_html}</div>
            </div>
            <div class="header-bottom">
                <div class="title-wrap">
                    <div class="app-title">Análise de Bens Financiáveis via FNE</div>
                </div>
            </div>
        </div>
        <div class="content-wrap">
        """,
        unsafe_allow_html=True,
    )


def carregar_ncms_passiveis(csv_path: str):
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Arquivo CSV n\u00e3o encontrado: {csv_path}")

    df = pd.read_csv(csv_path, dtype=str)
    if "NCMspassíveisdeCFI" in df.columns:
        coluna = "NCMspassíveisdeCFI"
    elif "NCM" in df.columns:
        coluna = "NCM"
    else:
        raise ValueError("CSV deve conter coluna 'NCMspassíveisdeCFI' ou 'NCM'")

    ncms = df[coluna].dropna().astype(str).str.strip().str.replace("[^0-9]", "", regex=True)
    ncms = ncms[ncms.str.len() > 0].str.zfill(8)
    return set(ncms.tolist())


def normalizar_ncm(ncm: str):
    if not ncm:
        return ""
    n = ''.join([c for c in ncm if c.isdigit()])
    return n.zfill(8) if len(n) > 0 else ""


def carregar_historico(path: str):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def salvar_historico(path: str, historico: list):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(historico, f, ensure_ascii=False, indent=2)


def adicionar_historico(entry: dict):
    if not entry.get("tipo_consulta"):
        if entry.get("ncm"):
            entry["tipo_consulta"] = "Consulta por NCM"
        elif entry.get("cfi"):
            entry["tipo_consulta"] = "Consulta direta por CFI"
        else:
            entry["tipo_consulta"] = "Consulta"

    history = carregar_historico(HISTORY_PATH)
    history.insert(0, entry)
    salvar_historico(HISTORY_PATH, history)


def analisar_ncm(ncm: str, cfi: str = None, cst: str = None):
    ncm_norm = normalizar_ncm(ncm)
    if not ncm_norm or len(ncm_norm) != 8:
        return {
            "status": "erro",
            "mensagem": "NCM inv\u00e1lido. Informe 8 d\u00edgitos num\u00e9ricos.",
            "ncm": ncm_norm,
        }

    try:
        ncms_passiveis = carregar_ncms_passiveis(CSV_PATH)
    except Exception as exc:
        return {
            "status": "erro",
            "mensagem": f"Falha ao carregar CSV de NCMs: {exc}",
            "ncm": ncm_norm,
        }

    if ncm_norm not in ncms_passiveis:
        resultado = "NCM não consta na lista de passíveis de credenciamento no CFI. Bem financiável pelo FNE!"
        status = "financiavel"
    else:
        resultado = "NCM consta na lista de passíveis de credenciamento no CFI. Investigar CFI/CST para decisão definitiva."
        status = "pendente"

    analise = {
        "data_hora": datetime.now().isoformat(sep=" ", timespec="seconds"),
        "ncm": ncm_norm,
        "cfi": cfi or "",
        "cst": cst or "",
        "status": status,
        "resultado": resultado,
    }
    return analise


def normalizar_cst(cst: str):
    if not cst:
        return ""
    somente_digitos = "".join([c for c in cst if c.isdigit()])
    return somente_digitos[:3]


def construir_resultado_final(base: dict, status: str, resultado: str, justificativa: str):
    final = dict(base)
    final["status"] = status
    final["resultado"] = resultado
    final["justificativa"] = justificativa
    final["data_hora"] = datetime.now().isoformat(sep=" ", timespec="seconds")
    return final


def decidir_sem_similar_nacional(base: dict):
    cst = normalizar_cst(base.get("cst", ""))
    if cst and cst[0] in {"6", "7"}:
        return construir_resultado_final(
            base,
            status="financiavel",
            resultado="Financiável pelo FNE.",
            justificativa="CST indica inexistência de similar nacional (origem iniciada em 6 ou 7).",
        )

    return construir_resultado_final(
        base,
        status="financiavel_condicionado",
        resultado="Financiável se inexistente similar nacional.",
        justificativa="NCM passível de CFI sem correspondência no catálogo.",
    )


def mostrar_resultado_final(resultado: dict):
    st.success(resultado.get("resultado", "Resultado concluído."))

    with st.expander("Ver detalhes da análise"):
        st.write(f"Data/Hora: {resultado.get('data_hora', '')}")
        st.write(f"NCM: {resultado.get('ncm', '')}")
        st.write(f"CFI informado: {resultado.get('cfi', '') or 'Não informado'}")
        st.write(f"CST informado: {resultado.get('cst', '') or 'Não informado'}")
        st.write(f"Status da análise: {resultado.get('status', '')}")
        st.write(f"Justificativa: {resultado.get('justificativa', 'N/A')}")

    if st.button("Gerar relatório PDF", key="btn_gerar_pdf"):
        filename = f"relatorio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        out_path = os.path.join(ROOT, filename)
        gerar_relatorio_pdf(resultado, out_path)
        with open(out_path, "rb") as f:
            pdf_bytes = f.read()
        st.download_button(
            "Download PDF",
            data=pdf_bytes,
            file_name=filename,
            mime="application/pdf",
            key="btn_download_pdf",
        )


@st.cache_data(ttl=600, show_spinner=False)
def consultar_cfi_por_campo_cache(campo: str, termo: str, quantidade: int = 500):
    if campo == "fabricante":
        return buscar_produto_cfi(fabricante=termo, quantidade=quantidade)
    if campo == "cnpj":
        return buscar_produto_cfi(cnpj=termo, quantidade=quantidade)
    if campo == "marca":
        return buscar_produto_cfi(marca=termo, quantidade=quantidade)
    if campo == "modelo":
        return buscar_produto_cfi(modelo=termo, quantidade=quantidade)
    return buscar_produto_cfi(nome=termo, quantidade=quantidade)


def normalizar_texto_busca(valor: str) -> str:
    texto = str(valor or "").strip().lower()
    texto = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in texto if not unicodedata.combining(c))


def apenas_digitos(valor: str) -> str:
    return "".join(c for c in str(valor or "") if c.isdigit())


def extrair_ncms_da_consulta(consulta: dict) -> list[str]:
    ncms = []
    vistos = set()
    for item in (consulta or {}).get("data", []) or []:
        ncm_item = normalizar_ncm(item.get("numeroNcm", ""))
        if ncm_item and ncm_item not in vistos:
            vistos.add(ncm_item)
            ncms.append(ncm_item)
    return ncms


def obter_identificador_item(item: dict, indice: int) -> str:
    for campo in ["codigoFiname", "cfi", "codigoCFI", "codigo", "id", "numeroFiname"]:
        valor = item.get(campo)
        if valor not in [None, ""]:
            return str(valor).strip()
    return f"idx-{indice + 1}"


def rotulo_item_catalogo(item: dict, indice: int) -> str:
    codigo = str(item.get("codigoFiname") or item.get("cfi") or item.get("codigoCFI") or "N/A").strip()
    nome = str(item.get("nomeItem") or "Sem descrição").strip()
    modelo = str(item.get("modeloItem") or "N/A").strip()
    fabricante = str(item.get("fabricante") or "N/A").strip()
    ncm = normalizar_ncm(item.get("numeroNcm", "")) or "N/A"
    return f"[{indice + 1}] CFI {codigo} | {nome[:70]} | Modelo: {modelo[:30]} | Marca/Fabricante: {fabricante[:30]} | NCM: {ncm}"


def selecionar_itens_correspondentes(itens: list, key_prefix: str) -> tuple[bool, list]:
    itens = itens or []
    if not itens:
        return False, []

    if len(itens) == 1:
        st.write("Item encontrado:")
        st.caption(rotulo_item_catalogo(itens[0], 0))
        corresponde = st.checkbox(
            "Este item corresponde ao bem analisado?",
            key=f"{key_prefix}_unico",
        )
        return corresponde, [itens[0]] if corresponde else []

    opcoes = []
    mapa_itens = {}
    for i, item in enumerate(itens):
        label = rotulo_item_catalogo(item, i)
        if label in mapa_itens:
            label = f"{label} | Ref: {obter_identificador_item(item, i)}"
        opcoes.append(label)
        mapa_itens[label] = item

    selecionados_labels = st.multiselect(
        "Selecione um ou mais itens que correspondem ao bem analisado:",
        options=opcoes,
        key=f"{key_prefix}_multiplos",
    )
    itens_selecionados = [mapa_itens[label] for label in selecionados_labels]

    if itens_selecionados:
        st.caption(f"Itens selecionados: {len(itens_selecionados)}")
    else:
        st.caption("Nenhum item selecionado.")

    return len(itens_selecionados) > 0, itens_selecionados


def resumir_itens_para_relatorio(itens: list) -> list[dict]:
    resumo = []
    for item in itens or []:
        resumo.append(
            {
                "codigoFiname": str(item.get("codigoFiname") or item.get("cfi") or item.get("codigoCFI") or "").strip(),
                "nomeItem": str(item.get("nomeItem") or "").strip(),
                "modeloItem": str(item.get("modeloItem") or "").strip(),
                "fabricante": str(item.get("fabricante") or "").strip(),
                "cnpjFabricante": str(item.get("cnpjFabricante") or "").strip(),
                "numeroNcm": normalizar_ncm(item.get("numeroNcm", "")),
                "posicaoCadastral": str(item.get("posicaoCadastral") or "").strip(),
                "imagemItem": str(item.get("imagemItem") or "").strip(),
            }
        )
    return resumo


def filtrar_itens_catalogo(itens: list, filtros: dict) -> list:
    campos_textuais = ["nomeItem", "modeloItem", "fabricante", "cnpjFabricante", "nomeNaturezaItem"]
    resultado = []
    vistos = set()

    termo = normalizar_texto_busca(filtros.get("termo", ""))
    termos = [t for t in re.split(r"\s+", termo) if t] if termo else []

    ncm_filtro = apenas_digitos(filtros.get("ncm", ""))
    cfi_filtro = apenas_digitos(filtros.get("cfi", "")).lstrip("0")
    nome_filtro = normalizar_texto_busca(filtros.get("nome", ""))
    modelo_filtro = normalizar_texto_busca(filtros.get("modelo", ""))
    marca_filtro = normalizar_texto_busca(filtros.get("marca", ""))
    fabricante_filtro = normalizar_texto_busca(filtros.get("fabricante", ""))
    cnpj_filtro = apenas_digitos(filtros.get("cnpj", ""))

    for item in itens or []:
        texto_campos = " ".join(normalizar_texto_busca(item.get(campo, "")) for campo in campos_textuais)
        if termos and not any(t in texto_campos for t in termos):
            continue

        if ncm_filtro and apenas_digitos(item.get("numeroNcm", "")) != ncm_filtro:
            continue

        codigo_item = apenas_digitos(item.get("codigoFiname", "")).lstrip("0")
        if cfi_filtro and codigo_item != cfi_filtro:
            continue

        if nome_filtro and nome_filtro not in normalizar_texto_busca(item.get("nomeItem", "")):
            continue

        if modelo_filtro and modelo_filtro not in normalizar_texto_busca(item.get("modeloItem", "")):
            continue

        fabricante_texto = normalizar_texto_busca(item.get("fabricante", ""))
        if marca_filtro and marca_filtro not in fabricante_texto:
            continue

        if fabricante_filtro and fabricante_filtro not in fabricante_texto:
            continue

        if cnpj_filtro and cnpj_filtro not in apenas_digitos(item.get("cnpjFabricante", "")):
            continue

        chave_item = None
        for campo_id in ["codigoFiname", "cfi", "codigoCFI", "codigo", "id", "numeroFiname"]:
            valor = item.get(campo_id)
            if valor not in [None, ""]:
                chave_item = f"{campo_id}:{str(valor).strip()}"
                break

        if not chave_item:
            chave_item = json.dumps(item, sort_keys=True, ensure_ascii=False)

        if chave_item in vistos:
            continue

        vistos.add(chave_item)
        resultado.append(item)

    return resultado


def gerar_termos_fallback(termo: str) -> list[str]:
    termo_norm = normalizar_texto_busca(termo)
    palavras = [p for p in re.split(r"\s+", termo_norm) if len(p) >= 6]
    termos = []
    for palavra in palavras:
        for tamanho in [5, 4]:
            if len(palavra) > tamanho:
                candidato = palavra[:tamanho]
                if candidato not in termos:
                    termos.append(candidato)
        if len(termos) >= 4:
            break
    return termos[:4]


def buscar_produto_cfi_multicampos(termo: str):
    termo_limpo = (termo or "").strip()
    if not termo_limpo:
        return {"success": False, "error": "Informe um termo para a busca multicampo."}

    respostas = [
        ("nome", consultar_cfi_por_campo_cache("nome", termo_limpo, quantidade=500)),
        ("modelo", consultar_cfi_por_campo_cache("modelo", termo_limpo, quantidade=500)),
        ("marca", consultar_cfi_por_campo_cache("marca", termo_limpo, quantidade=500)),
        ("fabricante", consultar_cfi_por_campo_cache("fabricante", termo_limpo, quantidade=500)),
        ("cnpj", consultar_cfi_por_campo_cache("cnpj", termo_limpo, quantidade=500)),
    ]

    respostas_ok = [(origem, resp) for origem, resp in respostas if resp.get("success")]
    if not respostas_ok:
        erros = [f"{origem}: {resp.get('error', 'Erro desconhecido')}" for origem, resp in respostas]
        return {
            "success": False,
            "error": "Falha na consulta ao catálogo CFI.",
            "details": erros,
            "keywords": [
                f"nome:{termo_limpo}",
                f"modelo:{termo_limpo}",
                f"marca:{termo_limpo}",
                f"fabricante:{termo_limpo}",
                f"cnpj:{termo_limpo}",
            ],
        }

    itens_base = []
    for _, resposta in respostas_ok:
        itens_base.extend(resposta.get("data", []))

    itens_filtrados = filtrar_itens_catalogo(itens_base, {"termo": termo_limpo})

    keywords = [
        f"nome:{termo_limpo}",
        f"modelo:{termo_limpo}",
        f"marca:{termo_limpo}",
        f"fabricante:{termo_limpo}",
        f"cnpj:{termo_limpo}",
    ]

    # Fallback controlado para termos longos quando a API não retorna o item esperado no termo completo.
    if not itens_filtrados:
        termos_fallback = gerar_termos_fallback(termo_limpo)
        for termo_fb in termos_fallback:
            keywords.extend([
                f"nome:{termo_fb}",
                f"modelo:{termo_fb}",
                f"marca:{termo_fb}",
                f"fabricante:{termo_fb}",
            ])
            itens_fb = []
            for campo in ["nome", "modelo", "marca", "fabricante"]:
                resposta_fb = consultar_cfi_por_campo_cache(campo, termo_fb, quantidade=200)
                if resposta_fb.get("success"):
                    itens_fb.extend(resposta_fb.get("data", []))

            if itens_fb:
                itens_filtrados = filtrar_itens_catalogo(itens_fb, {"termo": termo_limpo})
                if itens_filtrados:
                    break

    return {
        "success": True,
        "data": itens_filtrados,
        "quantidade": len(itens_filtrados),
        "keywords": keywords,
        "fields_filtered": ["nomeItem", "modeloItem", "fabricante", "cnpjFabricante", "nomeNaturezaItem"],
    }


def inicializar_estado_fluxo():
    if "fluxo_ncm" not in st.session_state:
        st.session_state["fluxo_ncm"] = None
    if "resultado_final" not in st.session_state:
        st.session_state["resultado_final"] = None
    if "fluxo_cfi" not in st.session_state:
        st.session_state["fluxo_cfi"] = None
    if "resultado_final_cfi" not in st.session_state:
        st.session_state["resultado_final_cfi"] = None


def resetar_fluxo():
    st.session_state["fluxo_ncm"] = None
    st.session_state["resultado_final"] = None
    for chave in [
        "input_ncm_inicial",
        "filtro_cfi",
        "filtro_unico_ncm",
        "mostrar_todos_itens_ncm",
        "radio_correspondencia",
        "selecao_correspondencia_ncm_unico",
        "selecao_correspondencia_ncm_multiplos",
    ]:
        if chave in st.session_state:
            del st.session_state[chave]


def resetar_fluxo_cfi():
    st.session_state["fluxo_cfi"] = None
    st.session_state["resultado_final_cfi"] = None
    for chave in [
        "input_cfi_direto",
        "filtro_cst_direto",
        "filtro_nome_direto",
        "filtro_marca_direto",
        "filtro_modelo_direto",
        "filtro_cnpj_direto",
        "radio_acao_pos_consulta_cfi",
        "select_ncm_refino_cfi",
        "tipo_filtro_individual_cfi",
        "valor_filtro_individual_cfi",
        "radio_correspondencia_cfi",
        "radio_correspondencia_cfi_refino",
        "selecao_correspondencia_cfi_unico",
        "selecao_correspondencia_cfi_multiplos",
        "selecao_correspondencia_refino_unico",
        "selecao_correspondencia_refino_multiplos",
    ]:
        if chave in st.session_state:
            del st.session_state[chave]


def renderizar_consulta_ncm():
    st.markdown("### Consulta por NCM")
    st.caption("Etapa 1: informe apenas o NCM. Etapa 2: em caso de NCM passível, refine a busca no catálogo CFI.")

    with st.form(key="consulta_ncm_inicial_form"):
        ncm_digitado = st.text_input(
            "NCM (8 dígitos)",
            key="input_ncm_inicial",
            max_chars=8,
            help="Aceita somente 8 dígitos numéricos.",
        )
        submit_ncm = st.form_submit_button("Consultar NCM")

    if submit_ncm:
        ncm_input = "".join([c for c in ncm_digitado if c.isdigit()])
        base = analisar_ncm(ncm_input)

        if base.get("status") == "erro":
            st.error(base["mensagem"])
            return

        st.session_state["resultado_final"] = None
        st.session_state["fluxo_ncm"] = {
            "base": base,
            "filtros": {"ncm": ncm_input},
            "consulta": None,
            "busca_realizada": False,
        }

        if base.get("status") == "financiavel":
            resultado_final = construir_resultado_final(
                base,
                status="financiavel",
                resultado="Financiável pelo FNE.",
                justificativa="NCM não passível de credenciamento no CFI.",
            )
            adicionar_historico(resultado_final)
            st.session_state["resultado_final"] = resultado_final
        else:
            st.info("NCM passível de CFI. Informe filtros opcionais para consultar o catálogo.")

    fluxo = st.session_state.get("fluxo_ncm")
    if not fluxo:
        return

    base = fluxo.get("base", {})
    consulta = fluxo.get("consulta")
    resultado_final = st.session_state.get("resultado_final")

    if resultado_final:
        mostrar_resultado_final(resultado_final)
        if st.button("Reiniciar análise", key="btn_resetar_analise"):
            resetar_fluxo()
        return

    if base.get("status") != "pendente":
        return

    st.info("NCM passível de CFI. Use o refino unificado para consultar e concluir a análise.")

    with st.form(key="consulta_cfi_refinada_form"):
        st.write(f"NCM consultado: {base.get('ncm', '')}")
        cfi_input = st.text_input("CFI (opcional)", key="filtro_cfi")
        termo_unico = st.text_input(
            "Pesquisa única (opcional)",
            key="filtro_unico_ncm",
            help="Busca parcial em nomeItem, modeloItem, fabricante, cnpjFabricante e nomeNaturezaItem.",
        )
        submit_busca = st.form_submit_button("Consultar catálogo CFI")

    if submit_busca:
        base["cfi"] = cfi_input or ""
        base["cst"] = ""
        st.session_state["fluxo_ncm"]["base"] = base
        filtros_usuario = {
            "ncm": base.get("ncm", ""),
            "cfi": cfi_input,
            "termo": termo_unico,
        }
        st.session_state["fluxo_ncm"]["filtros"] = filtros_usuario

        # Na aba NCM, a busca principal deve permanecer ancorada no NCM
        # para manter consistência com o fluxo original. Campos adicionais
        # refinam localmente os resultados retornados.
        criterio_api = {"ncm": base.get("ncm", "")}

        if is_cfi_api_configured():
            st.info("Consultando Catálogo CFI do BNDES...")
            consulta = buscar_produto_cfi(**criterio_api, quantidade=500)
            if consulta.get("success"):
                itens_brutos = consulta.get("data", [])
                itens_filtrados = filtrar_itens_catalogo(itens_brutos, filtros_usuario)
                consulta["data_bruta"] = itens_brutos
                consulta["quantidade_bruta"] = len(itens_brutos)
                consulta["data"] = itens_filtrados
                consulta["quantidade"] = len(itens_filtrados)
            st.session_state["fluxo_ncm"]["consulta"] = consulta
            st.session_state["fluxo_ncm"]["busca_realizada"] = True
        else:
            missing = get_cfi_config_errors()
            st.warning(
                "Integração CFI não configurada. Variáveis faltantes: " + ", ".join(missing)
            )
            st.info("Veja o arquivo MODELO_INTEGACAO_BNDES.md para instruções de configuração.")

    if not fluxo.get("busca_realizada", False):
        st.caption("Aguardando consulta ao catálogo CFI para avançar nas decisões do fluxo.")
        return

    if not consulta:
        st.warning("Não foi possível concluir sem consulta ao catálogo CFI.")
        return

    if consulta.get("success"):
        quantidade = consulta.get("quantidade", 0)
        st.success(f"{quantidade} produto(s) encontrado(s) no catálogo CFI.")

        quantidade_bruta = consulta.get("quantidade_bruta", quantidade)
        mostrar_todos = st.checkbox(
            f"Mostrar todos os itens da pesquisa base por NCM ({quantidade_bruta})",
            key="mostrar_todos_itens_ncm",
            value=False,
        )

        if mostrar_todos:
            with st.expander("Todos os itens retornados pela pesquisa de NCM"):
                if consulta.get("data_bruta"):
                    df_cfi_bruto = pd.DataFrame(consulta["data_bruta"])
                    st.dataframe(df_cfi_bruto, width='stretch')
                else:
                    st.info("A pesquisa base por NCM não retornou itens.")

        with st.expander("Detalhes dos produtos encontrados"):
            if consulta.get("data"):
                df_cfi = pd.DataFrame(consulta["data"])
                st.dataframe(df_cfi, width='stretch')
            else:
                st.info("Nenhum produto encontrado com os critérios informados.")

        if quantidade > 0:
            corresponde, itens_correspondentes = selecionar_itens_correspondentes(
                consulta.get("data", []),
                "selecao_correspondencia_ncm",
            )

            if st.button("Concluir análise", key="btn_concluir_com_correspondencia"):
                if corresponde:
                    final = construir_resultado_final(
                        base,
                        status="financiavel",
                        resultado="Financiável pelo FNE.",
                        justificativa=f"Bem credenciado e correspondente encontrado no catálogo CFI. Itens confirmados pelo usuário: {len(itens_correspondentes)}.",
                    )
                    final["itens_selecionados"] = resumir_itens_para_relatorio(itens_correspondentes)
                    final["quantidade_itens_confirmados"] = len(itens_correspondentes)
                else:
                    final = decidir_sem_similar_nacional(base)

                adicionar_historico(final)
                st.session_state["resultado_final"] = final
                st.rerun()
        else:
            if st.button("Concluir análise", key="btn_concluir_sem_resultado"):
                final = decidir_sem_similar_nacional(base)
                adicionar_historico(final)
                st.session_state["resultado_final"] = final
                st.rerun()
    else:
        st.warning("Falha na consulta ao catálogo CFI.")
        st.error(consulta.get("error", "Erro desconhecido"))
        with st.expander("Detalhes técnicos"):
            st.write(f"Status HTTP: {consulta.get('status_code', 'N/A')}")
            st.write(f"Keyword usado: {consulta.get('keyword', 'N/A')}")
            st.write(f"URL: {consulta.get('url', 'N/A')}")


def renderizar_consulta_direta_cfi():
    st.markdown("### Consulta direta por CFI")
    st.caption("Informe o CFI para a consulta inicial. Se a busca for infrutífera ou sem correspondência, escolha entre pesquisar por NCM do CFI ou por um único filtro individual.")

    with st.form(key="consulta_direta_cfi_form"):
        cfi_input = st.text_input(
            "CFI",
            key="input_cfi_direto",
            help="Informe o código CFI para busca direta no catálogo.",
        )
        submit_busca = st.form_submit_button("Consultar catálogo CFI")

    if submit_busca:
        cfi_limpo = (cfi_input or "").strip()
        if not cfi_limpo:
            st.error("Informe o CFI para a consulta direta.")
            return

        base = {
            "data_hora": datetime.now().isoformat(sep=" ", timespec="seconds"),
            "ncm": "",
            "cfi": cfi_limpo,
            "cst": "",
            "status": "pendente",
            "resultado": "Consulta direta por CFI em andamento.",
        }
        st.session_state["fluxo_cfi"] = {
            "base": base,
            "filtros": {
                "cfi": cfi_limpo,
            },
            "consulta": None,
            "busca_realizada": False,
            "refino_habilitado": False,
            "consulta_refino": None,
            "busca_refino_realizada": False,
        }
        st.session_state["resultado_final_cfi"] = None

        if is_cfi_api_configured():
            st.info("Consultando Catálogo CFI do BNDES...")
            consulta = buscar_produto_cfi(**st.session_state["fluxo_cfi"]["filtros"])
            st.session_state["fluxo_cfi"]["consulta"] = consulta
            st.session_state["fluxo_cfi"]["busca_realizada"] = True
        else:
            missing = get_cfi_config_errors()
            st.warning(
                "Integração CFI não configurada. Variáveis faltantes: " + ", ".join(missing)
            )
            st.info("Veja o arquivo MODELO_INTEGACAO_BNDES.md para instruções de configuração.")

    fluxo = st.session_state.get("fluxo_cfi")
    if not fluxo:
        return

    base = fluxo.get("base", {})
    consulta = fluxo.get("consulta")
    resultado_final = st.session_state.get("resultado_final_cfi")

    if resultado_final:
        mostrar_resultado_final(resultado_final)
        if st.button("Reiniciar análise", key="btn_resetar_analise_cfi"):
            resetar_fluxo_cfi()
        return

    if not fluxo.get("busca_realizada", False):
        st.caption("Aguardando consulta ao catálogo CFI para avançar na decisão.")
        return

    if not consulta:
        st.warning("Não foi possível concluir sem consulta ao catálogo CFI.")
        return

    if consulta.get("success"):
        quantidade = consulta.get("quantidade", 0)
        st.success(f"{quantidade} produto(s) encontrado(s) no catálogo CFI.")

        with st.expander("Detalhes dos produtos encontrados"):
            if consulta.get("data"):
                df_cfi = pd.DataFrame(consulta["data"])
                st.dataframe(df_cfi, width='stretch')
            else:
                st.info("Nenhum produto encontrado com os critérios informados.")

        if quantidade > 0:
            corresponde, itens_correspondentes = selecionar_itens_correspondentes(
                consulta.get("data", []),
                "selecao_correspondencia_cfi",
            )

            if corresponde:
                if st.button("Concluir análise", key="btn_concluir_consulta_direta_com_correspondencia"):
                    final = construir_resultado_final(
                        base,
                        status="financiavel",
                        resultado="Financiável pelo FNE.",
                        justificativa=f"Bem correspondente encontrado no catálogo CFI em consulta direta. Itens confirmados pelo usuário: {len(itens_correspondentes)}.",
                    )
                    final["itens_selecionados"] = resumir_itens_para_relatorio(itens_correspondentes)
                    final["quantidade_itens_confirmados"] = len(itens_correspondentes)
                    adicionar_historico(final)
                    st.session_state["resultado_final_cfi"] = final
                    st.rerun()
            else:
                st.warning("O CFI consultado não corresponde ao bem analisado. Escolha uma das opções de pesquisa abaixo.")
                st.session_state["fluxo_cfi"]["refino_habilitado"] = True
        else:
            st.warning("Nenhum item foi encontrado para o CFI informado.")
            st.info("Escolha uma das opções de pesquisa abaixo para continuar a análise.")
            st.session_state["fluxo_cfi"]["refino_habilitado"] = True
    else:
        st.warning("Falha na consulta ao catálogo CFI.")
        st.error(consulta.get("error", "Erro desconhecido"))
        with st.expander("Detalhes técnicos"):
            st.write(f"Status HTTP: {consulta.get('status_code', 'N/A')}")
            st.write(f"Keyword usado: {consulta.get('keyword', 'N/A')}")
            st.write(f"URL: {consulta.get('url', 'N/A')}")

    fluxo = st.session_state.get("fluxo_cfi")
    if not fluxo or not fluxo.get("refino_habilitado"):
        return

    st.markdown("#### Próxima etapa da pesquisa")
    opcao_refino = st.radio(
        "Escolha uma opção de pesquisa:",
        options=[
            "Pesquisar todos os bens com o mesmo NCM do CFI",
            "Pesquisar por filtro individual (apenas um filtro)",
        ],
        key="radio_acao_pos_consulta_cfi",
    )

    if opcao_refino == "Pesquisar todos os bens com o mesmo NCM do CFI":
        ncms_disponiveis = extrair_ncms_da_consulta(consulta)

        if not ncms_disponiveis:
            st.warning("Não foi possível identificar o NCM do CFI consultado para executar esta opção.")
        else:
            if len(ncms_disponiveis) == 1:
                ncm_refino = ncms_disponiveis[0]
                st.info(f"NCM identificado para pesquisa: {ncm_refino}")
            else:
                ncm_refino = st.selectbox(
                    "Selecione o NCM para pesquisar todos os bens:",
                    options=ncms_disponiveis,
                    key="select_ncm_refino_cfi",
                )

            if st.button("Consultar bens por NCM", key="btn_consultar_refino_ncm_cfi"):
                if is_cfi_api_configured():
                    st.info("Consultando Catálogo CFI por NCM...")
                    consulta_refino = buscar_produto_cfi(ncm=ncm_refino, quantidade=500)
                    base = fluxo.get("base", {})
                    base["ncm"] = ncm_refino
                    st.session_state["fluxo_cfi"]["base"] = base
                    st.session_state["fluxo_cfi"]["consulta_refino"] = consulta_refino
                    st.session_state["fluxo_cfi"]["busca_refino_realizada"] = True
                    st.session_state["fluxo_cfi"]["tipo_refino"] = "ncm"
                    st.session_state["fluxo_cfi"]["descricao_refino"] = f"NCM: {ncm_refino}"
                else:
                    missing = get_cfi_config_errors()
                    st.warning(
                        "Integração CFI não configurada. Variáveis faltantes: " + ", ".join(missing)
                    )
                    st.info("Veja o arquivo MODELO_INTEGACAO_BNDES.md para instruções de configuração.")
    else:
        with st.form(key="consulta_direta_cfi_refino_form"):
            opcoes_filtro = {
                "Nome": "nome",
                "Modelo": "modelo",
                "Marca": "marca",
                "CNPJ": "cnpj",
            }
            campo_escolhido = st.selectbox(
                "Filtro individual",
                options=list(opcoes_filtro.keys()),
                key="tipo_filtro_individual_cfi",
                help="Escolha apenas um filtro para pesquisa global no catálogo (sem restrição por NCM).",
            )
            valor_filtro = st.text_input(
                "Valor do filtro",
                key="valor_filtro_individual_cfi",
            )
            submit_refino = st.form_submit_button("Consultar por filtro individual")

        if submit_refino:
            campo_api = opcoes_filtro[campo_escolhido]
            termo_limpo = (valor_filtro or "").strip()
            if not termo_limpo:
                st.error("Informe o valor do filtro individual para pesquisar.")
                return

            if campo_api == "cnpj":
                termo_limpo = apenas_digitos(termo_limpo)
                if not termo_limpo:
                    st.error("Informe um CNPJ válido para o filtro individual.")
                    return

            if is_cfi_api_configured():
                st.info(f"Consultando Catálogo CFI por {campo_escolhido} (busca global, sem limitação por NCM)...")
                consulta_refino = consultar_cfi_por_campo_cache(campo_api, termo_limpo, quantidade=500)
                base = fluxo.get("base", {})
                # No filtro individual, a busca deve ser global no catálogo e sem ancoragem por NCM.
                base["ncm"] = ""
                st.session_state["fluxo_cfi"]["base"] = base
                st.session_state["fluxo_cfi"]["consulta_refino"] = consulta_refino
                st.session_state["fluxo_cfi"]["busca_refino_realizada"] = True
                st.session_state["fluxo_cfi"]["tipo_refino"] = "filtro_individual"
                st.session_state["fluxo_cfi"]["descricao_refino"] = f"{campo_escolhido}: {termo_limpo}"
            else:
                missing = get_cfi_config_errors()
                st.warning(
                    "Integração CFI não configurada. Variáveis faltantes: " + ", ".join(missing)
                )
                st.info("Veja o arquivo MODELO_INTEGACAO_BNDES.md para instruções de configuração.")

    fluxo = st.session_state.get("fluxo_cfi")
    if not fluxo.get("busca_refino_realizada", False):
        return

    consulta_refino = fluxo.get("consulta_refino")
    base = fluxo.get("base", {})
    if not consulta_refino:
        st.warning("Não foi possível concluir a busca refinada no catálogo CFI.")
        return

    if consulta_refino.get("success"):
        quantidade_refino = consulta_refino.get("quantidade", 0)
        st.success(f"{quantidade_refino} produto(s) encontrado(s) na busca refinada.")
        st.caption(f"Filtro aplicado: {fluxo.get('descricao_refino', 'não informado')}")

        with st.expander("Detalhes dos produtos encontrados na busca refinada"):
            if consulta_refino.get("data"):
                df_cfi_refino = pd.DataFrame(consulta_refino["data"])
                st.dataframe(df_cfi_refino, width='stretch')
            else:
                st.info("Nenhum produto encontrado com os filtros de refinamento.")

        if quantidade_refino > 0:
            corresponde_refino, itens_correspondentes_refino = selecionar_itens_correspondentes(
                consulta_refino.get("data", []),
                "selecao_correspondencia_refino",
            )

            if st.button("Concluir análise do refinamento", key="btn_concluir_refino_cfi"):
                if corresponde_refino:
                    final = construir_resultado_final(
                        base,
                        status="financiavel",
                        resultado="Financiável pelo FNE.",
                        justificativa=f"Bem correspondente encontrado no catálogo CFI após refinamento. Itens confirmados pelo usuário: {len(itens_correspondentes_refino)}.",
                    )
                    final["itens_selecionados"] = resumir_itens_para_relatorio(itens_correspondentes_refino)
                    final["quantidade_itens_confirmados"] = len(itens_correspondentes_refino)
                else:
                    final = construir_resultado_final(
                        base,
                        status="financiavel_condicionado",
                        resultado="Financiável se inexistente similar nacional.",
                        justificativa="CFI e bens sem correspondência após refinamento; analisar se o NCM não é passível de credenciamento e/ou se o CST inicia com 6 ou 7.",
                    )

                adicionar_historico(final)
                st.session_state["resultado_final_cfi"] = final
                st.rerun()
        else:
            if st.button("Concluir análise do refinamento", key="btn_concluir_refino_sem_resultado_cfi"):
                final = construir_resultado_final(
                    base,
                    status="financiavel_condicionado",
                    resultado="Financiável se inexistente similar nacional.",
                    justificativa="CFI e bens não encontrados após refinamento; analisar se o NCM não é passível de credenciamento e/ou se o CST inicia com 6 ou 7.",
                )
                adicionar_historico(final)
                st.session_state["resultado_final_cfi"] = final
                st.rerun()
    else:
        st.warning("Falha na consulta refinada ao catálogo CFI.")
        st.error(consulta_refino.get("error", "Erro desconhecido"))
        detalhes_erro = consulta_refino.get("details") or consulta_refino.get("errors")
        if detalhes_erro:
            with st.expander("Detalhes técnicos da busca multicampo"):
                st.write(detalhes_erro)


def renderizar_historico():
    st.markdown("### Histórico de Consultas")
    historico = carregar_historico(HISTORY_PATH)
    if historico:
        df = pd.DataFrame(historico)
        if "tipo_consulta" not in df.columns:
            df["tipo_consulta"] = df.apply(
                lambda row: (
                    "Consulta por NCM"
                    if str(row.get("ncm", "")).strip()
                    else (
                        "Consulta direta por CFI"
                        if str(row.get("cfi", "")).strip()
                        else "Consulta"
                    )
                ),
                axis=1,
            )
        colunas = [
            coluna
            for coluna in ["data_hora", "tipo_consulta", "ncm", "cfi", "status", "resultado"]
            if coluna in df.columns
        ]
        st.dataframe(df[colunas], width='stretch')
    else:
        st.info("Nenhuma análise ainda. Faça uma consulta para gerar histórico.")


def main():
    st.set_page_config(page_title="Análise Financiabilidade FNE", layout="centered")
    aplicar_tema_visual()
    renderizar_cabecalho()
    inicializar_estado_fluxo()

    opcao = st.radio(
        "Escolha uma opção:",
        options=["NCM", "CFI", "Histórico"],
        horizontal=True,
        key="menu_principal",
        label_visibility="collapsed",
    )

    if opcao == "NCM":
        renderizar_consulta_ncm()
    elif opcao == "CFI":
        renderizar_consulta_direta_cfi()
    else:
        renderizar_historico()

    st.markdown("</div>", unsafe_allow_html=True)


if __name__ == '__main__':
    main()
