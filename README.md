# Foreign Trade MCP

A Model Context Protocol (MCP) server for foreign trade business automation, providing tools for company research, professional contact discovery, and business intelligence.

## Features

- **Company Search & Enrichment**: Find and enrich company profiles with industry, revenue, and headcount data
- **Professional Discovery**: Search for decision-makers and key contacts at target companies
- **Contact Enrichment**: Get verified email and mobile phone numbers for professionals
- **Account Management**: Track credits and account status

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

## Available Tools

| Tool | Description |
|------|-------------|
| `search_company` | Search for companies by name |
| `enrich_company` | Get full company profile including headcount, industry, revenue |
| `search_person` | Search for professionals by name, title, company |
| `enrich_person` | Get verified contact details (email/mobile) for a person |
| `get_account_info` | Check account credits and status |

## Project Structure

```
foreign-trade-mcp/
├── mcp/
│   └── tools.py       # MCP tool implementations
├── main.py            # Entry point
├── requirements.txt   # Dependencies
└── README.md          # This file
```

## License

MIT
