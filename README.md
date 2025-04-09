# HyperInsight: A Hyperliquid Trading Analytics System



> 📚 Further Documentation can be found here: [HyperInsight Documentation](https://www.youtube.com/watch?v=bo1Un8C6PqY&ab_channel=SarveshRajdev)

HyperInsight is the ultimate analysis tool for Hyperliquid and the market. Empowering traders to use real-time statistics and track the best derivatives traders on Hyperliquid.

What's more? Our innovative AI agent swarm handles the workload, saving you the need to look through GBs of data and providing insights right on the spot.

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

5. Start the background jobs (these need to be scheduled by the developer, e.g., via cron):
   ```bash
   python -m background_jobs.main_job
   python -m background_jobs.analysis_job
   python -m background_jobs.vault_job
   python -m background_jobs.sentiment_job
   ```

6. In a new terminal, start the API server:
   ```bash
   python -m api.analysis_api
   ```

The background jobs will continuously collect and analyze trading data, while the API server provides access to this data.

### 2. Frontend Agent Setup

After the Hyperliquid system is running, you can set up the front end:

1. Navigate to the frontendAgent directory:
   ```bash
   cd frontendAgent
   ```

2. Install dependencies:
   ```bash
   pnpm i
   ```

3. Build the project:
   ```bash
   pnpm build
   ```

4. Start frontendAgent:
   ```bash
   pnpm start --characters="./characters/HyperLiquidHelper.json"
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

### FrontendAgent Component
- AI agent system for processing and responding to queries
- Integrates with the Hyperliquid analytics
- Provides interactive interface for data exploration

## Environment Variables

### Hyperliquid (.env)
- Required API keys and configuration for Hyperliquid data collection
- Database connection settings
- LLM configuration

### FrontendAgent (.env)
- AI model configuration
- API keys for various services
- Character and plugin settings

## Troubleshooting

### If background jobs fail:
- Check the logs in `hyperliquid/background_jobs/logs/`
- Verify API keys in `.env`
- Ensure database permissions

### If Eliza fails to start:
- Run `pnpm clean` and try again
- Check Node.js version (requires 23+)
- Verify that all dependencies are installed

## Support

For issues with:
- Hyperliquid component: Check the logs and verify the configuration
- Frontend Agent component: Visit Documentation

## License

This project is licensed under the terms specified in the LICENSE file.


# Team Contribution
Team is only one person: Sarvesh Rajdev :)
