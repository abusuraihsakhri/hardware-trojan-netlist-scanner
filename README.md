# Hardware Trojan Netlist Scanner

> **Domain:** Post-Quantum Cryptography & Hardware Security
> **Standards:** NIST FIPS 203/204/205, Trust-HUB Hardware Trojan Taxonomy

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## Overview

Hardware Trojan Netlist Scanner is a multi-agent analytical platform for evaluating gate-level netlists, detecting hardware trojan insertion patterns, and classifying stealth payloads in ASIC/FPGA designs. It combines deterministic threshold analysis with an extensible worker-agent architecture.

The system operates two parallel subsystems:

- **`agents/`** — Enterprise supervisor orchestrator with PHI outbound guard, HMAC-SHA256 audit trail, and FastAPI REST API.
- **`hardware_trojan/`** — Core gate-level netlist scanner with specialized sub-agents for rare-event transition detection, combinational loop scanning, and stealth payload classification.

---

## Key Capabilities

- **Multi-Agent Worker Architecture**: Specialized workers evaluate payloads against domain-specific thresholds (InvariantQC, SafetyEscalation, ProtocolConformance).
- **PHI Outbound Guard**: Active regex inspection blocking SSNs, MRNs, phone numbers, emails, and patient identifiers from leaving the system.
- **Tamper-Evident HMAC-SHA256 Audit Trail**: Chained, cryptographically signed logs for every evaluation and state transition.
- **FastAPI REST API**: OpenAPI 3.1 endpoints for audit dispatch, chat, and metrics.
- **Batch CSV Processing**: High-throughput batch evaluation of netlist scan records.
- **Enrichment Suite**: Eight domain-specific engines for trust-HUB taxonomy compliance, gate-level differential testing, ML-based trojan detection, and more.
- **Prometheus Telemetry**: Operational metrics export for monitoring.

---

## Installation

```bash
# Clone the repository
git clone https://github.com/abusuraihsakhri/hardware-trojan-netlist-scanner.git
cd hardware-trojan-netlist-scanner

# Install dependencies
pip install fastapi uvicorn pydantic pytest
```

---

## Usage

### CLI — Enterprise Supervisor

```bash
# Run single task evaluation
python cli.py audit --task-id TASK-001 --target KEY-01 --primary 28.5 --secondary 14.2 --critical --status DISCORDANT

# Batch process CSV records
python cli.py batch -i sample.csv -o results.csv

# Verify HMAC audit trail integrity
python cli.py verify-audit

# Launch FastAPI REST server
python cli.py serve --host 127.0.0.1 --port 8000

# Supervisory chat query
python cli.py chat "What is the system status?"
```

### CLI — Hardware Trojan Scanner

```bash
# Run gate-level netlist scan
python hardware_trojan_app.py audit --task-id TASK-001 --target TARGET-01 --primary 29.4 --secondary 15.1 --critical --status DISCORDANT

# Batch process
python hardware_trojan_app.py batch -i sample.csv -o results.csv

# Launch REST server
python hardware_trojan_app.py serve --host 127.0.0.1 --port 8000
```

### REST API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health and metadata check |
| GET | `/metrics` | Prometheus operational metrics |
| POST | `/api/audit` | Dispatch task payload across workers |
| POST | `/api/chat` | Supervisory conversational assistant |
| GET | `/api/audit/logs` | Retrieve and verify HMAC audit trail |

### Input Data Schema

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| `task_id` | string | Unique task identifier | Yes |
| `target_identifier` | string | Target entity or key | Yes |
| `primary_metric` | float | Primary measurement (must be finite) | Yes |
| `secondary_metric` | float | Secondary metric (must be finite) | No (default: 0.0) |
| `status_descriptor` | string | Status code or phenotype | No (default: "NOMINAL") |
| `is_critical_flag` | boolean | Emergency escalation flag | No (default: false) |

---

## Testing

```bash
# Run full test suite
pytest -v

# Run with coverage
pytest -v --cov=agents --cov=hardware_trojan --cov=enrichment
```

### Test Coverage

- PHI guard enforcement (SSN, MRN, phone, email patterns)
- Specialized worker threshold evaluations
- Supervisor consensus and audit trail integrity
- CLI command execution (audit, chat, verify-audit)
- Enrichment suite execution and threshold escalation
- Sub-agent detection logic (rare-event, combinational loop, stealth payload)

---

## Simulation & Benchmarking

```bash
# Run high-throughput simulation (default: 100 tasks)
python simulator.py 1000
```

---

## Container Deployment

```bash
# Build and run with Docker
docker build -t hardware-trojan-netlist-scanner .
docker run -p 8000:8000 -e AUDIT_SECRET_KEY=$(openssl rand -hex 32) hardware-trojan-netlist-scanner

# Or use docker-compose
AUDIT_SECRET_KEY=$(openssl rand -hex 32) docker-compose up -d
```

> **Security Note:** Always set a strong `AUDIT_SECRET_KEY` in production. The system generates a secure random key at startup if none is provided, but for consistent audit trails across restarts, a persistent key is recommended.

---

## Project Structure

```
hardware-trojan-netlist-scanner/
├── agents/                    # Enterprise supervisor subsystem
│   ├── __init__.py           # Package metadata (v3.0.0-ENTERPRISE)
│   ├── api.py                # FastAPI REST server
│   ├── base.py               # PHI guard, HMAC audit trail, security
│   ├── learning.py           # Bayesian calibration engine
│   ├── llm_factory.py        # LLM provider factory (mock, Ollama, Claude, OpenAI)
│   ├── metrics.py            # Prometheus metrics collector
│   ├── models.py             # Pydantic schemas and data models
│   ├── streamer.py           # WebSocket telemetry broadcaster
│   ├── supervisor.py         # Master orchestrator
│   └── workers.py            # Specialized domain workers
├── hardware_trojan/           # Gate-level netlist scanner subsystem
│   ├── __init__.py           # Package metadata (v2.0.0-FRONTIER)
│   ├── agents.py             # Sub-agents and coordinator
│   ├── cli.py                # CLI entry point
│   ├── engine.py             # Core algorithmic engine
│   ├── models.py             # Data models and telemetry
│   └── server.py             # FastAPI server factory
├── tests/                     # Pytest test suite
│   ├── test_enrichment.py
│   ├── test_hardware_trojan.py
│   └── test_hardware_trojan_netlist_scanner.py
├── web/                       # Operations console (HTML/JS)
│   └── index.html
├── enrichment.py              # Domain enrichment engines
├── cli.py                     # Enterprise CLI entry point
├── simulator.py               # High-throughput simulation
├── benchmark_dataset.json     # Golden benchmark test cases
├── sample.csv                 # Sample batch input
├── sample_payload.json        # Sample API payload
├── pyproject.toml             # Project metadata and dependencies
├── Dockerfile                 # Container build
├── docker-compose.yml         # Container orchestration
└── .github/workflows/ci.yml   # CI/CD pipeline
```

---

## Security Architecture

- **Zero-PHI Outbound Interceptor:** Blocks SSNs, MRNs, phone numbers, emails, DOB patterns, and patient names.
- **HMAC-SHA256 Audit Trail:** Chained cryptographic signatures with integrity verification.
- **Input Validation:** Rejects NaN and Infinity values that could bypass threshold checks.
- **Secure Defaults:** No hardcoded secrets; audit key generated via `secrets.token_hex()` if not provided.

---

## License

MIT License. See [LICENSE](LICENSE) for details.
