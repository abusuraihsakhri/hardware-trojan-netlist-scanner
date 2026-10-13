# Hardware Trojan Netlist Scanner

### [Open the Live Application →](https://abusuraihsakhri.github.io/hardware-trojan-netlist-scanner/)

A Python command-line/API project with a standalone browser interface for **rule-based metric triage**.

**Scope:** Despite the historical repository name, the current implementation does **not** parse Verilog/VHDL netlists, analyze connectivity, identify hardware Trojans, or validate designs against Trust-HUB or NIST standards. Its results are threshold-based flags on user-provided numeric records, not evidence of a Trojan. The two Python subsystems use different secondary thresholds; they must not be treated as interchangeable.

## Browser application

Open `web/index.html` directly, or serve the `web/` directory using a static server:

```bash
python -m http.server 8080 --directory web
```

Then open `http://localhost:8080`. The browser form evaluates one record, displays rule findings and exports a JSON report. No API, runtime package, or Python-in-the-browser is needed. Browser metrics and identifiers are evaluated locally; the page does not make network requests.

The browser evaluator matches the enterprise `agents/` worker conditions:

| Condition | Finding |
|---|---|
| Primary metric > 25 | Elevated alert |
| Secondary metric > 12 | Elevated alert |
| Critical flag true | Critical alert (takes precedence) |
| Descriptor contains DISCORDANT, ANOMALY, MUTANT, VIOLATION, FAIL or REJECT | Elevated alert |

These limits are illustrative software rules, **not validated hardware detection cutoffs**.

## Python installation

Python 3.9 or newer is required. The CI matrix checks 3.10, 3.11 and 3.12.

```bash
git clone https://github.com/abusuraihsakhri/hardware-trojan-netlist-scanner.git
cd hardware-trojan-netlist-scanner
python -m pip install -e ".[api,test]"
python -m pytest -v
node --test web/app.test.js   # optional; requires Node.js
```

## Command-line workflows

The root CLI uses the Pydantic-based `agents/` subsystem:

```bash
python cli.py audit --task-id EXAMPLE-1 --target NET-1 --primary 28.5 --secondary 14.2 --status ANOMALY
python cli.py batch -i sample.csv -o results.csv
python cli.py verify-audit
python cli.py chat "status"
python cli.py serve --host 127.0.0.1 --port 8000
```

The separate legacy `hardware_trojan/` subsystem can be invoked with `python hardware_trojan_app.py audit ...`. It uses a **secondary threshold of 10**, rather than 12, and its own result schema. Both CLIs classify metrics, not gate-level designs.

### HTTP endpoints

When running the root CLI's server:

| Method | Path | Function |
|---|---|---|
| GET | `/health` | Service health metadata |
| GET | `/metrics` | JSON counters (not Prometheus text) |
| POST | `/api/audit` | Evaluate one numeric record |
| POST | `/api/chat` | Return local mock response |
| GET | `/api/audit/logs` | In-memory audit metadata and integrity status |

Example API request:

```bash
curl -s http://127.0.0.1:8000/api/audit \
  -H 'Content-Type: application/json' \
  -d '{"task_id":"EXAMPLE-1","target_identifier":"NET-1","primary_metric":28.5,"secondary_metric":14.2,"status_descriptor":"ANOMALY","is_critical_flag":false}'
```

## Security and data handling

- The static browser tool processes data locally, makes no uploads, and does not store results persistently.
- The Python API processes supplied identifiers and metrics in the server process. The server retains dossiers and signed audit metadata **in memory**; they are lost when it restarts.
- Audit entries contain metadata and SHA-256 payload digests, chained with HMAC-SHA256. Signature verification detects in-memory modification while the original signing key is held. This is **not** durable audit storage.
- The Python supervisor uses regex-based restricted-identifier screening. It is not comprehensive anonymization or a guarantee of HIPAA compliance. Do not submit sensitive records to an untrusted server.
- `AUDIT_SECRET_KEY` should be a persistent, strong secret for server deployments. Docker Compose requires you to supply it and does not ship a default key.
- The language-model factory currently supports **only a deterministic mock**. No remote inference provider is implemented.

## Development and deployment

The repository contains two Python packages (`agents/` and `hardware_trojan/`), a root CLI, regression tests, Docker configuration, and the dependency-free static `web/` application.

```bash
python -m pytest -v
python -m compileall -q agents hardware_trojan cli.py enrichment.py simulator.py
node --check web/app.js
node --test web/app.test.js
```

CI performs these checks and attempts to publish `web/` to GitHub Pages from `master` after the test matrix succeeds. Pages availability depends on the repository's hosting settings and must be verified separately. The browser UI uses standard JavaScript and CSS; modern Chromium, Firefox and Safari are intended targets, but full cross-browser certification has not been performed.

## License

MIT — see [LICENSE](LICENSE).
