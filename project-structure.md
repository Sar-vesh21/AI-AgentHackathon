# Current Project Structure

```
trading-analytics-platform/
├── hyperliquid/                    # Hyperliquid trading analytics
│   ├── background_jobs/           # Background processing jobs
│   │   └── main_job.py           # Main background job
│   ├── data/                      # Data processing modules
│   ├── api/                       # API endpoints
│   ├── db/                        # Database related code
│   ├── agent/                     # Agent related code
│   ├── analysis_cache/            # Cached analysis data
│   ├── myenv/                     # Python virtual environment
│   ├── main.py                    # Main application entry
│   ├── llm_agent.py              # LLM agent implementation
│   ├── requirements.txt           # Python dependencies
│   ├── .env                       # Environment variables
│   ├── hyperliquid.db            # SQLite database
│   └── *.json                     # Various data files
│
├── eliza/                         # Eliza AI agent system
│   ├── packages/                  # Core packages
│   ├── client/                    # Client application
│   ├── agent/                     # Agent implementation
│   ├── docs/                      # Documentation
│   ├── characters/                # Character definitions
│   ├── scripts/                   # Utility scripts
│   ├── tests/                     # Test files
│   ├── i18n/                      # Internationalization
│   ├── patches/                   # Code patches
│   ├── .github/                   # GitHub configuration
│   ├── .devcontainer/            # Development container config
│   ├── package.json              # Node.js dependencies
│   ├── tsconfig.json             # TypeScript configuration
│   ├── turbo.json                # Turborepo configuration
│   ├── pnpm-workspace.yaml       # pnpm workspace config
│   ├── .env                      # Environment variables
│   └── various config files      # Other configuration files
│
├── README.md                      # Project documentation
├── .gitignore                    # Git ignore rules
└── LICENSE                       # Project license
```

## Key Components

### Hyperliquid Component
- **Background Jobs**: Continuous data processing and analysis
- **Data Processing**: Market data analysis and processing
- **API**: REST API endpoints for data access
- **Database**: SQLite database for storing trading data
- **Agent**: Trading agent implementation
- **LLM Integration**: Language model integration for analysis

### Eliza Component
- **Core Packages**: Main functionality packages
- **Client**: User interface
- **Agent**: AI agent implementation
- **Documentation**: Project documentation
- **Characters**: AI character definitions
- **Testing**: Test suite
- **Internationalization**: Multi-language support

## Configuration Files
- Environment variables (.env)
- Package management (package.json, requirements.txt)
- Build configuration (tsconfig.json, turbo.json)
- Version control (.gitignore)
- License information (LICENSE) 