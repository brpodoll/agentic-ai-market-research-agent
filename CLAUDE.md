# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a standalone AI-powered Market Research Agent that analyzes businesses and identifies AI automation opportunities. It uses CrewAI framework with multiple specialized agents (Market Research Analyst, Business Process Optimization Specialist, and Financial ROI Analyst) to perform comprehensive business analysis.

## Key Commands

### Setup
```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install crewai langchain-openai python-dotenv

# Set up environment
echo "OPENAI_API_KEY=sk-your-key-here" > .env
```

### Running the Application
```bash
python market_research_agent.py
```

## Core Architecture

### Multi-Agent System
The application uses a CrewAI-based multi-agent architecture with three specialized agents:

1. **Market Research Analyst** - Analyzes business operations and identifies automation opportunities
2. **Business Process Optimization Specialist** - Evaluates processes and designs automation solutions
3. **Financial ROI Analyst** - Calculates ROI projections and business impact

### Key Components

- **MarketResearchAgent class** (`market_research_agent.py:70-358`) - Main orchestrator that coordinates the agent crew
- **create_research_crew()** (`market_research_agent.py:124-162`) - Initializes and configures the three specialized agents
- **analyze_business()** (`market_research_agent.py:164-238`) - Executes the multi-stage analysis workflow with tasks for each agent
- **Industry templates** (`market_research_agent.py:86-122`) - Pre-configured process mappings for legal, consulting, real estate, healthcare, and manufacturing industries

### Data Models

The system uses dataclasses to structure analysis results:
- **BusinessProfile** (`market_research_agent.py:37-46`) - Business information and pain points
- **ProcessAnalysis** (`market_research_agent.py:48-58`) - Detailed analysis of automatable processes with ROI calculations
- **MarketResearchResult** (`market_research_agent.py:60-69`) - Complete analysis package with recommendations

### Workflow

1. **Business Discovery** (`collect_business_info()`) - Interactive questionnaire collects business details
2. **Agent Creation** (`create_research_crew()`) - Instantiates three specialized CrewAI agents
3. **Task Execution** (`analyze_business()`) - Runs sequential tasks: market research → process analysis → ROI calculation
4. **Result Processing** (`_parse_analysis_result()`) - Structures LLM outputs into dataclass format
5. **Report Generation** (`print_analysis_report()`) - Formats and displays comprehensive analysis

## Configuration

- Requires `OPENAI_API_KEY` environment variable or in `.env` file
- Uses GPT-4o-mini model for cost-effective analysis
- Temperature set to 0.3 for consistent, focused outputs

## Important Implementation Details

### LLM Response Parsing
The `_parse_analysis_result()` method currently uses simplified parsing logic. In production, the raw LLM responses would need more sophisticated NLP parsing to extract structured data from the agent outputs.

### Report Generation
- Interactive mode collects business info via 6-question questionnaire
- Generates timestamped JSON reports (`market_research_analysis_YYYYMMDD_HHMMSS.json`)
- Console output uses formatted tables and sections for professional presentation

### Error Handling
- Validates OpenAI API key on startup
- Provides clear instructions if API key is missing
- Wrapped main execution in try/catch for graceful error reporting