#!/usr/bin/env python3
"""
MCP API Server - LAB02 VERSION with JSON-RPC 2.0

MCP-compliant HTTP server with JSON-RPC 2.0 protocol.
Participants can extend this with their own tools.

✅ MCP 2025-11-25 COMPLIANT:
============================
This server implements the official MCP Streamable HTTP transport:
- JSON-RPC 2.0 message protocol
- POST /message endpoint for all tool operations
- tools/list method for tool discovery
- tools/call method for tool execution
- Proper error codes and responses

Why JSON-RPC?:
- Standard protocol (not custom)
- Easy to test with curl (just add JSON wrapper)
- Production-ready and spec-compliant
- Same complexity as REST but more powerful

For MCP specification, see: https://modelcontextprotocol.io/specification/2025-11-25
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import httpx
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Konfigurer logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="MCP API Server - Lab03",
    description="Forenklet HTTP API for workshop med kun værfunksjonalitet",
    version="1.0.0"
)

# API konstanter
YR_API_BASE = "https://api.met.no/weatherapi/locationforecast/2.0"
YR_USER_AGENT = "IngridReisetjenester/1.0 (workshop-booster26)"
NOMINATIM_API_BASE = "https://nominatim.openstreetmap.org"

# Mapping fra yr.no symbol_code til norske beskrivelser
SYMBOL_CODE_MAP = {
    "clearsky": "klarvær",
    "fair": "lettskyet",
    "partlycloudy": "delvis skyet",
    "cloudy": "skyet",
    "lightrainshowers": "lette regnbyger",
    "rainshowers": "regnbyger",
    "heavyrainshowers": "kraftige regnbyger",
    "lightrainshowersandthunder": "lette regnbyger og torden",
    "rainshowersandthunder": "regnbyger og torden",
    "heavyrainshowersandthunder": "kraftige regnbyger og torden",
    "lightsleetshowers": "lette sluddbyger",
    "sleetshowers": "sluddbyger",
    "heavysleetshowers": "kraftige sluddbyger",
    "lightsnowshowers": "lette snøbyger",
    "snowshowers": "snøbyger",
    "heavysnowshowers": "kraftige snøbyger",
    "lightrain": "lett regn",
    "rain": "regn",
    "heavyrain": "kraftig regn",
    "lightrainandthunder": "lett regn og torden",
    "rainandthunder": "regn og torden",
    "heavyrainandthunder": "kraftig regn og torden",
    "lightsleet": "lett sludd",
    "sleet": "sludd",
    "heavysleet": "kraftig sludd",
    "lightsnow": "lett snø",
    "snow": "snø",
    "heavysnow": "kraftig snø",
    "fog": "tåke",
}

# HTTP klient
http_client = httpx.AsyncClient()

# Request/Response modeller

# JSON-RPC 2.0 modeller
class JSONRPCRequest(BaseModel):
    """JSON-RPC 2.0 request format."""
    jsonrpc: str = "2.0"
    id: Optional[Any] = None  # Kan være string, nummer, eller null
    method: str  # f.eks. "tools/list" eller "tools/call"
    params: Optional[Dict[str, Any]] = None  # Parametere til metoden

class JSONRPCError(BaseModel):
    """JSON-RPC 2.0 error object."""
    code: int  # Standard JSON-RPC feilkoder
    message: str  # Feilmelding
    data: Optional[Any] = None  # Ekstra feildata

class JSONRPCResponse(BaseModel):
    """JSON-RPC 2.0 response format."""
    jsonrpc: str = "2.0"
    id: Optional[Any] = None
    result: Optional[Any] = None  # Suksess resultat
    error: Optional[JSONRPCError] = None  # Feil objekt (eksklusiv med result)

class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    service: str
    timestamp: str

# Startup/shutdown handlers
@app.on_event("startup")
async def startup_event():
    """Initialiser ved oppstart."""
    logger.info("Starting MCP API Server Lab03...")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup ved nedstengning."""
    await http_client.aclose()
    logger.info("MCP API Server Lab03 avsluttet")

def translate_symbol_code(symbol_code: str) -> str:
    """Oversett yr.no symbol_code til norsk beskrivelse."""
    # Fjern _day/_night/_polartwilight suffix
    base = symbol_code.split("_")[0] if "_" in symbol_code else symbol_code
    return SYMBOL_CODE_MAP.get(base, symbol_code)


async def geocode_location(location: str) -> Optional[Dict[str, float]]:
    """Geocode en lokasjon til koordinater."""
    try:
        params = {
            "q": location,
            "format": "json",
            "limit": 1,
            "addressdetails": 1
        }

        response = await http_client.get(
            f"{NOMINATIM_API_BASE}/search",
            params=params,
            headers={"User-Agent": YR_USER_AGENT}
        )
        response.raise_for_status()

        data = response.json()
        if not data:
            return None

        result = data[0]
        return {
            "lat": float(result["lat"]),
            "lon": float(result["lon"])
        }

    except Exception as e:
        logger.error(f"Geocoding error: {e}")
        return None

async def get_weather_forecast(location: str) -> Dict[str, Any]:
    """Hent værprognose for en destinasjon via yr.no (api.met.no)."""
    try:
        # Geocode lokasjon
        coords = await geocode_location(location)
        if not coords:
            return {"error": f"Kunne ikke finne lokasjon: {location}"}

        # Hent yr.no forecast
        yr_url = f"{YR_API_BASE}/compact"
        yr_params = {
            "lat": round(coords["lat"], 4),
            "lon": round(coords["lon"], 4),
        }
        yr_headers = {"User-Agent": YR_USER_AGENT}

        response = await http_client.get(yr_url, params=yr_params, headers=yr_headers)
        response.raise_for_status()
        yr_data = response.json()

        timeseries = yr_data["properties"]["timeseries"]
        if not timeseries:
            return {"error": "Ingen værdata tilgjengelig fra yr.no"}

        # Nåværende vær fra første entry
        now_entry = timeseries[0]
        now_details = now_entry["data"]["instant"]["details"]
        now_symbol = ""
        if "next_1_hours" in now_entry["data"]:
            now_symbol = now_entry["data"]["next_1_hours"]["summary"]["symbol_code"]
        elif "next_6_hours" in now_entry["data"]:
            now_symbol = now_entry["data"]["next_6_hours"]["summary"]["symbol_code"]

        result = {
            "location": {
                "name": location,
                "coordinates": [coords["lat"], coords["lon"]]
            },
            "current": {
                "temperature": round(now_details["air_temperature"]),
                "feels_like": round(now_details["air_temperature"]),  # yr.no har ikke feels_like
                "humidity": round(now_details["relative_humidity"]),
                "description": translate_symbol_code(now_symbol),
                "wind_speed": now_details["wind_speed"],
                "timestamp": now_entry["time"]
            },
            "forecast": []
        }

        # Grupper timeseries etter dag for 5-dagers prognose
        daily_forecasts: Dict[str, Dict[str, Any]] = {}
        today = datetime.fromisoformat(timeseries[0]["time"].replace("Z", "+00:00")).strftime("%Y-%m-%d")

        for entry in timeseries:
            dt = datetime.fromisoformat(entry["time"].replace("Z", "+00:00"))
            date_key = dt.strftime("%Y-%m-%d")

            # Hopp over dagens dato (allerede i current)
            if date_key == today:
                continue

            details = entry["data"]["instant"]["details"]
            temp = details["air_temperature"]

            # Hent symbol_code fra next_1_hours eller next_6_hours
            symbol = ""
            if "next_1_hours" in entry["data"]:
                symbol = entry["data"]["next_1_hours"]["summary"]["symbol_code"]
            elif "next_6_hours" in entry["data"]:
                symbol = entry["data"]["next_6_hours"]["summary"]["symbol_code"]

            if date_key not in daily_forecasts:
                daily_forecasts[date_key] = {
                    "date": date_key,
                    "temp_min": temp,
                    "temp_max": temp,
                    "descriptions": [],
                    "humidity": details["relative_humidity"],
                    "wind_speed": details["wind_speed"]
                }

            daily_forecasts[date_key]["temp_min"] = min(daily_forecasts[date_key]["temp_min"], temp)
            daily_forecasts[date_key]["temp_max"] = max(daily_forecasts[date_key]["temp_max"], temp)
            if symbol:
                daily_forecasts[date_key]["descriptions"].append(translate_symbol_code(symbol))

        # Formater dagsprognose (maks 5 dager)
        for date_key in sorted(daily_forecasts.keys())[:5]:
            day = daily_forecasts[date_key]
            descriptions = day["descriptions"]
            description = max(set(descriptions), key=descriptions.count) if descriptions else "ukjent"
            result["forecast"].append({
                "date": day["date"],
                "temp_min": round(day["temp_min"]),
                "temp_max": round(day["temp_max"]),
                "description": description,
                "humidity": round(day["humidity"]),
                "wind_speed": day["wind_speed"]
            })

        return result

    except Exception as e:
        logger.error(f"Weather forecast error: {e}")
        return {"error": f"Kunne ikke hente væropplysninger: {str(e)}"}

# API Endpoints
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Helse sjekk."""
    return HealthResponse(
        status="healthy",
        service="MCP API Server Lab03",
        timestamp=datetime.now().isoformat()
    )

@app.post("/message")
async def handle_jsonrpc(request: JSONRPCRequest):
    """
    JSON-RPC 2.0 message handler - Hoved-endpoint for MCP kommunikasjon.

    ============================================================================
    WORKSHOP MERKNAD: JSON-RPC 2.0 Message Handler
    ============================================================================

    Dette er HOVEDENDEPOINTET for MCP kommunikasjon.
    Alle MCP operasjoner går gjennom dette endepointet via JSON-RPC 2.0 protokollen.

    HVORFOR JSON-RPC 2.0?
    ---------------------
    - Standard protokoll (ikke proprietær REST)
    - Enkel request/response struktur
    - Konsistent feilhåndtering med standardiserte feilkoder
    - Produksjonsklar (brukt i mange reelle systemer)
    - Lett å teste med curl (bare send JSON)

    JSON-RPC 2.0 REQUEST FORMAT:
    ---------------------------
    {
        "jsonrpc": "2.0",           // Versjon (alltid "2.0")
        "id": 1,                    // Unik ID for request (valgfritt for notifikasjoner)
        "method": "tools/list",     // Metode som skal kalles
        "params": {...}             // Parametere til metoden (valgfritt)
    }

    JSON-RPC 2.0 RESPONSE FORMAT:
    ----------------------------
    Suksess:
    {
        "jsonrpc": "2.0",
        "id": 1,                    // Samme ID som i requesten
        "result": {...}             // Resultat fra metoden
    }

    Feil:
    {
        "jsonrpc": "2.0",
        "id": 1,
        "error": {
            "code": -32601,         // Standard feilkode
            "message": "Method not found",
            "data": {...}           // Ekstra feildetaljer (valgfritt)
        }
    }

    STØTTEDE METODER:
    -----------------
    - "tools/list": Hent liste over tilgjengelige tools (tilsvarer GET /tools)
    - "tools/call": Kall et spesifikt tool (tilsvarer POST /weather etc.)

    STANDARD JSON-RPC FEILKODER:
    ---------------------------
    -32700  Parse error       JSON parsing feilet
    -32600  Invalid Request   Ugyldig JSON-RPC request
    -32601  Method not found  Metoden finnes ikke
    -32602  Invalid params    Ugyldige parametere
    -32603  Internal error    Server intern feil

    TOOLS/LIST EKSEMPEL:
    -------------------
    Request:
    curl -X POST http://localhost:8000/message \\
      -H "Content-Type: application/json" \\
      -d '{
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list"
      }'

    Response:
    {
        "jsonrpc": "2.0",
        "id": 1,
        "result": {
            "tools": [
                {
                    "name": "get_weather_forecast",
                    "description": "...",
                    "inputSchema": {...}
                }
            ]
        }
    }

    TOOLS/CALL EKSEMPEL:
    -------------------
    Request:
    curl -X POST http://localhost:8000/message \\
      -H "Content-Type: application/json" \\
      -d '{
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "get_weather_forecast",
            "arguments": {
                "location": "Oslo, Norway"
            }
        }
      }'

    Response:
    {
        "jsonrpc": "2.0",
        "id": 2,
        "result": {
            "content": [{"type": "text", "text": "..."}],
            "structuredContent": {...},
            "isError": false
        }
    }

    IMPLEMENTASJONSMØNSTER:
    ----------------------
    1. Valider JSON-RPC request format (Pydantic gjør dette)
    2. Route til riktig method handler basert på "method" feltet
    3. Utfør operasjonen
    4. Returner JSON-RPC response med samme ID

    SAMMENLIGNING MED REST:
    ----------------------
    REST (gammel måte):
        GET /tools
        POST /weather {"location": "Oslo"}

    JSON-RPC (ny måte):
        POST /message {"method": "tools/list", ...}
        POST /message {"method": "tools/call", "params": {"name": "get_weather_forecast", ...}}

    Forskjell: Ett endpoint, alle operasjoner. Standard protokoll.

    MCP SPESIFIKASJON:
    ------------------
    https://modelcontextprotocol.io/specification/2025-11-25/basic/transports

    ============================================================================
    """
    try:
        # Valider JSON-RPC versjon
        if request.jsonrpc != "2.0":
            return JSONRPCResponse(
                id=request.id,
                error=JSONRPCError(
                    code=-32600,
                    message="Invalid Request",
                    data="Only JSON-RPC 2.0 is supported"
                )
            )

        # Route til riktig method handler
        if request.method == "tools/list":
            # Hent liste over tilgjengelige tools
            result = await handle_tools_list()
            return JSONRPCResponse(
                id=request.id,
                result=result
            )

        elif request.method == "tools/call":
            # Kall et spesifikt tool
            if not request.params:
                return JSONRPCResponse(
                    id=request.id,
                    error=JSONRPCError(
                        code=-32602,
                        message="Invalid params",
                        data="tools/call requires params with 'name' and 'arguments'"
                    )
                )

            tool_name = request.params.get("name")
            arguments = request.params.get("arguments", {})

            if not tool_name:
                return JSONRPCResponse(
                    id=request.id,
                    error=JSONRPCError(
                        code=-32602,
                        message="Invalid params",
                        data="Missing required parameter: 'name'"
                    )
                )

            result = await handle_tools_call(tool_name, arguments)
            return JSONRPCResponse(
                id=request.id,
                result=result
            )

        else:
            # Ukjent metode
            return JSONRPCResponse(
                id=request.id,
                error=JSONRPCError(
                    code=-32601,
                    message="Method not found",
                    data=f"Unknown method: {request.method}. Supported: tools/list, tools/call"
                )
            )

    except Exception as e:
        # Intern server feil
        logger.error(f"JSON-RPC handler error: {e}")
        return JSONRPCResponse(
            id=request.id if hasattr(request, 'id') else None,
            error=JSONRPCError(
                code=-32603,
                message="Internal error",
                data=str(e)
            )
        )

async def handle_tools_list() -> Dict[str, Any]:
    """
    Handler for tools/list method.
    Returnerer liste over tilgjengelige tools i MCP format.

    ============================================================================
    WORKSHOP MERKNAD: MCP Tools Manifest - Dynamisk Tool Discovery
    ============================================================================

    Dette er NØKKELEN til det dynamiske tool discovery mønsteret.
    Agenten kaller denne metoden via JSON-RPC for å lære hvilke tools som finnes.

    HVORDAN LEGGE TIL ET NYTT TOOL:
    --------------------------------
    1. Legg til tool definition i tools arrayen nedenfor
    2. Legg til routing logikk i handle_tools_call() funksjonen
    3. Restart tjenester: docker compose restart mcp-server travel-agent
    4. Agenten laster automatisk og bruker det nye toolet!

    MCP SPESIFIKASJON FELTER:
    -------------------------
    Krevet av MCP spec:
    - name: Unik identifikator for toolet
    - description: Hva toolet gjør (OpenAI bruker dette)
    - inputSchema: JSON Schema for parametere (JSON Schema 2020-12)

    Valgfritt men anbefalt:
    - title: Menneskelesbart visningsnavn
    - outputSchema: JSON Schema for responsstruktur

    ============================================================================
    """
    tools = [
        {
            "name": "get_weather_forecast",
            "title": "Weather Forecast Provider",
            "description": "Hent værprognose for en destinasjon med nåværende forhold og 5-dagers varsling",
            "inputSchema": {
                "$schema": "https://json-schema.org/draft/2020-12/schema",
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "Navn på by eller lokasjon (f.eks. 'Oslo', 'Bergen', 'New York')"
                    }
                },
                "required": ["location"],
                "additionalProperties": False
            },
            "outputSchema": {
                "$schema": "https://json-schema.org/draft/2020-12/schema",
                "type": "object",
                "properties": {
                    "location": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "coordinates": {
                                "type": "array",
                                "items": {"type": "number"}
                            }
                        }
                    },
                    "current": {
                        "type": "object",
                        "properties": {
                            "temperature": {"type": "number"},
                            "feels_like": {"type": "number"},
                            "humidity": {"type": "number"},
                            "description": {"type": "string"},
                            "wind_speed": {"type": "number"},
                            "timestamp": {"type": "string"}
                        }
                    },
                    "forecast": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "date": {"type": "string"},
                                "temp_min": {"type": "number"},
                                "temp_max": {"type": "number"},
                                "description": {"type": "string"},
                                "humidity": {"type": "number"},
                                "wind_speed": {"type": "number"}
                            }
                        }
                    }
                }
            }
        }
        # LEGG TIL DINE NYE TOOLS HER!
        # Bare kopier strukturen over og tilpass for ditt brukstilfelle
    ]

    return {"tools": tools}

async def handle_tools_call(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handler for tools/call method.
    Router til riktig tool basert på navn.

    Args:
        tool_name: Navn på tool som skal kalles (f.eks. "get_weather_forecast")
        arguments: Argumenter til toolet (f.eks. {"location": "Oslo"})

    Returns:
        MCP tool result format med content, structuredContent, isError
    """
    # Route til riktig tool implementasjon
    if tool_name == "get_weather_forecast":
        # Valider at location parameter finnes
        location = arguments.get("location")
        if not location:
            return {
                "content": [{"type": "text", "text": "Mangler påkrevd parameter: 'location'"}],
                "isError": True
            }

        # Kall værprognose logikken
        result = await get_weather_forecast(location)

        # Sjekk for forretningslogikk feil
        if "error" in result:
            return {
                "content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False)}],
                "isError": True
            }

        # Returner suksess
        return {
            "content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}],
            "structuredContent": result,
            "isError": False
        }

    else:
        # Ukjent tool
        return {
            "content": [{"type": "text", "text": f"Ukjent tool: {tool_name}"}],
            "isError": True
        }

if __name__ == "__main__":
    logger.info("Starting MCP Server API Lab03 on port 8000...")
    uvicorn.run(app, host="0.0.0.0", port=8000)