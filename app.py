import json
import os
from datetime import datetime

import pandas as pd
import streamlit as st

from cfi_api import buscar_produto_cfi, get_cfi_config_errors, is_cfi_api_configured
from report import gerar_relatorio_pdf


ROOT = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(ROOT, "NCMspassíveisdeCFI.csv")
HISTORY_PATH = os.path.join(ROOT, "history.json")


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

    adicionar_historico(analise)
    return analise


def main():
    st.set_page_config(page_title="Análise Financiabilidade FNE", layout="centered")
    st.title("Análise de Financiabilidade FNE")

    st.markdown("### 1) Entrada de dados")
    with st.form(key="analise_form"):
        ncm_input = st.text_input("NCM (8 dígitos)")
        cfi_input = st.text_input("CFI (opcional)")
        cst_input = st.text_input("CST (opcional)")
        nome_input = st.text_input("Nome do Bem (opcional)")
        marca_input = st.text_input("Marca (opcional)")
        modelo_input = st.text_input("Modelo (opcional)")
        cnpj_input = st.text_input("CNPJ do fabricante (opcional)")
        submit = st.form_submit_button("Analisar")

    if submit:
        res = analisar_ncm(ncm_input, cfi_input, cst_input)

        if res.get("status") == "erro":
            st.error(res["mensagem"])
        else:
            st.success(res["resultado"])
            st.json(res)

            if st.button("Gerar relatório PDF"):
                filename = f"relatorio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                out_path = os.path.join(ROOT, filename)
                gerar_relatorio_pdf(res, out_path)
                st.success(f"Relatório gerado: {filename}")
                st.download_button("Download PDF", data=open(out_path, "rb"), file_name=filename, mime="application/pdf")

            if is_cfi_api_configured():
                st.info("🔍 Consultando Catálogo CFI do BNDES...")
                consulta = buscar_produto_cfi(
                    ncm=ncm_input,
                    cfi=cfi_input,
                    nome=nome_input,
                    modelo=modelo_input,
                    marca=marca_input,
                    cnpj=cnpj_input,
                )
                if consulta.get("success"):
                    st.success(f"✅ {consulta.get('quantidade', 0)} produtos encontrados no catálogo CFI")
                    
                    with st.expander("📊 Detalhes dos produtos encontrados"):
                        if consulta.get("data"):
                            df_cfi = pd.DataFrame(consulta["data"])
                            st.dataframe(df_cfi, use_container_width=True)
                        else:
                            st.info("Nenhum produto encontrado com os critérios informados.")
                    
                    st.json(consulta)
                else:
                    st.warning("⚠️ Falha na consulta ao Catálogo CFI")
                    st.error(consulta.get("error", "Erro desconhecido"))
                    
                    with st.expander("🔧 Detalhes técnicos"):
                        st.write(f"**Status HTTP:** {consulta.get('status_code', 'N/A')}")
                        st.write(f"**Keyword usado:** {consulta.get('keyword', 'N/A')}")
                        st.write(f"**URL:** {consulta.get('url', 'N/A')}")
            else:
                missing = get_cfi_config_errors()
                st.warning(
                    "🔧 Integração CFI não configurada. Variáveis faltantes: " + ", ".join(missing)
                )
                st.info("📝 Veja o arquivo `MODELO_INTEGACAO_BNDES.md` para instruções de configuração.")

    st.markdown("### 2) Histórico de análises")
    historico = carregar_historico(HISTORY_PATH)
    if historical := historico:
        df = pd.DataFrame(historical)
        st.dataframe(df)
    else:
        st.info("Nenhuma análise ainda. Faça uma consulta para gerar histórico.")


if __name__ == '__main__':
    main()
