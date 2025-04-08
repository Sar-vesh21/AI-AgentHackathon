# Trading Analytics Platform

This repository contains two main components:
1. A Hyperliquid trading analytics system
2. An Eliza AI agent system

## Prerequisites

- Python 3.8+
- Node.js 23+
- pnpm
- SQLite3

## Setup Instructions

### 1. Hyperliquid Analytics Setup

First, set up and run the Hyperliquid analytics system:

1. Navigate to the hyperliquid directory:
```bash
cd hyperliquid
```

2. Create and activate a virtual environment:
```bash
python -m venv myenv
source myenv/bin/activate  # On Windows: myenv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Start the background jobs:
```bash
python background_jobs/main_job.py
```

6. In a new terminal, start the API server:
```bash
python main.py
```

The background jobs will continuously collect and analyze trading data, while the API server provides access to this data.

### 2. Eliza Setup

After the Hyperliquid system is running, you can set up Eliza:

1. Navigate to the eliza directory:
```bash
cd eliza
```

2. Install dependencies:
```bash
pnpm i
```

3. Build the project:
```bash
pnpm build
```

4. Start Eliza:
```bash
pnpm start
```

5. In a new terminal, start the client:
```bash
pnpm start:client
```

## System Architecture

### Hyperliquid Component
- Background jobs collect and analyze trading data
- API server provides access to analyzed data
- SQLite database stores trading metrics and analysis
- LLM agent provides insights on trading patterns

### Eliza Component
- AI agent system for processing and responding to queries
- Integrates with the Hyperliquid analytics
- Provides interactive interface for data exploration

## Environment Variables

### Hyperliquid (.env)
- Required API keys and configuration for Hyperliquid data collection
- Database connection settings
- LLM configuration

### Eliza (.env)
- AI model configuration
- API keys for various services
- Character and plugin settings

## Troubleshooting

1. If background jobs fail:
   - Check the logs in `hyperliquid/background_jobs/logs/`
   - Verify API keys in `.env`
   - Ensure database permissions

2. If Eliza fails to start:
   - Run `pnpm clean` and try again
   - Check Node.js version (requires 23+)
   - Verify all dependencies are installed

## Support

For issues with:
- Hyperliquid component: Check the logs and verify configuration
- Eliza component: Visit [Eliza Documentation](https://elizaos.github.io/eliza/)

## License

This project is licensed under the terms specified in the LICENSE file. 