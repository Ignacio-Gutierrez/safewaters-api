"""
Módulo para interactuar con la API de ThreatFox de abuse.ch.

Utiliza modelos Pydantic para validación de datos y manejo de respuestas.
"""
from app.config import settings
import httpx
from app.schemas.urls_check import URLResponse
from app.utils.external_api_models.threatfox_model import ThreatFoxResponse

THREATFOX_API_URL = settings.THREATFOX_API_URL
THREATFOX_API_KEY = settings.THREATFOX_API_KEY

async def check_threatfox(domain: str) -> URLResponse:
    """
    Consulta ThreatFox usando modelos Pydantic para validación de datos.
    
    Args:
        domain (str): El dominio a consultar en ThreatFox.
        
    Returns:
        URLResponse: Resultado de la verificación con información del dominio.
    """
    payload = {
        "query": "search_ioc",
        "search_term": domain
    }

    headers = {
        "Auth-Key": THREATFOX_API_KEY
    }

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                THREATFOX_API_URL,
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            
            # Usar el modelo Pydantic para validar la respuesta
            threatfox_response = ThreatFoxResponse.model_validate(response.json())
            
            if threatfox_response.query_status == "ok" and threatfox_response.data:
                # Buscar IOCs con confianza >= 75 (umbral más conservador para reducir falsos positivos)
                valid_iocs = [ioc for ioc in threatfox_response.data if ioc.confidence_level >= 75]
                
                if valid_iocs:
                    # Seleccionar el IOC con mayor nivel de confianza
                    highest_confidence_ioc = max(valid_iocs, key=lambda x: x.confidence_level)
                    malware_info = f" ({highest_confidence_ioc.malware_printable})" if highest_confidence_ioc.malware_printable else ""
                    return URLResponse(
                        domain=domain,
                        malicious=True,
                        info=f"IOC encontrado: {highest_confidence_ioc.ioc} (Confianza: {highest_confidence_ioc.confidence_level}){malware_info}",
                        source="ThreatFox"
                    )
                
                return URLResponse(
                    domain=domain,
                    malicious=False,
                    info=f"Dominio '{domain}' encontrado pero sin IOCs confiables (>= 75%).",
                    source="ThreatFox"
                )
            
            elif threatfox_response.query_status == "no_result":
                return URLResponse(
                    domain=domain,
                    malicious=False,
                    info=f"Dominio '{domain}' no encontrado en ThreatFox.",
                    source="ThreatFox"
                )
            
            else:
                return URLResponse(
                    domain=domain,
                    malicious=False,
                    info=f"ThreatFox devolvió estado: {threatfox_response.query_status}",
                    source="ThreatFox"
                )

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            return URLResponse(
                domain=domain,
                malicious=False,
                info="Error de autenticación con ThreatFox: Auth-Key inválida o expirada",
                source="ThreatFox"
            )
        elif e.response.status_code == 403:
            return URLResponse(
                domain=domain,
                malicious=False,
                info="Error de autorización con ThreatFox: Acceso denegado",
                source="ThreatFox"
            )
        else:
            return URLResponse(
                domain=domain,
                malicious=False,
                info=f"Error HTTP {e.response.status_code} de ThreatFox: {e.response.text[:100]}",
                source="ThreatFox"
            )
    except Exception as e:
        return URLResponse(
            domain=domain,
            malicious=False,
            info=f"Error consultando ThreatFox: {str(e)}",
            source="ThreatFox"
        )
