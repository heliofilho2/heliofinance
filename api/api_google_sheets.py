"""
API FastAPI para expor dados do Google Sheets para o app Flutter
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
from pathlib import Path
import sys
import json

# Criar arquivo de credenciais a partir de variável de ambiente (Railway)
creds_json = os.getenv('GOOGLE_CREDENTIALS')
if creds_json:
    # Railway: criar arquivo temporário
    creds_path = '/tmp/google-credentials.json'
    os.makedirs('/tmp', exist_ok=True)
    with open(creds_path, 'w') as f:
        f.write(creds_json)
    os.environ['GOOGLE_CREDENTIALS_PATH'] = creds_path
    print(f"✅ Credenciais criadas a partir de variável de ambiente: {creds_path}")
elif not os.getenv('GOOGLE_CREDENTIALS_PATH'):
    # Desenvolvimento local: usar arquivo padrão
    default_path = Path(__file__).parent.parent / 'google-credentials.json'
    if default_path.exists():
        os.environ['GOOGLE_CREDENTIALS_PATH'] = str(default_path)
        print(f"✅ Usando credenciais locais: {default_path}")

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Carregar variáveis de ambiente do arquivo .env
try:
    from dotenv import load_dotenv
    # Carregar .env do diretório raiz do projeto
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
    else:
        # Tentar carregar .env do diretório atual
        load_dotenv()
except ImportError:
    # python-dotenv não instalado, continuar sem ele
    pass

from services.google_sheets_breno import GoogleSheetsBreno
from services.report_service import ReportService
from services.alert_service import AlertService
from services.categorization_service import CategorizationService

app = FastAPI(title="Breno Finance API")

# CORS para Flutter
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuração
SPREADSHEET_ID = "1zK0xBqbcS_05eloUPnTn0k-B3mMYdnk8rjWek5YNSuI"

def get_sheets_service():
    """Inicializa serviço Google Sheets"""
    try:
        # Tentar obter do .env ou variável de ambiente
        creds_path = os.getenv('GOOGLE_CREDENTIALS_PATH')
        
        # Se não estiver configurado, tentar usar o arquivo padrão na raiz
        if not creds_path:
            default_path = Path(__file__).parent.parent / 'google-credentials.json'
            if default_path.exists():
                creds_path = str(default_path)
                print(f"✅ Usando arquivo de credenciais padrão: {creds_path}")
            else:
                raise ValueError(
                    "GOOGLE_CREDENTIALS_PATH não configurado e arquivo padrão não encontrado.\n"
                    "Configure a variável de ambiente GOOGLE_CREDENTIALS_PATH ou crie um arquivo .env com:\n"
                    "GOOGLE_CREDENTIALS_PATH=google-credentials.json"
                )
        
        if not os.path.exists(creds_path):
            raise FileNotFoundError(f"Arquivo de credenciais não encontrado: {creds_path}")
        
        return GoogleSheetsBreno(SPREADSHEET_ID, creds_path)
    except Exception as e:
        import traceback
        error_msg = f"Erro ao inicializar Google Sheets: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        raise


# Models
class StatusResponse(BaseModel):
    saldo: float
    gasto_diario: float
    entrada: float
    saida: float
    diario_total: float
    performance: float
    limite_diario: float
    semaforo: str
    status: str
    status_text: str


class RelatorioSemanalResponse(BaseModel):
    periodo: Dict[str, str]
    top_5_gastos: List[Dict[str, Any]]
    economia_vs_previsto: float
    total_previsto: float
    total_real: float
    performance_semana: float
    total_entrada: float
    total_saida: float
    tendencia_dias: List[Dict[str, Any]]


class RelatorioMensalResponse(BaseModel):
    mes_atual: Dict[str, Any]
    mes_anterior: Dict[str, Any]
    comparativo: Dict[str, Any]
    insights: List[str]


class AlertaResponse(BaseModel):
    tipo: str
    prioridade: str
    titulo: str
    mensagem: str
    emoji: str


class ProjecaoMensal(BaseModel):
    mes: int
    ano: int
    nome_mes: str
    entrada_prevista: float
    saida_prevista: float
    diario_previsto: float
    performance_prevista: float
    saldo_inicial: float
    saldo_final: float
    negativo: bool


class AlertaProjecao(BaseModel):
    mes: str
    ano: int
    saldo_projetado: float
    severidade: str
    mensagem: str


class ProjecaoResponse(BaseModel):
    sucesso: bool
    saldo_atual: float
    mes_atual: str
    ano_atual: int
    projecoes: List[ProjecaoMensal]
    alertas: List[AlertaProjecao]
    total_alertas: int
    meses_projetados: int
    erro: Optional[str] = None


# Endpoints
@app.get("/")
async def root():
    return {"message": "Breno Finance API", "version": "1.0.0"}


@app.get("/api/status")
async def get_status():
    """Retorna status financeiro atual"""
    try:
        service = get_sheets_service()
        status = service.obter_status_atual()
        
        # Verificar se há erro no retorno
        if 'erro' in status:
            raise HTTPException(status_code=500, detail=status['erro'])
        
        # Garantir que todos os campos necessários existem
        required_fields = {
            'saldo': 0.0,
            'gasto_diario': 0.0,
            'entrada': 0.0,
            'saida': 0.0,
            'diario_total': 0.0,
            'performance': 0.0,
            'limite_diario': 0.0,
            'semaforo': '🟢',
            'status': 'ok',
            'status_text': 'Status não disponível'
        }
        
        for field, default_value in required_fields.items():
            if field not in status:
                status[field] = default_value
        
        return status
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_detail = f"{str(e)}\n\nTraceback:\n{traceback.format_exc()}"
        print(f"ERRO em /api/status: {error_detail}")  # Log no console
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/relatorio/semanal", response_model=RelatorioSemanalResponse)
async def get_relatorio_semanal():
    """Retorna relatório semanal"""
    try:
        service = get_sheets_service()
        report_service = ReportService(service)
        relatorio = report_service.gerar_relatorio_semanal()
        
        if not relatorio.get('sucesso'):
            raise HTTPException(status_code=500, detail=relatorio.get('erro'))
        
        return RelatorioSemanalResponse(**relatorio)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/relatorio/mensal", response_model=RelatorioMensalResponse)
async def get_relatorio_mensal(mes: Optional[int] = None, ano: Optional[int] = None):
    """Retorna relatório mensal"""
    try:
        service = get_sheets_service()
        report_service = ReportService(service)
        relatorio = report_service.gerar_relatorio_mensal(mes, ano)
        
        if not relatorio.get('sucesso'):
            raise HTTPException(status_code=500, detail=relatorio.get('erro'))
        
        return RelatorioMensalResponse(**relatorio)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/alertas", response_model=List[AlertaResponse])
async def get_alertas():
    """Retorna alertas ativos"""
    try:
        service = get_sheets_service()
        alert_service = AlertService(service)
        alertas = alert_service.verificar_alertas()
        return [AlertaResponse(**a) for a in alertas]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/categorias")
async def get_categorias():
    """Retorna lista de categorias"""
    try:
        categorization = CategorizationService()
        return {"categorias": categorization.listar_categorias()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/projecao", response_model=ProjecaoResponse)
async def get_projecao(meses: int = 6):
    """Retorna projeção de saldo futuro baseado em valores previstos"""
    try:
        if meses < 1 or meses > 12:
            meses = 6
        
        service = get_sheets_service()
        projecao = service.calcular_projecao_futura(meses_futuros=meses)
        
        if not projecao.get('sucesso'):
            return ProjecaoResponse(
                sucesso=False,
                saldo_atual=0.0,
                mes_atual="",
                ano_atual=0,
                projecoes=[],
                alertas=[],
                total_alertas=0,
                meses_projetados=0,
                erro=projecao.get('erro', 'Erro desconhecido')
            )
        
        # Converter projeções para modelos
        projecoes_model = [
            ProjecaoMensal(**p) for p in projecao.get('projecoes', [])
        ]
        
        # Converter alertas para modelos
        alertas_model = [
            AlertaProjecao(**a) for a in projecao.get('alertas', [])
        ]
        
        return ProjecaoResponse(
            sucesso=True,
            saldo_atual=projecao.get('saldo_atual', 0.0),
            mes_atual=projecao.get('mes_atual', ''),
            ano_atual=projecao.get('ano_atual', 0),
            projecoes=projecoes_model,
            alertas=alertas_model,
            total_alertas=len(alertas_model),
            meses_projetados=meses
        )
    except Exception as e:
        import traceback
        error_detail = f"{str(e)}\n\nTraceback:\n{traceback.format_exc()}"
        print(f"ERRO em /api/projecao: {error_detail}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/transacao")
async def criar_transacao(tipo: str, valor: float, descricao: str):
    """Cria uma nova transação"""
    try:
        service = get_sheets_service()
        
        if tipo.lower() == 'gasto':
            result = service.registrar_gasto_diario(valor, descricao)
        elif tipo.lower() == 'entrada':
            result = service.registrar_entrada(valor, descricao)
        elif tipo.lower() == 'saida':
            result = service.registrar_saida_fixa(valor, descricao)
        else:
            raise HTTPException(status_code=400, detail="Tipo inválido. Use: gasto, entrada ou saida")
        
        if not result.get('sucesso'):
            raise HTTPException(status_code=500, detail=result.get('erro'))
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/projecao", response_model=ProjecaoResponse)
async def get_projecao(meses: int = 6):
    """Retorna projeção de saldo futuro baseado em valores previstos"""
    try:
        if meses < 1 or meses > 12:
            meses = 6
        
        service = get_sheets_service()
        projecao = service.calcular_projecao_futura(meses_futuros=meses)
        
        if not projecao.get('sucesso'):
            return ProjecaoResponse(
                sucesso=False,
                saldo_atual=0.0,
                mes_atual="",
                ano_atual=0,
                projecoes=[],
                alertas=[],
                total_alertas=0,
                meses_projetados=0,
                erro=projecao.get('erro', 'Erro desconhecido')
            )
        
        # Converter projeções para modelos
        projecoes_model = [
            ProjecaoMensal(**p) for p in projecao.get('projecoes', [])
        ]
        
        # Converter alertas para modelos
        alertas_model = [
            AlertaProjecao(**a) for a in projecao.get('alertas', [])
        ]
        
        return ProjecaoResponse(
            sucesso=True,
            saldo_atual=projecao.get('saldo_atual', 0.0),
            mes_atual=projecao.get('mes_atual', ''),
            ano_atual=projecao.get('ano_atual', 0),
            projecoes=projecoes_model,
            alertas=alertas_model,
            total_alertas=len(alertas_model),
            meses_projetados=meses
        )
    except Exception as e:
        import traceback
        error_detail = f"{str(e)}\n\nTraceback:\n{traceback.format_exc()}"
        print(f"ERRO em /api/projecao: {error_detail}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
