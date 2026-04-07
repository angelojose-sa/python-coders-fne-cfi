import datetime
import os
import re

from fpdf import FPDF


ROOT = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.join(ROOT, "modelos", "Logo_do_Banco_do_Nordeste.svg")
LOGO_BRANCO_PATH = os.path.join(ROOT, "modelos", "Logo_do_Banco_do_Nordeste_branco_tmp.svg")

# Paleta institucional BNB
COR_PRIMARIA_BNB = (166, 25, 60)  # #A6193C
PANTONE_194C = (157, 34, 53)
PANTONE_151C = (255, 130, 0)
PANTONE_425C = (84, 88, 90)
COR_TEXTO = (45, 45, 45)


def _obter_logo_para_pdf() -> str:
    """Retorna caminho do logo para o PDF, com tons vermelhos convertidos para branco."""
    if not os.path.exists(LOGO_PATH):
        return LOGO_PATH

    if not LOGO_PATH.lower().endswith(".svg"):
        return LOGO_PATH

    try:
        with open(LOGO_PATH, "r", encoding="utf-8") as f:
            logo_svg = f.read()

        logo_branco = re.sub(r"#A80A35", "#FFFFFF", logo_svg, flags=re.IGNORECASE)
        logo_branco = re.sub(r"#A6193C", "#FFFFFF", logo_branco, flags=re.IGNORECASE)
        logo_branco = re.sub(r"#9D2235", "#FFFFFF", logo_branco, flags=re.IGNORECASE)

        with open(LOGO_BRANCO_PATH, "w", encoding="utf-8") as f:
            f.write(logo_branco)

        return LOGO_BRANCO_PATH
    except Exception:
        return LOGO_PATH


def _texto(valor) -> str:
    if valor is None:
        return ""
    return str(valor).replace("\u2013", "-").replace("\u2014", "-")


class RelatorioBNBPDF(FPDF):
    def header(self):
        self.set_fill_color(*COR_PRIMARIA_BNB)
        self.rect(0, 0, 210, 24, style="F")

        logo_pdf_path = _obter_logo_para_pdf()
        if os.path.exists(logo_pdf_path):
            try:
                self.image(logo_pdf_path, x=10, y=0.5, w=28)
            except Exception:
                pass

        self.set_text_color(255, 255, 255)
        self.set_font("Helvetica", "B", 11)
        self.set_xy(44, 9)
        self.cell(0, 5, "Relatório de Análise de Bens Financiáveis via FNE", ln=True)
        self.ln(14)

    def footer(self):
        self.set_y(-15)
        self.set_draw_color(*PANTONE_425C)
        self.line(10, self.get_y(), 200, self.get_y())
        self.set_text_color(*PANTONE_425C)
        self.set_font("Helvetica", "", 8)
        self.cell(0, 8, f"Página {self.page_no()}", align="R")


def _titulo_secao(pdf: FPDF, titulo: str):
    pdf.ln(2)
    pdf.set_fill_color(*PANTONE_151C)
    pdf.set_text_color(40, 40, 40)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 8, _texto(titulo), ln=True, fill=True)
    pdf.ln(1)


def _linha_campo(pdf: FPDF, rotulo: str, valor: str):
    margem_esquerda = pdf.l_margin
    largura_rotulo = 52
    x_inicial = margem_esquerda
    y_inicial = pdf.get_y()

    # Garante posição consistente para cada linha e evita cursor "herdado"
    # de chamadas anteriores de multi_cell.
    pdf.set_xy(x_inicial, y_inicial)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(*PANTONE_425C)
    pdf.cell(largura_rotulo, 6, _texto(rotulo), ln=False)

    largura_valor = pdf.w - pdf.r_margin - (x_inicial + largura_rotulo)
    if largura_valor < 20:
        largura_valor = 20

    pdf.set_xy(x_inicial + largura_rotulo, y_inicial)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(*COR_TEXTO)
    pdf.multi_cell(largura_valor, 6, _texto(valor) if _texto(valor) else "N/A")
    pdf.set_x(margem_esquerda)


def _renderizar_dados_analise(pdf: FPDF, resultado: dict):
    _titulo_secao(pdf, "Resumo da análise")

    campos = [
        ("Data/Hora", resultado.get("data_hora") or datetime.datetime.now().isoformat(sep=" ", timespec="seconds")),
        ("Status", resultado.get("status", "")),
        ("Resultado", resultado.get("resultado", "")),
        ("Justificativa", resultado.get("justificativa", "")),
        ("NCM", resultado.get("ncm", "")),
        ("CFI", resultado.get("cfi", "")),
        ("CST", resultado.get("cst", "")),
    ]

    for rotulo, valor in campos:
        _linha_campo(pdf, rotulo, valor)


def _renderizar_itens_selecionados(pdf: FPDF, itens: list):
    _titulo_secao(pdf, "Dados do(s) bem(ns) selecionado(s)")

    if not itens:
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(*COR_TEXTO)
        pdf.multi_cell(0, 6, "Nenhum item selecionado para detalhamento.")
        return

    for idx, item in enumerate(itens, start=1):
        if pdf.get_y() > 245:
            pdf.add_page()
            _titulo_secao(pdf, "Dados do(s) bem(ns) selecionado(s)")

        pdf.set_draw_color(*PANTONE_425C)
        pdf.set_fill_color(247, 247, 247)
        y_inicial = pdf.get_y()
        pdf.rect(10, y_inicial, 190, 43, style="DF")
        pdf.set_xy(12, y_inicial + 2)

        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(*PANTONE_194C)
        pdf.cell(0, 6, f"Item {idx}", ln=True)

        _linha_campo(pdf, "Código CFI", item.get("codigoFiname", ""))
        _linha_campo(pdf, "Nome do item", item.get("nomeItem", ""))
        _linha_campo(pdf, "Modelo", item.get("modeloItem", ""))
        _linha_campo(pdf, "Fabricante/Marca", item.get("fabricante", ""))
        _linha_campo(pdf, "CNPJ fabricante", item.get("cnpjFabricante", ""))
        _linha_campo(pdf, "NCM", item.get("numeroNcm", ""))
        _linha_campo(pdf, "Situação cadastral", item.get("posicaoCadastral", ""))

        imagem = _texto(item.get("imagemItem", ""))
        if imagem:
            _linha_campo(pdf, "Imagem (URL)", imagem)

        pdf.ln(3)


def gerar_relatorio_pdf(resultado: dict, output_path: str):
    """Gera relatório PDF com identidade visual BNB e dados detalhados da análise."""
    pdf = RelatorioBNBPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=20)

    try:
        pdf.add_page()
        _renderizar_dados_analise(pdf, resultado)
        _renderizar_itens_selecionados(pdf, resultado.get("itens_selecionados", []))
        pdf.output(output_path)
    finally:
        if os.path.exists(LOGO_BRANCO_PATH):
            try:
                os.remove(LOGO_BRANCO_PATH)
            except Exception:
                pass

    return output_path
