#!/usr/bin/env python3
"""
Microservice Agent - AI Agent som kaller MCP Server via HTTP

Denne agenten kobler OpenAI GPT med MCP server som kjører som separat tjeneste.

✅ MCP 2025-11-25 COMPLIANT:
============================
Denne agenten kommuniserer med MCP serveren via offisiell JSON-RPC 2.0 protokoll:
- POST /message endpoint for alle operasjoner
- tools/list method for å hente tilgjengelige tools
- tools/call method for å kjøre tools
- Standardisert feilhåndtering med JSON-RPC error codes

Dette er en produksjonsklar implementasjon som følger MCP-spesifikasjonen.
For MCP spec, se: https://modelcontextprotocol.io/specification/2025-11-25
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Dict, Any, List

import httpx
from openai import OpenAI
from conversation_memory import ConversationMemory

# Konfigurer logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global agent instance for API server
agent_instance = None

class MicroserviceAgent:
    """
    AI Agent som bruker MCP server via HTTP API.
    
    Denne agenten:
    1. Håndterer OpenAI API kommunikasjon
    2. Kaller MCP server endpoints i stedet for direkte funksjoner
    3. Administrerer samtalehukommelse
    """
    
    def __init__(self, mcp_server_url: str = None, memory_db_path: str = "/data/conversations.db"):
        # Initialiser OpenAI klient
        # Støtter både GitHub Models (standard for workshop) og OpenAI API
        base_url = os.getenv("OPENAI_BASE_URL", "https://models.github.ai/inference")
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), base_url=base_url)
        logger.info(f"OpenAI client configured with base_url: {base_url}")
        
        # MCP server URL - bruk environment variable hvis tilgjengelig
        if mcp_server_url is None:
            mcp_server_url = os.getenv("MCP_SERVER_URL", "http://mcp-server:8000")
        self.mcp_server_url = mcp_server_url
        
        # Initialiser hukommelse
        self.memory = ConversationMemory(memory_db_path)
        self.current_session_id = None
        
        # HTTP klient for MCP kall
        self.http_client = httpx.AsyncClient()
        
        # Tools vil bli hentet dynamisk fra MCP server
        self.tools = []
        # Tool endpoint mapping lagres separat
        self.tool_endpoints = {}
        
        logger.info("MicroserviceAgent initialisert")
    
    async def load_tools_from_mcp_server(self):
        """
        Hent tilgjengelige tools fra MCP server dynamisk.
        Konverterer fra MCP format til OpenAI function calling format og lagrer endpoint info.

        VIKTIG: Endpoint mappings hentes dynamisk fra MCP server - ingen hardkoding!
        Hver tool kan spesifisere sin egen endpoint og HTTP method.

        ============================================================================
        WORKSHOP MERKNAD: Dynamisk Tool Discovery Pattern
        ============================================================================

        Dette er KJERNEN i det dynamiske tool discovery mønsteret. Å forstå denne
        funksjonen er kritisk for å utvide systemet med nye tools.

        HVORDAN DET VIRKER:
        -------------------
        1. Ved agent oppstart, hent tools manifest fra MCP server via GET /tools
        2. MCP server returnerer JSON med tool definisjoner (navn, beskrivelse, schema)
        3. Konverter hver MCP tool til OpenAI function calling format
        4. Lagre endpoint mappings for senere HTTP kall under tool kjøring
        5. Agenten er nå klar med alle tilgjengelige tools - INGEN KODEENDRINGER NØDVENDIG!

        MCP TOOL FORMAT (fra server):
        {
            "name": "get_weather_forecast",
            "description": "Get weather forecast for a location",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "City name"}
                },
                "required": ["location"]
            },
            "endpoint": "/weather",
            "method": "POST"
        }

        OPENAI FUNCTION FORMAT (konvertert):
        {
            "type": "function",
            "function": {
                "name": "get_weather_forecast",
                "description": "Get weather forecast for a location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {"type": "string", "description": "City name"}
                    },
                    "required": ["location"]
                }
            }
        }

        HVORFOR DETTE ER VIKTIG:
        ------------------------
        - Legg til nye tools i MCP server uten å røre agent koden
        - Agenten oppdager automatisk nye kapasiteter ved oppstart
        - Enkelt å teste forskjellige tool konfigurasjoner (bare mock /tools endpoint)
        - Muliggjør plugin-stil arkitektur for workshops

        PRØV SELV:
        ----------
        1. Legg til et nytt tool endpoint i services/mcp-server/app.py
        2. Legg det til i tools manifest i /tools endpointet
        3. Restart begge tjenestene: docker compose restart mcp-server travel-agent
        4. Agenten vil automatisk laste og bruke ditt nye tool!

        RELATERT KODE:
        --------------
        - MCP Server tools manifest: services/mcp-server/app.py:192-261
        - Tool kjøring: services/agent/app.py:127-194 (call_mcp_tool)
        - OpenAI integrasjon: services/agent/app.py:204-292 (process_query)

        ============================================================================
        """
        try:
            logger.info(f"Henter tools fra MCP server: {self.mcp_server_url}")

            # STEG 1: Hent tools manifest fra MCP server via JSON-RPC
            # Bygg JSON-RPC 2.0 request for tools/list metoden
            jsonrpc_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/list"
            }

            response = await self.http_client.post(
                f"{self.mcp_server_url}/message",
                json=jsonrpc_request
            )
            response.raise_for_status()

            jsonrpc_response = response.json()

            # Sjekk for JSON-RPC feil
            if jsonrpc_response.get("error") is not None:
                error = jsonrpc_response["error"]
                logger.error(f"JSON-RPC feil ved henting av tools: {error.get('message')}")
                return False

            # Ekstraher tools fra JSON-RPC result
            mcp_tools = jsonrpc_response.get("result")
            if mcp_tools is None:
                logger.error("JSON-RPC response mangler 'result' felt")
                return False

            tools_list = mcp_tools.get("tools", [])

            # STEG 2: Konverter MCP format til OpenAI function calling format
            # Vi trenger to datastrukturer:
            # - converted_tools: Liste av OpenAI function definisjoner (for chat completions)
            # - tool_endpoints: Dict som mapper tool navn til HTTP endpoints (for kjøring)
            converted_tools = []
            tool_endpoints = {}

            for tool in tools_list:
                # Konverter MCP tool schema til OpenAI function schema
                # Nøkkelforskjellen: MCP bruker "inputSchema", OpenAI bruker "parameters"
                openai_tool = {
                    "type": "function",
                    "function": {
                        "name": tool["name"],
                        "description": tool["description"],
                        "parameters": tool["inputSchema"]  # Direkte mapping
                    }
                }
                converted_tools.append(openai_tool)

                # STEG 3: Lagre endpoint mapping for senere HTTP kall
                # Når OpenAI kaller dette toolet, må vi vite hvilket endpoint vi skal kalle
                if "endpoint" in tool:
                    tool_endpoints[tool["name"]] = {
                        "endpoint": tool["endpoint"],
                        "method": tool.get("method", "POST")
                    }

            # STEG 4: Lagre til instansvariabler
            # Disse vil bli brukt i process_query() og call_mcp_tool()
            self.tools = converted_tools
            self.tool_endpoints = tool_endpoints
            logger.info(f"Lastet {len(self.tools)} tools fra MCP server med {len(self.tool_endpoints)} endpoint mappings")
            return True

        except Exception as e:
            logger.error(f"Kunne ikke hente tools fra MCP server: {e}")
            # Merk: Agenten fortsetter selv om tools feiler å laste
            # Dette tillater grunnleggende operasjon uten MCP server
            return False
    async def call_mcp_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """
        Kall MCP server via JSON-RPC 2.0 tools/call metode.
        Håndterer MCP-compliant response format med content array og isError flag.

        ============================================================================
        WORKSHOP MERKNAD: MCP Tool Kjøring - Agent til MCP Server Kommunikasjon
        ============================================================================

        Denne funksjonen kalles ETTER at OpenAI har bestemt at et tool er nødvendig.
        Den håndterer JSON-RPC kommunikasjonen mellom Agent og MCP Server.

        KJØRINGSFLYT:
        -------------
        1. OpenAI returnerer: "Jeg må kalle get_weather_forecast med {location: 'Oslo'}"
        2. Denne funksjonen bygger JSON-RPC request med metode "tools/call"
        3. Sender POST http://mcp-server:8000/message med JSON-RPC body
        4. Mottar JSON-RPC response med MCP tool result (content array og structuredContent)
        5. Ekstraherer strukturert data og returnerer det til OpenAI for endelig svar

        MCP RESPONS FORMAT:
        -------------------
        Suksess:
        {
            "content": [{"type": "text", "text": "Oslo weather: 5°C, light rain"}],
            "structuredContent": {
                "location": {"name": "Oslo", "coordinates": [59.9, 10.7]},
                "current": {"temperature": 5, "description": "light rain"},
                "forecast": [...]
            },
            "isError": false
        }

        Feil:
        {
            "content": [{"type": "text", "text": "Location not found"}],
            "isError": true
        }

        HVORFOR TO FORMATER (content + structuredContent)?
        ---------------------------------------------------
        - content: Menneskelesbar tekst for visning (MCP standard)
        - structuredContent: Parset JSON for programmatisk tilgang (vår utvidelse)
        - OpenAI kan bruke structuredContent til bedre å forstå dataen

        JSON-RPC 2.0 TOOLS/CALL REQUEST FORMAT:
        ----------------------------------------
        {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "get_weather_forecast",
                "arguments": {"location": "Oslo"}
            }
        }

        JSON-RPC 2.0 RESPONSE FORMAT:
        ------------------------------
        Suksess:
        {
            "jsonrpc": "2.0",
            "id": 2,
            "result": {
                "content": [...],
                "structuredContent": {...},
                "isError": false
            }
        }

        Feil (JSON-RPC protokoll nivå):
        {
            "jsonrpc": "2.0",
            "id": 2,
            "error": {
                "code": -32602,
                "message": "Invalid params"
            }
        }

        Feil (MCP tool nivå):
        {
            "jsonrpc": "2.0",
            "id": 2,
            "result": {
                "content": [{"type": "text", "text": "Location not found"}],
                "isError": true
            }
        }

        FEILHÅNDTERING:
        ---------------
        Fire typer feil:
        1. JSON-RPC protokoll feil (error objekt i response) -> Ukjent metode, ugyldig params
        2. MCP tool feil (isError: true i result) -> Forretningslogikk feil (lokasjon ikke funnet)
        3. HTTP feil (404, 500) -> Fanges av raise_for_status()
        4. Nettverksfeil (timeout, connection refused) -> Fanges av exception handler

        PRØV SELV:
        ----------
        1. Legg til logging for å se eksakte HTTP requests:
           logger.info(f"HTTP {method} {url} with {arguments}")

        2. Legg til caching for gjentatte tool kall:
           cache_key = f"{tool_name}:{json.dumps(arguments)}"
           if cache_key in self.tool_cache:
               return self.tool_cache[cache_key]

        3. Legg til retry logikk for forbigående feil:
           from tenacity import retry, stop_after_attempt
           @retry(stop=stop_after_attempt(3))
           async def call_with_retry(...):

        RELATERT KODE:
        --------------
        - Tool lasting: services/agent/app.py:59-168 (load_tools_from_mcp_server)
        - MCP server implementasjon: services/mcp-server/app.py:264-310 (/weather endpoint)
        - OpenAI integrasjon: services/agent/app.py:204-292 (process_query)

        MCP SPESIFIKASJON:
        ------------------
        https://modelcontextprotocol.io/specification/2025-11-25/server/tools

        ============================================================================
        """
        try:
            logger.info(f"Kaller MCP server: {tool_name} med args: {arguments}")

            # STEG 1: Bygg JSON-RPC 2.0 request for tools/call metoden
            jsonrpc_request = {
                "jsonrpc": "2.0",
                "id": 2,  # Kan være hvilken som helst unik ID
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                }
            }

            # STEG 2: Send JSON-RPC request til MCP server
            url = f"{self.mcp_server_url}/message"
            logger.info(f"Sender JSON-RPC tools/call request til {url}")

            response = await self.http_client.post(url, json=jsonrpc_request)
            response.raise_for_status()

            jsonrpc_response = response.json()

            # STEG 2a: Sjekk for JSON-RPC protokoll feil
            if jsonrpc_response.get("error") is not None:
                error = jsonrpc_response["error"]
                error_msg = f"JSON-RPC feil {error.get('code')}: {error.get('message')}"
                logger.error(error_msg)
                return json.dumps({"error": error_msg}, ensure_ascii=False)

            # STEG 2b: Ekstraher MCP tool result fra JSON-RPC response
            result = jsonrpc_response.get("result")
            if result is None:
                logger.error("JSON-RPC response mangler 'result' felt")
                return json.dumps({"error": "Mangler result i JSON-RPC response"}, ensure_ascii=False)

            # STEG 3: Parse MCP-compliant respons format
            # MCP spec: https://modelcontextprotocol.io/specification/2025-11-25/server/tools
            # Alle MCP tools MÅ returnere: {content: [...], isError: bool}
            is_error = result.get("isError", False)

            if is_error:
                # STEG 3a: Håndter feilrespons
                # Ekstraher menneskelesbar feilmelding fra content array
                error_text = ""
                for content_item in result.get("content", []):
                    if content_item.get("type") == "text":
                        error_text = content_item.get("text", "")
                        break
                logger.error(f"MCP tool execution error: {error_text}")
                return json.dumps({"error": error_text}, ensure_ascii=False)

            # STEG 3b: Håndter suksessrespons
            # Foretrekk structuredContent for JSON data (vår utvidelse til MCP)
            if "structuredContent" in result:
                return json.dumps(result["structuredContent"], ensure_ascii=False)

            # Fallback: Ekstraher tekst fra content array (MCP standard)
            for content_item in result.get("content", []):
                if content_item.get("type") == "text":
                    return content_item.get("text", "{}")

            return "{}"

        except Exception as e:
            # STEG 4: Håndter nettverk/HTTP feil
            # Dette er IKKE MCP feil, men infrastrukturfeil
            logger.error(f"MCP tool call failed: {e}")
            return json.dumps({"error": str(e)})
    
    def start_new_session(self, session_name: str = None):
        """Start en ny samtalesession."""
        if not session_name:
            session_name = f"Microservice_Session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.current_session_id = self.memory.create_session(session_name)
        logger.info(f"Ny session startet: {self.current_session_id}")
    
    async def process_query(self, query: str) -> str:
        """
        Prosesser brukerforespørsel med AI og MCP verktøy.
        """
        if not self.current_session_id:
            self.start_new_session()
        
        try:
            # Hent samtalehistorikk
            history = self.memory.get_conversation_history(self.current_session_id)
            
            # Bygg meldinger for OpenAI
            messages = [
                {
                    "role": "system",
                    "content": """Du er Ingrid, en vennlig og kompetent agent fra Ingrids Reisetjenester. 

Du kan bruke alle tilgjengelige verktøy.
Du er fra Bergen og elsker regn, og dette passer du på å nevne i samtalen hvis det passer seg.
Utover det, vær vennlig, personlig og hjelpsom - du representerer Ingrids Reisetjenester.
Svar på norsk med mindre brukeren spør på et annet språk.

MERK: Dette er LAB03 versjon med dynamisk tools discovery."""
                }
            ]
            
            # Legg til samtalehistorikk
            for msg in history:
                if msg["role"] == "user":
                    messages.append({"role": "user", "content": msg["content"]})
                elif msg["role"] == "assistant":
                    messages.append({"role": "assistant", "content": msg["content"]})
            
            # Legg til ny brukermelding
            messages.append({"role": "user", "content": query})
            
            # Første AI-kall med OpenAI
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                tools=self.tools,
                tool_choice="auto"
            )
            
            response_message = response.choices[0].message

            # Håndter verktøykall
            tool_calls_made = None
            tool_results = []

            if response_message.tool_calls:
                # Lagre tool calls informasjon
                tool_calls_made = [
                    {
                        "id": tc.id,
                        "type": tc.type,
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in response_message.tool_calls
                ]

                # Legg til assistant melding med tool calls
                messages.append({
                    "role": "assistant",
                    "content": response_message.content,
                    "tool_calls": tool_calls_made
                })

                for tool_call in response_message.tool_calls:
                    function_name = tool_call.function.name
                    arguments = json.loads(tool_call.function.arguments)

                    # Kall MCP server
                    tool_result = await self.call_mcp_tool(function_name, arguments)

                    # Lagre tool result for metadata
                    tool_results.append({
                        "tool": function_name,
                        "arguments": arguments,
                        "result": tool_result[:200] if len(tool_result) > 200 else tool_result  # Trunkert for metadata
                    })

                    messages.append({
                        "role": "tool",
                        "content": tool_result,
                        "tool_call_id": tool_call.id
                    })

                logger.info("Verktøykall fullført, henter endelig svar...")

                # Få endelig svar med OpenAI
                final_response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages
                )

                final_answer = final_response.choices[0].message.content
            else:
                final_answer = response_message.content

            # Lagre samtale med metadata
            user_metadata = {
                "timestamp": datetime.now().isoformat(),
                "query_length": len(query)
            }

            assistant_metadata = {
                "timestamp": datetime.now().isoformat(),
                "model": "gpt-4o-mini",
                "had_tool_calls": tool_calls_made is not None,
                "response_length": len(final_answer),
                "tool_results": tool_results if tool_results else None
            }

            self.memory.add_message(
                self.current_session_id,
                "user",
                query,
                metadata=user_metadata
            )
            self.memory.add_message(
                self.current_session_id,
                "assistant",
                final_answer,
                tool_calls=tool_calls_made,
                metadata=assistant_metadata
            )
            
            return final_answer
            
        except Exception as e:
            logger.error(f"Query processing error: {e}")
            return f"Beklager, jeg fikk en feil: {str(e)}"
    
    async def close(self):
        """Rydd opp ressurser."""
        await self.http_client.aclose()

# Test funksjon
async def main():
    """CLI grensesnitt for testing."""
    agent = MicroserviceAgent()
    
    # Last inn tools fra MCP server
    tools_loaded = await agent.load_tools_from_mcp_server()
    if not tools_loaded:
        logger.warning("Kunne ikke laste tools fra MCP server, fortsetter uten tools")
    
    agent.start_new_session("Test Session")
    
    while True:
        query = input("Du: ").strip()
        if query.lower() in ['quit', 'exit', 'q']:
            break
        
        response = await agent.process_query(query)
        print(f"Ingrid: {response}\n")
    
    await agent.close()

def start_agent_api():
    """Start agent som HTTP API service."""
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel
    from contextlib import asynccontextmanager
    import uvicorn
    
    # Global agent instance - definert på modul nivå
    global agent_instance
    agent_instance = None
    
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Oppstart
        global agent_instance
        logger.info("Starter Ingrid Agent Service...")
        try:
            agent_instance = MicroserviceAgent()

            # Last inn tools fra MCP server
            tools_loaded = await agent_instance.load_tools_from_mcp_server()
            if not tools_loaded:
                logger.warning("Kunne ikke laste tools fra MCP server, fortsetter uten tools")

            agent_instance.start_new_session("HTTP API Session")
            logger.info("Ingrid Agent Service startet")
            logger.info(f"Agent instans opprettet: {agent_instance is not None}")
        except Exception as e:
            logger.error(f"Feilet å starte agent: {e}")
            agent_instance = None

        yield

        # Nedstengning
        if agent_instance:
            await agent_instance.close()
        logger.info("Ingrid Agent Service avsluttet")
    
    # FastAPI app for agent
    agent_app = FastAPI(
        title="Ingrid Agent API",
        description="AI agent service for Ingrids Reisetjenester",
        version="1.0.0",
        lifespan=lifespan
    )
    
    class QueryRequest(BaseModel):
        query: str
    
    class QueryResponse(BaseModel):
        success: bool
        response: str
        timestamp: str
    
    @agent_app.get("/health")
    async def health():
        return {
            "status": "healthy",
            "service": "Ingrid Agent",
            "timestamp": datetime.now().isoformat(),
            "agent_ready": agent_instance is not None
        }
    
    @agent_app.post("/query", response_model=QueryResponse)
    async def process_query_api(request: QueryRequest):
        global agent_instance
        logger.info(f"Query forespørsel mottatt: {request.query}")
        logger.info(f"Agent instans status: {agent_instance is not None}")

        if not agent_instance:
            logger.error("Agent instans er None!")
            raise HTTPException(status_code=503, detail="Agent ikke tilgjengelig")

        try:
            logger.info("Prosesserer query med agent...")
            response = await agent_instance.process_query(request.query)
            logger.info("Query prosessert vellykket")
            return QueryResponse(
                success=True,
                response=response,
                timestamp=datetime.now().isoformat()
            )
        except Exception as e:
            logger.error(f"Query prosessering feil: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    # Start HTTP server
    logger.info("Starter Agent API på port 8001...")
    uvicorn.run(agent_app, host="0.0.0.0", port=8001)

if __name__ == "__main__":
    logger.info("Starter Agent Service på port 8001...")
    start_agent_api()
