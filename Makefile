# MCP Workshop - Development Commands
# ====================================

.PHONY: help up down restart logs status test clean build shell-mcp shell-agent shell-web health curl-list curl-weather curl-agent

# Default target
help: ## Show this help
	@echo "MCP Workshop Commands"
	@echo "====================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ============================================================================
# Docker Compose
# ============================================================================

up: ## Start all services
	docker compose up -d

up-build: ## Start all services with rebuild
	docker compose up -d --build

down: ## Stop all services
	docker compose down

restart: ## Restart all services
	docker compose restart

logs: ## Follow logs from all services
	docker compose logs -f

logs-mcp: ## Follow MCP server logs
	docker compose logs -f mcp-server

logs-agent: ## Follow agent logs
	docker compose logs -f travel-agent

logs-web: ## Follow web logs
	docker compose logs -f web

status: ## Show service status
	@echo "=== Container Status ==="
	@docker compose ps
	@echo ""
	@echo "=== Health Status ==="
	@curl -s http://localhost:8000/health 2>/dev/null && echo " ✓ MCP Server (8000)" || echo " ✗ MCP Server (8000)"
	@curl -s http://localhost:8001/health 2>/dev/null && echo " ✓ Agent (8001)" || echo " ✗ Agent (8001)"
	@curl -s http://localhost:8080/health 2>/dev/null && echo " ✓ Web (8080)" || echo " ✗ Web (8080)"

health: ## Check health of all services
	@echo "MCP Server:"; curl -s http://localhost:8000/health | python3 -m json.tool 2>/dev/null || echo "  Not responding"
	@echo "Agent:"; curl -s http://localhost:8001/health | python3 -m json.tool 2>/dev/null || echo "  Not responding"
	@echo "Web:"; curl -s http://localhost:8080/health | python3 -m json.tool 2>/dev/null || echo "  Not responding"

# ============================================================================
# Development
# ============================================================================

build: ## Build all Docker images
	docker compose build

build-mcp: ## Build MCP server image
	docker compose build mcp-server

build-agent: ## Build agent image
	docker compose build travel-agent

build-web: ## Build web image
	docker compose build web

shell-mcp: ## Open shell in MCP server container
	docker compose exec mcp-server /bin/sh

shell-agent: ## Open shell in agent container
	docker compose exec travel-agent /bin/sh

shell-web: ## Open shell in web container
	docker compose exec web /bin/sh

clean: ## Remove containers, volumes, and images
	docker compose down -v --rmi local
	rm -rf services/agent/data/*.db

# ============================================================================
# Testing - LAB 1: Explore Tools
# ============================================================================

curl-list: ## LAB1: List available MCP tools (tools/list)
	@echo "=== Calling tools/list ==="
	@curl -s -X POST "http://localhost:8000/message" \
		-H "Content-Type: application/json" \
		-d '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}' | python3 -m json.tool

curl-weather: ## LAB1: Test weather tool directly (tools/call)
	@echo "=== Calling get_weather_forecast for Oslo ==="
	@curl -s -X POST "http://localhost:8000/message" \
		-H "Content-Type: application/json" \
		-d '{"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "get_weather_forecast", "arguments": {"location": "Oslo"}}}' | python3 -m json.tool

curl-agent: ## LAB1: Test query through agent
	@echo "=== Querying agent about weather ==="
	@curl -s -X POST "http://localhost:8001/query" \
		-H "Content-Type: application/json" \
		-d '{"query": "Hva er været i Bergen?"}' | python3 -m json.tool

# ============================================================================
# Testing - LAB 2: Random Fact Tool
# ============================================================================

curl-fact: ## LAB2: Test random fact tool (after implementation)
	@echo "=== Calling get_random_fact ==="
	@curl -s -X POST "http://localhost:8000/message" \
		-H "Content-Type: application/json" \
		-d '{"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "get_random_fact", "arguments": {"category": "space"}}}' | python3 -m json.tool

curl-fact-agent: ## LAB2: Test fact tool via agent
	@echo "=== Querying agent for a fact ==="
	@curl -s -X POST "http://localhost:8001/query" \
		-H "Content-Type: application/json" \
		-d '{"query": "Fortell meg et interessant faktum om verdensrommet"}' | python3 -m json.tool

# ============================================================================
# Testing - LAB 3: News API
# ============================================================================

curl-news: ## LAB3: Test news tool (after implementation)
	@echo "=== Calling get_news ==="
	@curl -s -X POST "http://localhost:8000/message" \
		-H "Content-Type: application/json" \
		-d '{"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "get_news", "arguments": {"topic": "AI", "language": "en"}}}' | python3 -m json.tool

curl-news-agent: ## LAB3: Test news via agent
	@echo "=== Querying agent for news ==="
	@curl -s -X POST "http://localhost:8001/query" \
		-H "Content-Type: application/json" \
		-d '{"query": "Hva er de siste nyhetene om kunstig intelligens?"}' | python3 -m json.tool

# ============================================================================
# Combined Tests
# ============================================================================

curl-combo: ## Test combining multiple tools
	@echo "=== Querying agent with multiple tools ==="
	@curl -s -X POST "http://localhost:8001/query" \
		-H "Content-Type: application/json" \
		-d '{"query": "Hva er været i Oslo, og fortell meg et faktum om verdensrommet"}' | python3 -m json.tool

# ============================================================================
# Compliance Testing
# ============================================================================

test-compliance: ## Run MCP SDK compliance test
	docker compose --profile compliance-test up mcp-sdk-client

# ============================================================================
# Database
# ============================================================================

db-view: ## Open Datasette to view conversation database
	@echo "Opening Datasette at http://localhost:8090"
	docker compose --profile datasette up -d datasette
	@sleep 2
	@open http://localhost:8090 2>/dev/null || echo "Visit http://localhost:8090"

db-stats: ## Show database statistics
	@docker compose exec travel-agent python3 -c "from conversation_memory import ConversationMemory; m = ConversationMemory(); print(m.get_stats())"

# ============================================================================
# Quick Start
# ============================================================================

setup: ## Initial setup (copy .env.example to .env)
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "Created .env from .env.example"; \
		echo "Please edit .env and add your API keys:"; \
		echo "  - OPENAI_API_KEY"; \
		echo "  (Værdata bruker yr.no - ingen API-nøkkel nødvendig)"; \
	else \
		echo ".env already exists"; \
	fi

quickstart: setup up status ## Full quickstart: setup + start + status
	@echo ""
	@echo "=== Workshop Ready ==="
	@echo "Web UI: http://localhost:8080"
	@echo ""
	@echo "Try these commands:"
	@echo "  make curl-list     # List available tools"
	@echo "  make curl-weather  # Test weather tool"
	@echo "  make curl-agent    # Query through agent"
