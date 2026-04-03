import datetime
from fpdf import FPDF


def gerar_relatorio_pdf(resultado: dict, output_path: str):
    """Gera relatório PDF resumindo o resultado da análise."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Relat\u00f3rio de An\u00e1lise de Financiabilidade FNE", ln=True, align="C")

    pdf.set_font("Arial", "", 12)
    pdf.ln(8)

    pdf.cell(0, 8, f"Data: {datetime.datetime.now().isoformat(sep=' ', timespec='seconds')}", ln=True)

    for chave, valor in resultado.items():
        pdf.ln(4)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(50, 8, f"{chave}", ln=False)
        pdf.set_font("Arial", "", 12)
        pdf.multi_cell(0, 8, str(valor))

    pdf.output(output_path)
    return output_path
