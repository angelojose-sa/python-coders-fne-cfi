@echo off
REM Iniciar o app Streamlit com as credenciais configuradas

echo.
echo ========================================================================
echo APP DE ANALISE DE FINANCIABILIDADE FNE - BNDES CFI
echo ========================================================================
echo.

REM Configurar as credenciais (estas ja estao no arquivo credenciais_api_bdnes.env)
REM Se preferir, descomente as linhas abaixo:
REM set BNDES_CFI_CONSUMER_KEY=dKA3jLkCZuuLBWP3yDQXbCXwj0Ua
REM set BNDES_CFI_CONSUMER_SECRET=VpZxfWkVhAXfzXLgswrawk7Hylga

echo Iniciando Streamlit...
echo Abrira automaticamente em: http://localhost:8505
echo.

cd /d "%~dp0"

REM Instalar dependencias se necessario
python -m pip install -q -r requirements.txt 2>nul

REM Executar app
python -m streamlit run app.py --server.port 8505

pause
