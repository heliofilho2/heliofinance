"""
Rotas para integração com Google Sheets
"""
import os
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.database import get_db
from services.google_sheets_service import GoogleSheetsService

router = APIRouter()

# ID da planilha (da URL)
SPREADSHEET_ID = "1zK0xBqbcS_05eloUPnTn0k-B3mMYdnk8rjWek5YNSuI"


class SyncRequest(BaseModel):
    month: Optional[int] = None
    year: Optional[int] = None


@router.post("/google-sheets/sync")
def sync_to_google_sheets(request: SyncRequest, db: Session = Depends(get_db)):
    """
    Sincroniza transações do banco para Google Sheets
    """
    try:
        credentials_path = os.getenv('GOOGLE_CREDENTIALS_PATH')
        if not credentials_path:
            raise HTTPException(
                status_code=400,
                detail="GOOGLE_CREDENTIALS_PATH não configurado. Configure as credenciais do Google."
            )
        
        service = GoogleSheetsService(
            spreadsheet_id=SPREADSHEET_ID,
            credentials_path=credentials_path
        )
        
        result = service.sync_transactions_to_sheet(
            db=db,
            month=request.month,
            year=request.year
        )
        
        if result['success']:
            return result
        else:
            raise HTTPException(status_code=500, detail=result['message'])
            
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Arquivo de credenciais não encontrado. Configure GOOGLE_CREDENTIALS_PATH."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao sincronizar: {str(e)}")


@router.get("/google-sheets/test")
def test_google_sheets_connection():
    """
    Testa conexão com Google Sheets
    """
    try:
        credentials_path = os.getenv('GOOGLE_CREDENTIALS_PATH')
        if not credentials_path:
            return {
                "success": False,
                "message": "GOOGLE_CREDENTIALS_PATH não configurado"
            }
        
        service = GoogleSheetsService(
            spreadsheet_id=SPREADSHEET_ID,
            credentials_path=credentials_path
        )
        
        # Tentar ler primeira linha
        data = service.get_sheet_data("A1:E1")
        
        return {
            "success": True,
            "message": "Conexão com Google Sheets OK",
            "sample_data": data
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Erro: {str(e)}"
        }
