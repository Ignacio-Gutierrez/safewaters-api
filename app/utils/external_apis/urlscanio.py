"""
Módulo para interactuar con la API de URLScan.io.

Basado en la documentación oficial de URLScan.io v1 y utiliza modelos Pydantic
para validación de datos.
"""
from app.config import settings
import httpx
from app.schemas.urls_check import URLResponse
from app.utils.external_api_models.urlscanio_model import URLScanioResponse
from typing import Optional

URLSCANIO_API_URL = settings.URLSCANIO_API_URL
URLSCANIO_API_KEY = settings.URLSCANIO_API_KEY

# Whitelist básica de dominios verificados como seguros
SAFE_DOMAINS = {
    'google.com', 'github.com', 'microsoft.com', 'apple.com',
    'amazon.com', 'facebook.com', 'twitter.com', 'linkedin.com',
    'stackoverflow.com', 'mozilla.org', 'wikipedia.org'
}

def _is_whitelisted(domain: str) -> bool:
    """Verifica si el dominio está en whitelist"""
    domain_clean = domain.lower().strip()
    
    # Verificar dominio exacto
    if domain_clean in SAFE_DOMAINS:
        return True
        
    # Verificar subdominios de dominios seguros
    for safe_domain in SAFE_DOMAINS:
        if domain_clean.endswith(f'.{safe_domain}'):
            return True
            
    return False

def _analyze_scan_results(urlscanio_response: URLScanioResponse, domain: str) -> URLResponse:
    """
    Analiza los resultados de scans para determinar si es malicioso.
    Basado en la documentación oficial de URLScan.io.
    """
    results = urlscanio_response.results
    
    if not results:
        return URLResponse(
            domain=domain,
            malicious=False,
            info=f"Dominio '{domain}' no encontrado en URLScan.io.",
            source="URLScan.io"
        )
    
    malicious_count = 0
    suspicious_count = 0
    total_scans = min(len(results), 3)  # Analizar máximo 3 scans más recientes
    worst_score = 0
    
    for result in results[:total_scans]:
        verdicts = result.verdicts
        
        if verdicts:
            # Usar el campo malicious directo si está disponible
            if verdicts.malicious is True:
                malicious_count += 1
            
            # Analizar score (-100 a 100, según documentación)
            score = verdicts.score or 0
            if score > worst_score:
                worst_score = score
            
            # Considerar sospechoso si score > 25
            if score > 25:
                suspicious_count += 1
    
    # Determinar veredicto final
    malicious_ratio = malicious_count / total_scans if total_scans > 0 else 0
    
    if malicious_ratio >= 0.5:  # 50% o más scans maliciosos
        return URLResponse(
            domain=domain,
            malicious=True,
            info=f"Dominio '{domain}' marcado como malicioso en {malicious_count}/{total_scans} scans recientes (score: {worst_score})",
            source="URLScan.io"
        )
    
    elif malicious_count > 0:  # Al menos uno malicioso
        return URLResponse(
            domain=domain,
            malicious=True,
            info=f"Dominio '{domain}' tiene indicadores sospechosos ({malicious_count} maliciosos de {total_scans} scans, score: {worst_score})",
            source="URLScan.io"
        )
    
    elif worst_score > 50:  # Score alto sin flag malicious explícito
        return URLResponse(
            domain=domain,
            malicious=True,
            info=f"Dominio '{domain}' con score alto de maliciosidad: {worst_score}",
            source="URLScan.io"
        )
    
    else:  # Limpio o mayormente limpio
        return URLResponse(
            domain=domain,
            malicious=False,
            info=f"Dominio '{domain}' no presenta indicadores de peligro en {total_scans} scan(s) analizados (score: {worst_score})",
            source="URLScan.io"
        )

async def check_urlscanio(domain: str) -> URLResponse:
    """
    Consulta URLScan.io usando la API de búsqueda pública y modelos Pydantic.
    
    Args:
        domain (str): El dominio a consultar en URLScan.io.
        
    Returns:
        URLResponse: Resultado de la verificación con información del dominio.
    """
    # 1. Verificar whitelist básica
    if _is_whitelisted(domain):
        return URLResponse(
            domain=domain,
            malicious=False,
            info=f"Dominio '{domain}' está en whitelist de sitios verificados como seguros.",
            source="URLScan.io"
        )

    headers = {
        "API-Key": URLSCANIO_API_KEY
    }

    try:
        # 2. Buscar scans existentes usando API pública
        async with httpx.AsyncClient(timeout=15.0) as client:
            search_url = f"{URLSCANIO_API_URL}/search/"
            params = {
                "q": f"domain:{domain}",
                "size": 3  # Solo los más recientes
            }
            
            response = await client.get(search_url, params=params, headers=headers)
            response.raise_for_status()
            
            # Usar el modelo Pydantic para validar la respuesta
            response_json = response.json()
            urlscanio_response = URLScanioResponse.model_validate(response_json)
            
            # 3. Analizar resultados
            return _analyze_scan_results(urlscanio_response, domain)
        
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            return URLResponse(
                domain=domain,
                malicious=False,
                info="Error de autenticación con URLScan.io: API-Key inválida o expirada",
                source="URLScan.io"
            )
        elif e.response.status_code == 403:
            return URLResponse(
                domain=domain,
                malicious=False,
                info="Error de autorización con URLScan.io: Acceso denegado",
                source="URLScan.io"
            )
        elif e.response.status_code == 429:
            return URLResponse(
                domain=domain,
                malicious=False,
                info="Límite de rate de URLScan.io excedido, intente más tarde",
                source="URLScan.io"
            )
        else:
            return URLResponse(
                domain=domain,
                malicious=False,
                info=f"Error HTTP {e.response.status_code} de URLScan.io: {e.response.text[:100]}",
                source="URLScan.io"
            )
    except Exception as e:
        return URLResponse(
            domain=domain,
            malicious=False,
            info=f"Error consultando URLScan.io: {str(e)}",
            source="URLScan.io"
        )
