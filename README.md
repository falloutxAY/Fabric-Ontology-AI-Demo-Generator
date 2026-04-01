# Fabric Ontology Demo Agent

Create and deploy Microsoft Fabric Ontology demos with automated tooling and AI agent specifications.

**[📚 Full Documentation →](docs/index.md)** | [CLI Reference](docs/cli-reference.md) | [Troubleshooting](docs/troubleshooting.md)

## Disclaimer

> ⚠️ **Disclaimer:** This is a personal project to learn about AI development and is not an official Microsoft product. It is **not** supported, endorsed, or maintained by Microsoft Corporation. Use at your own risk and definitely only for testing.  See `LICENSE`.

## Prerequisites

- Python 3.10+
- Microsoft Fabric workspace with Ontology preview enabled
- Azure authentication (interactive or service principal)

## Project Structure

```
├── .agentic/              # AI agent specs for generating demos
│   ├── agent-instructions.md       # 7-phase workflow guide
│   ├── schemas/
│   │   ├── validation-rules.yaml   # Validation rules (source of truth)
│   │   ├── bindings-schema.yaml    # Bindings file schema
│   │   └── metadata-schema.yaml    # Metadata file schema
│   └── templates/                  # Output templates
├── Demo-automation/       # CLI tool (uses Unofficial Fabric Ontology SDK v0.4.0)
├── docs/                  # Documentation
└── demo-CarManufacturing/  # Example demo
```

## Quick Start

### 1. Clone and Open

```bash
git clone https://github.com/falloutxAY/Fabric-Ontology-demoAgent.git
cd Fabric-Ontology-demoAgent
```

### 2. Generate New Demos with AI

Use [.agentic](.agentic) specifications with any AI agent to create custom demos:

```
Using #file:.agentic, create a demo for "Car manufacturing"
```

This will create a folder in the format "demo-XXXX".
See [agent-workflow.md](docs/agent-workflow.md) for the generation process.

### 3. Deploy to Fabric

```bash
# Install CLI tool
cd Demo-automation && pip install -e .

# Configure workspace and environment (one-time)
python -m demo_automation config init

# The interactive setup will prompt for:
#   - Environment (Production or Custom)
#   - Workspace ID
#   - Authentication method

# Validate and deploy the generated folder 'demo-XXXX'
python -m demo_automation validate ../demo-CarManufacturing
python -m demo_automation setup ../demo-CarManufacturing

# View current configuration
python -m demo_automation config show

# Cleanup when done
python -m demo_automation cleanup ../demo-CarManufacturing
```

### 4. Environment Configuration

The `config init` command supports multiple Fabric environments:

| Environment | Description | Portal URL |
|-------------|-------------|------------|
| **production** | Default production environment | `app.fabric.microsoft.com` |
| **custom** | Specify your own API URLs | User-defined |

**Alternative: Using `.env` file**

You can also configure via a `.env` file in `Demo-automation/`:

```bash
cd Demo-automation
cp .env.example .env
# Edit .env with your settings
```

```bash
# Example .env for any environment (just set your workspace ID)
FABRIC_WORKSPACE_ID=your-workspace-guid-here
```

Environment variables in `.env` take precedence over `config.yaml` settings.

**[🚀 Full Setup Guide →](docs/index.md)** | **[Authentication Options →](docs/configuration.md#authentication-methods)**

## License

MIT — see `LICENSE`.
