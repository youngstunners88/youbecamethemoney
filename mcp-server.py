#!/usr/bin/env python3
"""
Zo Computer MCP Bridge - Enables Claude Code to control Garcia-Ramsees infrastructure
Exposes 8 tools for bash execution, database queries, agent messaging, and deployments
"""

import os
import json
import subprocess
import requests
from typing import Any
from mcp.server.models import Tool
from mcp.server import Server
import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# Load Zo connection config from ~/.zo/.env
ZO_CONFIG = {
    "host": os.getenv("ZO_HOST", "localhost"),
    "port": int(os.getenv("ZO_PORT", "22")),
    "user": os.getenv("ZO_USER", "deploy"),
    "db_host": os.getenv("ZO_DB_HOST", "localhost"),
    "db_name": os.getenv("ZO_DB_NAME", "garcia_ramsees"),
    "db_user": os.getenv("ZO_DB_USER", "postgres"),
    "ramsees_api": os.getenv("RAMSEES_API", "https://detectable-clarita-casuistically.ngrok-free.dev"),
}

server = Server("zo-bridge")

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> Any:
    """Route tool calls to implementation"""
    try:
        if name == "zo_bash":
            return await zo_bash(arguments.get("command"))
        elif name == "zo_postgres":
            return await zo_postgres(arguments.get("query"))
        elif name == "zo_hermes_chat":
            return await zo_hermes_chat(arguments.get("message"), arguments.get("priority", "normal"))
        elif name == "zo_deploy":
            return await zo_deploy(arguments.get("service"), arguments.get("version"))
        elif name == "zo_logs":
            return await zo_logs(arguments.get("service"), arguments.get("lines", 50))
        elif name == "zo_health":
            return await zo_health()
        elif name == "zo_restart":
            return await zo_restart(arguments.get("service"))
        elif name == "zo_config":
            return await zo_config(arguments.get("action"), arguments.get("key"), arguments.get("value"))
    except Exception as e:
        log.error(f"Tool error: {e}")
        return {"error": str(e), "status": "failed"}

async def zo_bash(command: str) -> dict:
    """Execute command on Zo via SSH"""
    try:
        result = subprocess.run(
            ["ssh", f"{ZO_CONFIG['user']}@{ZO_CONFIG['host']}", "-p", str(ZO_CONFIG['port']), command],
            capture_output=True,
            text=True,
            timeout=30
        )
        return {
            "status": "success" if result.returncode == 0 else "error",
            "output": result.stdout,
            "error": result.stderr,
            "exit_code": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {"status": "timeout", "error": "Command exceeded 30s timeout"}
    except Exception as e:
        return {"status": "error", "error": str(e)}

async def zo_postgres(query: str) -> dict:
    """Execute PostgreSQL query on Zo database"""
    try:
        cmd = f"psql -h {ZO_CONFIG['db_host']} -U {ZO_CONFIG['db_user']} -d {ZO_CONFIG['db_name']} -c \"{query}\""
        result = await zo_bash(cmd)
        return {
            "status": result.get("status"),
            "data": result.get("output"),
            "error": result.get("error")
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

async def zo_hermes_chat(message: str, priority: str = "normal") -> dict:
    """Send message to Ramsees agent via API"""
    try:
        response = requests.post(
            f"{ZO_CONFIG['ramsees_api']}/api/ramsees-message",
            json={"message": message, "priority": priority, "source": "zo-bridge"},
            timeout=10
        )
        return {
            "status": "success" if response.status_code == 200 else "error",
            "response": response.json(),
            "code": response.status_code
        }
    except requests.exceptions.Timeout:
        return {"status": "timeout", "error": "Ramsees API request timeout"}
    except Exception as e:
        return {"status": "error", "error": str(e)}

async def zo_deploy(service: str, version: str) -> dict:
    """Deploy service version to Zo"""
    cmd = f"cd /opt/ramsees && docker pull {service}:{version} && docker-compose up -d {service}"
    result = await zo_bash(cmd)
    return {"status": result.get("status"), "deployment": service, "version": version, "output": result.get("output")}

async def zo_logs(service: str, lines: int = 50) -> dict:
    """Fetch service logs from Zo"""
    cmd = f"journalctl -u {service} -n {lines} --no-pager"
    result = await zo_bash(cmd)
    return {"status": result.get("status"), "service": service, "logs": result.get("output")}

async def zo_health() -> dict:
    """Check overall Zo system health"""
    checks = {
        "cpu": await zo_bash("top -bn1 | grep 'Cpu(s)' | awk '{print $2}'"),
        "memory": await zo_bash("free -h | grep Mem"),
        "disk": await zo_bash("df -h /"),
        "services": await zo_bash("systemctl list-units --type=service --state=running | wc -l")
    }
    return {"status": "success", "health_checks": checks}

async def zo_restart(service: str) -> dict:
    """Restart service on Zo"""
    result = await zo_bash(f"systemctl restart {service}")
    return {"status": result.get("status"), "service": service, "restarted": result.get("exit_code") == 0}

async def zo_config(action: str, key: str = None, value: str = None) -> dict:
    """Manage Zo configuration"""
    if action == "get":
        result = await zo_bash(f"cat /etc/ramsees/config.json | jq '.{key}'")
        return {"status": "success", "key": key, "value": result.get("output")}
    elif action == "set":
        cmd = f"echo '{json.dumps({key: value})}' | jq . > /tmp/config.json && mv /tmp/config.json /etc/ramsees/config.json"
        result = await zo_bash(cmd)
        return {"status": result.get("status"), "key": key, "updated": result.get("exit_code") == 0}
    else:
        return {"status": "error", "error": f"Unknown action: {action}"}

def register_tools():
    """Register all 8 tools with MCP server"""
    tools = [
        Tool(
            name="zo_bash",
            description="Execute shell command on Zo Computer via SSH",
            inputSchema={"type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"]}
        ),
        Tool(
            name="zo_postgres",
            description="Execute PostgreSQL query on Zo database",
            inputSchema={"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}
        ),
        Tool(
            name="zo_hermes_chat",
            description="Send message to Ramsees agent",
            inputSchema={"type": "object", "properties": {"message": {"type": "string"}, "priority": {"type": "string"}}, "required": ["message"]}
        ),
        Tool(
            name="zo_deploy",
            description="Deploy service version to Zo",
            inputSchema={"type": "object", "properties": {"service": {"type": "string"}, "version": {"type": "string"}}, "required": ["service", "version"]}
        ),
        Tool(
            name="zo_logs",
            description="Fetch service logs from Zo",
            inputSchema={"type": "object", "properties": {"service": {"type": "string"}, "lines": {"type": "integer"}}, "required": ["service"]}
        ),
        Tool(
            name="zo_health",
            description="Check Zo system health (CPU, memory, disk, services)",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="zo_restart",
            description="Restart service on Zo",
            inputSchema={"type": "object", "properties": {"service": {"type": "string"}}, "required": ["service"]}
        ),
        Tool(
            name="zo_config",
            description="Manage Zo configuration (get/set)",
            inputSchema={"type": "object", "properties": {"action": {"type": "string"}, "key": {"type": "string"}, "value": {"type": "string"}}, "required": ["action"]}
        ),
    ]
    server.tools = tools

if __name__ == "__main__":
    register_tools()
    server.run()
