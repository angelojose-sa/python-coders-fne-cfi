@echo off
REM Script para iniciar o app de análise FNE com integração CFI BNDES
cd /d "%~dp0"
set BNDES_CFI_API_BASE_URL=https://ws.bndes.gov.br/cfi_catalogo/
python -m streamlit run app.py --server.port 8505 --server.headless true
pause