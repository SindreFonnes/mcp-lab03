---
marp: true
theme: default
paginate: true
backgroundColor: #1e1e1e
color: #ffffff
header: 'AI Agent Workshop - Model Context Protocol'
footer: 'Leif Terje Fonnes & Lars Søraas | Mars 2026'
style: |
  section {
    font-size: 24px;
    line-height: 1.3;
    padding: 40px;
  }
  h1 {
    font-size: 42px;
    margin-bottom: 0.4em;
    margin-top: 0.2em;
  }
  h2 {
    font-size: 32px;
    margin-bottom: 0.3em;
    margin-top: 0.2em;
  }
  h3 {
    font-size: 28px;
    margin-bottom: 0.2em;
    margin-top: 0.2em;
  }
  li {
    margin-bottom: 0.2em;
  }
  code {
    font-size: 18px;
  }
  pre {
    font-size: 16px;
    line-height: 1.2;
    margin: 0.5em 0;
  }
  ul, ol {
    margin: 0.5em 0;
  }
  .columns {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 1rem; /* Adds space between columns */
  }
---

<!-- 
_class: lead
_color: black _color: black
-->

# AI Agent Workshop
## AI Agenter med Model Context Protocol (MCP)

**Leif Terje Fonnes og Lars Søraas**  
*13 Mars - Booster 2026*

![bg](https://www.publicdomainpictures.net/pictures/180000/velka/paper-and-a-pencil-14671851619PA.jpg)

---

# 🎯 Læringsmål

- **Forstå** MCP arkitektur og konsepter
- **Bygge** din egen AI agent med verktøy
- **Utvide** systemet med nye funksjoner
- **Deploye** ved hjelp av Docker containere
- **Lære** beste praksis for produksjon

![bg ](https://images.unsplash.com/photo-1589395937658-0557e7d89fad?fm=jpg&q=60&w=3000&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D)

---
<!-- 
_color: black _color: black
-->

# Agenda

1. **Introduksjon til MCP og AI Agenter**
2. **Arkitektur Oversikt**
3. **Etablere Utviklingsmiljø**
4. **MCP Arkitektur Recap**
5. **Hands-on**
8. **Avanserte Funksjoner**
9. **Forbedringer**
10. **Oppsummering & Ressurser**


![bg](https://www.publicdomainpictures.net/pictures/180000/velka/paper-and-a-pencil-14671851619PA.jpg)

---

<!-- _class: lead -->
# Hva er Model Context Protocol (MCP)?

![bg right](https://plus.unsplash.com/premium_photo-1678216285973-466494c8c707?fm=jpg&q=60&w=3000&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D)

---
# Men først litt kontekst - hva er egentlig en AI agent?

<div class="columns">
<div>

## En agent er "_noe_" som kan:
- Forstå brukerforespørsler
- Gi kontekstuelle svar
- Lære og tilpasse seg over tid
- Utføre handlinger via verktøy
- Hente sanntidsdata og ressurser
</div>
<div>

## For å få til dette trenger den
- Resonnering
  - Planlegge, ta beslutninger
- Minne
  - Huske, ha kunnskap
- Tilgang til den virkelige verden
  - Sanse, føle, handle
</div>
</div>

## MCP gir tilgang til verktøy og data på en standardisert måte!

---

# MCP

###  **Protokoll** for å sende meldinger mellom AI og verktøy
- **Transport**: Hvilke kanaler som brukes (HTTP, stdio, WebSocket)

- **Verkøydefinisjon**: Hvordan verktøy beskrives og oppdages
- **Ressurser**: Tilgang til data og dokumenter
- **Prompts**: Gjenbrukbare prompt templates

#### https://modelcontextprotocol.io/specification/2025-11-25 + https://modelcontextprotocol.io/docs/getting-started/intro

![bg right](https://images.unsplash.com/photo-1764185800646-f75f7e16e465?q=80&w=870)

---

<!-- _class: lead -->
# Arkitektur

## Hvordan henger det hele sammen?
### Workshop

![bg right](https://images.unsplash.com/photo-1554793000-245d3a3c2a51?fm=jpg&q=60&w=3000&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D)

---
# Systemarkitektur


## 🌐 **Web Grensesnitt**
- Enkelt HTML frontend for testing
- Sanntids interaksjon med agent


## 🤖 **AI Agent** 
- Prosesserer brukerforespørsler med OpenAI
- Kaller MCP verktøy når nødvendig
- Håndterer "samtale minne"

## 🖥️ **MCP Server**
- Huser verktøy for agenten
- Gjør verktøy tilgjengelig via MCP standard
- Håndterer ekstern API og ressurs integrasjon

![w:500 bg right](https://res.cloudinary.com/duiwgrncm/image/upload/v1769337120/overordnet_1_xxnp4q.png)

---
# Deployment

- Hver komponent kjører i egen Docker container
- Host eksponerer 8080 (Web) og 8001 (Agent API), og 8000 (MCP Server API)
- Log og data deles via volum

![w:500 bg right](https://res.cloudinary.com/duiwgrncm/image/upload/v1769296308/docker-ws_hsahin.png)

---
# Dataflyt

## Oppstart

![h:16cm bg](https://res.cloudinary.com/duiwgrncm/image/upload/v1769353979/oppstart_1_dqqr1a.png)

---
# Dataflyt

## Forespørsel

![h:16cm bg](https://res.cloudinary.com/duiwgrncm/image/upload/v1769337313/dataflyt_1_p11d46.png)

---

<!-- _class: lead -->
# Etablere utviklingmiljø for workshop

![bg opacity:.3](https://res.cloudinary.com/duiwgrncm/image/upload/v1769355942/walkator-klMii3cR9iI-unsplash_xxqclo.jpg)

---

# Utviklingsmiljø for workshop

## 1. Logg inn på din Github konto
## 2. Lag en *fork* av https://github.com/zral/mcp-lab03
## 3. Kryss av **Copy the main branch only**
## 4. Velg **Code / Codespaces / Create Codespace on...**
## 5. Kopier **env.example** til **.env** i Codespace
## Du har nå et fiks ferdig utviklingsmiljø!

---

# API nøkkel OpenAI GPT-4.1-mini
## Denne trenger du for å få tilgang til en LLM (værdata bruker yr.no - ingen nøkkel nødvendig)
<p></p>

## 1. Gå til https://github.com/marketplace/models
## 2. Velg **OpenAI GPT-4o-mini / Use this model / Create Personal Access Token**
## 3. Kopier tokenet - husk - du kan _ikke_ få se det på nytt
## 4. Åpne **.env** filen i Codespaces og legg tokenet inn i placeholderen for ```OPENAI_API_KEY```
## 5. Værdata hentes fra yr.no (api.met.no) - ingen API-nøkkel nødvendig
---

<!-- _class: lead -->
# Før vi går igang - recap og presiseringer

![bg opacity:.3](https://res.cloudinary.com/duiwgrncm/image/upload/v1769355942/walkator-klMii3cR9iI-unsplash_xxqclo.jpg)

---

# MCP Arkitektur

## Dynamisk Tools Discovery
- **Agent henter tools automatisk** fra MCP server ved oppstart
- **Ingen hardkoding** av verktøydefinisjon i agent-kode
- **MCP standard** for tools exchange

## Enklere utvikling
- **Kun endre MCP server** for å legge til nye verktøy
- **Agent restarter automatisk** med nye tools
- **Løs kobling** mellom komponenter

## Skalerbarhet
- **Flere MCP servere** kan eksponere forskjellige verktøy
- **Plugin arkitektur** for nye funksjonalitet

https://modelcontextprotocol.io/specification/2025-11-25/server/tools

---

# MCP Standard 2025-11-25
## WS følger standarden men med noen forenklinger for læring

<div class="columns" >
<div>

### 1. ✅ **JSON-RPC 2.0 Protokoll**
- ✅ Implementert `tools/list` og `tools/call`
- ✅ Bruker standardiserte JSON-RPC meldinger
- ⚠️ Kan utvides med notifikasjoner og kansellering

### 2. **Fler transport-protokoller**
- ✅ **HTTP**: Allerede støttet
- 📝 **stdio**: For CLI integrasjon
- 📝 **HTTP SSE**: For streaming
- 📝 **WebSocket**: For sanntids-kommunikasjon
</div>
<div>

### 3. **Forenkle - Bruk MCP SDK**
- Python: `mcp` pakke fra modelcontextprotocol
- TypeScript: `@modelcontextprotocol/sdk`
- Forenkler håndtering av transport og protokoller
- MERK: Vår JSON-RPC implementasjon følger standarden og er kompatibel!

### 4. **Utvid med fler MCP kapabiliteter**
- **Resources**: Tilgang til data og dokumenter
- **Prompts**: Gjenbrukbare prompt templates
- **Sampling**: LLM sampling requests
</div>

---

<!-- _class: lead -->
# Hands-on: Utforske koden

![bg opacity:.3](https://res.cloudinary.com/duiwgrncm/image/upload/v1769355942/walkator-klMii3cR9iI-unsplash_xxqclo.jpg)

---


# Prosjektstruktur

```
./
├── docker-compose.yml        # 🐳 Container orkestrering (bruk: docker compose)
├── .env.example              # 🔐 Miljøvariabler (kopier til .env)
└── services/ 
    ├── mcp-server/          # 🔧 MCP Server
    │   ├── app.py           # ⭐ JSON-RPC 2.0 endpoint
    │   ├── Dockerfile       # 🐳 Container image
    │   └── requirements.txt
    ├── agent/               # 🤖 AI Agent
    │   ├── app.py           # ⭐ OpenAI & MCP Server integration
    │   ├── conversation_memory.py       # 🧠 Samtale-minne
    │   ├── Dockerfile
    │   └── requirements.txt
    ├── web/                  # 🌐 Frontend
    │   ├── app.py            # ⭐ Enkel webserver
    │   ├── Dockerfile
    │   └── templates/
    ├── mcp-sdk-client/       # ✅ Compliance test
    │   ├── test_mcp_sdk.py
    │   ├── Dockerfile
    │   └── requirements.txt
    └── shared/               # 📦 Delte ressurser
```

---

# Agent - Hente tools fra MCP server

```python
# services/agent/app.py

# Tools hentes dynamisk fra MCP server ved oppstart via JSON-RPC
async def load_tools_from_mcp_server(self):
    """Hent tilgjengelige tools fra MCP server via JSON-RPC."""
    jsonrpc_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list"
    }
    response = await self.http_client.post(
        f"{self.mcp_server_url}/message",
        json=jsonrpc_request
    )
    jsonrpc_response = response.json()
    mcp_tools = jsonrpc_response["result"]

    # Konverter fra MCP format til OpenAI function calling format
    for tool in mcp_tools.get("tools", []):
        openai_tool = {
            "type": "function",
            "function": {
                "name": tool["name"],
                "description": tool["description"],
                "parameters": tool["inputSchema"]
            }
        }
        self.tools.append(openai_tool)
```

---
# MCP Server - Tools-manifest

```json
{
  "tools": [
    {
      "name": "get_weather_forecast",
      "title": "Weather Forecast Provider",
      "description": "Hent værprognose for en destinasjon...",
      "inputSchema": {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "properties": {
          "location": {
            "type": "string",
            "description": "Navn på by eller lokasjon"
          }
        },
        "required": ["location"],
        "additionalProperties": false
      },
      "outputSchema": {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "properties": {
          "location": { "type": "object" },
          "current": { "type": "object" },
          "forecast": { "type": "array" }
        }
      }
    }
  ]
}
```

---

# 🔄 JSON-RPC 2.0 Protokoll

### MCP Message handler - JSON-RPC
```python
# MCP Server: JSON-RPC message handler
@app.post("/message")
async def handle_jsonrpc(request: JSONRPCRequest):
    if request.method == "tools/list":
        return JSONRPCResponse(id=request.id, result={"tools": [...]})
    elif request.method == "tools/call":
        tool_name = request.params["name"]
        arguments = request.params["arguments"]
        result = await handle_tools_call(tool_name, arguments)
        return JSONRPCResponse(id=request.id, result=result)
```

### Agent kaller med JSON-RPC
```python
# Agent: Kall tools/call via JSON-RPC
jsonrpc_request = {
    "jsonrpc": "2.0",
    "id": 2,                # Unik ID per kall
    "method": "tools/call",
    "params": {
        "name": "get_weather_forecast",
        "arguments": {"location": "Oslo"}
    }
}
response = await http_client.post("/message", json=jsonrpc_request)
result = response.json()["result"]
```

---

# Flyt - Verktøykall

```python
# Når OpenAI vil bruke et verktøy
if response_message.tool_calls:
    for tool_call in response_message.tool_calls:
        tool_name = tool_call.function.name
        tool_args = json.loads(tool_call.function.arguments)
        
        # Kall MCP server
        tool_result = await self.call_mcp_tool(tool_name, tool_args)
        
        # Legg til resultat i samtalen
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": json.dumps(tool_result)
        })
```

---

<!-- _class: lead -->
# Hands-on: Bygging av verktøy

![bg opacity:.3](https://res.cloudinary.com/duiwgrncm/image/upload/v1769355942/walkator-klMii3cR9iI-unsplash_xxqclo.jpg)

---

# Labøvelse 1: Utforsk nåværende verktøy

## La oss undersøke værverktøyet og den nye MCP arkitekturen

```bash
# Start systemet
docker compose up -d

# Test tools/list - se tilgjengelige verktøy (JSON-RPC)
curl -X POST "http://localhost:8000/message" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}' | python3 -m json.tool

# Test tools/call - kall værverktøy direkte (JSON-RPC)
curl -X POST "http://localhost:8000/message" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
      "name": "get_weather_forecast",
      "arguments": {"location": "Oslo"}
    }
  }'

# Test via agent (agent bruker JSON-RPC internt)
curl -X POST "http://localhost:8001/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Hva er været i Bergen?"}'
```

---

# Labøvelse 2: Legg til nytt verktøy - Tilfeldig fakta

### Steg 1: Legg til faktum-endpoint i MCP Server

<div style="font-size: small;">

```python
# I services/mcp-server/app.py

async def get_random_fact(category: str = "general") -> Dict[str, Any]:
    """Få et tilfeldig interessant faktum."""
    try:
        facts = {
            "general": ["Honningbien produserer mat spist av mennesker.",
                       "Bananer er bær, men jordbær er ikke det."],
            "space": ["En dag på Venus er lengre enn året sitt.",
                     "Saturn ville flyte i vann."]
        }
        
        import random
        fact = random.choice(facts.get(category, facts["general"]))
        
        result = {
            "category": category,
            "fact": fact,
            "timestamp": datetime.now().isoformat()
        }
        
        return result
        
    except Exception as e:
        logger.error(f"Fact retrieval error: {e}")
        return {"error": f"Kunne ikke hente faktum: {str(e)}"}
```
</div>

---

# Labøvelse 2: Oppdater tools manifest

### Steg 2: Legg til i tools listen (JSON-RPC compliant)

<div style="font-size: small;">

```python
# I services/mcp-server/app.py, oppdater handle_tools_list():

async def handle_tools_list() -> Dict[str, Any]:
    tools = [
        {
            "name": "get_weather_forecast",
            "title": "Weather Forecast Provider",
            "description": "Hent værprognose for en destinasjon",
            "inputSchema": { /* ... */ }
        },
        {
            "name": "get_random_fact",
            "title": "Random Fact Provider",
            "description": "Få et tilfeldig interessant faktum",
            "inputSchema": {
                "$schema": "https://json-schema.org/draft/2020-12/schema",
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "Faktakategori (general, space)",
                        "enum": ["general", "space"]
                    }
                },
                "required": ["category"],
                "additionalProperties": False
            }
        }
    ]
    return {"tools": tools}
```

</div>

---
# Labøvelse 2: Håndter verktøykall

### Steg 3: Legg til routing i handle_tools_call()

```python
# I handle_tools_call(), legg til:

elif tool_name == "get_random_fact":
    category = arguments.get("category", "general")
    
    result = await get_random_fact(category)
    
    if "error" in result:
        return {
            "content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False)}],
            "isError": True
        }
    
    return {
        "content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}],
        "structuredContent": result,
        "isError": False
    }
```
---

# Labøvelse 2: Test det nye verktøyet

### Steg 4: JSON-RPC Compliance Testing

```bash
# Build på nytt (agent henter tools ved oppstart)
docker compose build mcp-server travel-agent
docker compose up -d

# Test tools/list med JSON-RPC
curl -X POST "http://localhost:8000/message" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}' | python3 -m json.tool

# Test tools/call for å hente faktum (space kategori)
curl -X POST "http://localhost:8000/message" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
      "name": "get_random_fact",
      "arguments": {"category": "space"}
    }
  }' | python3 -m json.tool

# Test det nye verktøyet via agent
curl -X POST "http://localhost:8001/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Fortell meg et interessant faktum om verdensrommet"}'
```

---

# Forventet resultat

**Når du kjører disse kommandoene skal du se:**
- ✅ `tools/list` returnerer både `get_weather_forecast` og `get_random_fact`
- ✅ `tools/call` for `get_random_fact` returnerer en JSON response
- ✅ Agent kan bruke både værverktøy og faktaverktøy i samme samtale

---

# Labøvelse 2.5: Validering - Flere verktøy sammen

**Test at agenten kan bruke begge verktøyene i samme spørsmål:**

```bash
curl -X POST "http://localhost:8001/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Hva er været i Oslo og fortell meg et faktum om verdensrommet"}'
```

Agenten skal nå automatisk:
1. Hente værdata for Oslo
2. Hente et faktum om verdensrommet
3. Kombinere svarene i ett svar

---

# Labøvelse 3: API integrasjon - https://newsapi.org


<div class="columns">
<div>

### Nå skal du bruke **alt** du har lært så langt og legge til et ekte Nyhets-API

Koden du kan bruke ser du på høyre side. 

- I tillegg må det lages manifest og routing for verktøyet.
- API nøkkel må legges til i .env filen som NEWS_API_KEY.
- Til slutt test med JSON-RPC eller Curl og via agenten.

</div>
<div>

```python
# I services/mcp-server/app.py - Legg til i handle_tools_call()

async def get_news(topic: str, language: str = "no") -> Dict[str, Any]:
    """Få nylige nyheter om et emne via NewsAPI."""
    api_key = os.getenv("NEWS_API_KEY")
    if not api_key:
        return {
            "isError": True,
            "content": [{"type": "text", "text": "NEWS_API_KEY ikke konfigurert"}]
        }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://newsapi.org/v2/everything",
                params={
                    "q": topic,
                    "language": language,
                    "apiKey": api_key
                },
                timeout=10.0
            )
        
        news_data = response.json()
        articles = [
            {"title": article["title"], "url": article["url"]}
            for article in news_data.get("articles", [])[:3]
        ]
        
        return {
            "isError": False,
            "content": [{
                "type": "text",
                "text": f"Nyeste nyheter om '{topic}':\n\n" + 
                        "\n".join([f"- {a['title']}\n  {a['url']}" for a in articles])
            }]
        }
    except Exception as e:
        return {
            "isError": True,
            "content": [{"type": "text", "text": f"Feil ved henting av nyheter: {str(e)}"}]
        }
```

## Legg til i handle_tools_list()
```python
{
    "name": "get_news",
    "description": "Hent nyeste nyheter om et emne",
    "inputSchema": {
        "type": "object",
        "properties": {
            "topic": {"type": "string", "description": "Emne å søke etter"},
            "language": {"type": "string", "description": "Språkkode (f.eks. 'no', 'en')"}
        },
        "required": ["topic"]
    }
}
```

</div>
</div>
---

<!-- _class: lead -->
# 🐳 Deployment & Test

---

# Docker compose kommandoer

## Utviklingsarbeidsflyt

```bash
# Start fra bunnen av
docker compose up --build

# Stopp alt
docker compose down

# Bygg spesifikk tjeneste på nytt
docker compose build mcp-server

# Se logger
docker compose logs -f travel-agent

# Sjekk helse
curl http://localhost:8000/health
```

---

# Miljøoppsett

## 1. Kopier miljøfil
```bash
cp .env.example .env
```

## 2. Legg til API nøkler
```bash
# .env
OPENAI_API_KEY=your-openai-api-key-here
# Værdata bruker yr.no (api.met.no) - ingen API-nøkkel nødvendig
NEWS_API_KEY=your-news-api-key-here  # Hvis du bruker news verktøy
```

## 3. Bygg og start
```bash
docker compose up --build
```

---

# Teststrategi

## 1. Enhetstesting (Individuelle verktøy)
```bash
# Test MCP server tools/call direkte via JSON-RPC
curl -X POST "http://localhost:8000/message" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "get_weather_forecast",
      "arguments": {"location": "Oslo"}
    }
  }'

# Test Labøvelse 3: get_news verktøy
curl -X POST "http://localhost:8000/message" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
      "name": "get_news",
      "arguments": {"topic": "Python", "language": "en"}
    }
  }'
```

## 2. Integrasjonstesting (Full flyt)
```bash
# Test gjennom agent
curl -X POST "http://localhost:8001/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Hva er de nyeste nyhetene om AI?"}'
```

## 3. Webtesting
Åpne http://localhost:8080 i nettleser

---

# Tips - Debugging

## Vanlige problemer & løsninger

### 🔴 **Container vil ikke starte**
```bash
docker compose logs service-name
```

### 🔴 **API kall feiler**
```bash
docker compose exec travel-agent env | grep API
```

### 🔴 **Verktøy ikke gjenkjent**
```bash
curl http://localhost:8001/health
```

---

<!-- _class: lead -->
# Avanserte Funksjoner

![bg opacity:.3](https://res.cloudinary.com/duiwgrncm/image/upload/v1769355942/walkator-klMii3cR9iI-unsplash_xxqclo.jpg)

---

# Avanserte MCP Verktøy Konsepter

<div class="columns">
<div>

### 1. **Verktøy med tilstand** (Stateful Tools)
- **Brukerpreferanser**: Husk temperaturenhet, språk, lokasjon
- **Samtalehistorie**: Se tidligere spørsmål og svar
- **Sesjonshåndtering**: Autentisering, autorisering
- **Eksempel**: Weather tool husker at bruker bruker Celsius

### 2. **Asynkrone operasjoner** (Async/Polling)
- **Langvarige oppgaver**: API kall som tar lang tid
- **Bakgrunnsprosessering**: Datahenting eller beregning
- **Polling/Callbacks**: Sjekk status på jobb
- **Eksempel**: Bestille rapport → motta status-ID → polle for resultat
</div>
<div>

## 3. **Flertrinns arbeidsflyt** (Orchestration)
- **Verktøy-kjeding**: Tool A gir output til Tool B
- **Betinget logikk**: "Hvis værvarsel dårlig, sjekk alternativer"
- **Feilhåndtering**: Retry ved timeout, fallback-alternativer
- **Eksempel**: Hent vær → finn attraksjoner → bestill aktivitet
</div>
</div>

---

# Sikkerhetsbetraktninger

## Inputvalidering
```python
from pydantic import BaseModel, validator

class SecureRequest(BaseModel):
    location: str
    
    @validator('location')
    def validate_location(cls, v):
        if len(v) > 100:
            raise ValueError('Lokasjon for lang')
        # Legg til mer validering...
        return v
```

## Håndtering - API nøkler 
```python
import os

def get_api_key(service: str) -> str:
    key = os.getenv(f"{service.upper()}_API_KEY")
    if not key:
        raise ValueError(f"Mangler {service} API nøkkel")
    return key
```

---

# Deployment - Produksjon

## Skalerbarhet
- **Lastbalansering** med flere agent instanser
- **Database clustering** for samtale minne
- **Caching** for ofte brukte verktøy-resultater

## Overvåkning
- **Helse sjekker** og oppetid overvåkning
- **Logging aggregering** (ELK stack)
- **Metrics innsamling** (Prometheus/Grafana)
- **Feilsporing** (Sentry)

## Sikkerhet
- **API rate limiting**
- **Input sanitisering**
- **HTTPS terminering**
- **Håndtering av hemmeligheter**

---

# Utvidelse av arkitektur

## Legg til nye funksjoner

### 🧠 **Minne**
- Vektor databaser for semantisk søk
- Kunnskaps grafer for relasjoner
- Langsiktig læring og tilpasning

### 🔗 **Integrasjon**
- Webhook endepunkter for sanntid oppdateringer
- Meldingskøer for asynkron prosessering
- Hendelsesdrevet arkitektur

### 🌐 **Multi-Modal atøtte**
- Bildeanalyse verktøy
- Lydprosessering
- Tolking av video

---

<!-- _class: lead -->
# Videre arbeid

![bg opacity:.3](https://res.cloudinary.com/duiwgrncm/image/upload/v1769355942/walkator-klMii3cR9iI-unsplash_xxqclo.jpg)

---

# Øvelse 1: Værforbedring
**Vanskelighet: Nybegynner**

Forbedre værverktøyet til å inkludere:
- UV-indeks informasjon
- Luftkvalitet data
- Soloppgang/solnedgang tider

**Tips:** yr.no (api.met.no) gir all denne dataen i responsen - uten API-nøkkel!

---

# Øvelse 2: Kalkulatorverktøy
**Vanskelighet: Nybegynner**

Lag et kalkulator verktøy som kan:
- Utføre grunnleggende matematiske operasjoner
- Håndtere komplekse uttrykk
- Vise steg-for-steg løsninger

```python
# Verktøy idé
@app.post("/tools/calculate")
async def calculate(request: CalculationRequest):
    # Din implementasjon her
    pass
```

---

# Øvelse 3: Minne-Aktivert Chat
**Vanskelighet: Mellomnivå**

Utvid agenten til å huske:
- Brukerpreferanser (favoritt byer, enheter)
- Tidligere samtaler
- Personaliserte anbefalinger

**Filer å modifisere:**
- `conversation_memory.py`
- Logikk for samtale med agent

---

# Øvelse 4: Orkestrering - Arbeidsflyt
**Vanskelighet: Avansert**

Lag en reiseplanlegging arbeidsflyt:
1. Få vær for destinasjon
2. Finn nærliggende attraksjoner
3. Sjekk kalender tilgjengelighet
4. Send e-post sammendrag

**Krever:** Flere API integrasjoner + arbeidsflyt logikk

---

<!-- _class: lead -->
# Oppsummering

![bg opacity:.3](https://res.cloudinary.com/duiwgrncm/image/upload/v1769355942/walkator-klMii3cR9iI-unsplash_xxqclo.jpg)

---

# Hva du har lært

<div class="columns" >
<div>

## 🧠 **Konsepter**
- Model Context Protocol grunnleggende
- JSON-RPC 2.0 protokoll for verktøy-kommunikasjon
- Dynamisk tool discovery og loading
- AI agent arkitektur mønstre
- Verktøy-basert AI system design

## 🚀 **Beste Praksis**
- Strukturert feilhåndtering og error responses
- Sikkerhetsbetraktninger (input validering, API nøkler)
- Prosjektstruktur og kodeorganisering
- Debugging og logging
</div>
<div>

## 🛠️ **Praktiske Ferdigheter**
- Bygge MCP-kompatible verktøy
- Integrere eksterne APIer sikkert
- Docker containerisering og docker compose orchestration
- Teststrategier
- Conversation memory og stateful agenter

</div>
</div>

---

# Neste Steg

## 📚 **Fortsett å lære**
- Utforsk MCP spesifikasjonen i dybden
- Studer avanserte AI agent mønstre
- Lær om vektor databaser og RAG og integrer med MCP

## 🔧 **Bygg mer**
- Lag industri-spesifikke verktøy
- Implementer produksjon overvåkning
- Skaler til multi-tenant arkitektur

## 🌐 **Community**
- Bli med i MCP utvikler community
- Bidra til open source verktøy
- Del implementasjoner

---

# Ressurser

## 📖 **Dokumentasjon**
- [Model Context Protocol Docs](https://modelcontextprotocol.io/)
- [OpenAI API Reference](https://platform.openai.com/docs/)
- [Docker Compose Guide](https://docs.docker.com/compose/)

## 🛠️ **Verktøy & Biblioteker**
- [FastAPI Dokumentasjon](https://fastapi.tiangolo.com/)
- [Pydantic for Data Validering](https://pydantic-docs.helpmanual.io/)
- [HTTPX for Async HTTP](https://www.python-httpx.org/)

---

<!-- _class: lead -->
# Spørsmål & diskusjon

## Takk for oss!

**Leif Terje Fonnes**
leffen@gmail.com
github.com/leffen

**Lars Søraas**  
lsoraas@gmail.com  
github.com/zral  

![bg opacity:.3](https://res.cloudinary.com/duiwgrncm/image/upload/v1769355942/walkator-klMii3cR9iI-unsplash_xxqclo.jpg)

