# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with the Sage project - a multi-persona AI-powered tmux session monitoring tool.

## Project Overview

Sage is an enhanced Python-based tmux automation tool that:
- Monitors multiple tmux panes for idle state
- Uses configurable AI personas to suggest contextually appropriate commands
- Supports multiple AI providers (OpenRouter, Anthropic, OpenAI-compatible endpoints)
- Maintains project-specific context and interaction history
- Compresses persona definitions using Markqant format for efficiency
- Features personas like Omni (philosophical), Claude Code (development), Trisha (fun), and Aye (companion)

## Build/Run Commands

### Python Project Setup
- Create virtual environment: `python -m venv .venv`
- Activate environment: `source .venv/bin/activate` (Unix/macOS) or `.venv\Scripts\activate` (Windows)
- Install dependencies: `pip install -r requirements.txt`
- Create default personas: `python create_personas.py`
- Run original script: `python ss.py`
- Run enhanced version: `python sage.py [persona_name]`

### Development Commands
- Lint: `ruff check .`
- Format: `black .`
- Type check: `mypy .`
- Run tests: `pytest` (when tests are added)

## Code Structure

### Main Components

1. **ss.py** - The original simple monitoring script

2. **sage.py** - Enhanced version with persona support containing:
   - `PersonaManager` - Manages AI personas and configurations
   - `MarkqantProcessor` - Handles .mq format compression/decompression
   - `ContextManager` - Manages project-specific context and logs
   - `SageSession` - Main session orchestrator with rich UI

3. **create_personas.py** - Creates default personas:
   - Omni - Philosophical guide using GPT-4o
   - Claude Code - Development specialist using Claude 3 Sonnet
   - Trisha - Fun and colorful using Llama 3 70B
   - Aye - Helpful companion using GPT-4 Turbo

### File Structure
```
~/.sage/
├── personas/
│   ├── [persona].mq    # Compressed personality (Markqant format)
│   └── [persona].yml   # API configuration

project/
├── .sage_proj/
│   ├── context.m8          # Compressed context
│   ├── interactions.jsonl  # Interaction history
│   └── sage_*.log         # Session logs
```

### Configuration
- `SESSION = "my-session"` - Default tmux session name
- `IDLE_THRESHOLD_RANGE = (10, 20)` - Random idle time range
- `CHECK_INTERVAL = 1` - Check frequency in seconds

## Dependencies

### Required Python Packages
```
pyyaml>=6.0.1          # YAML configuration parsing
httpx>=0.25.0          # Modern HTTP client for API calls
rich>=13.7.0           # Beautiful terminal output
python-dotenv>=1.0.0   # Environment variable management
```

### System Requirements
- tmux installed and running
- Python 3.8+
- API keys for chosen providers (OpenRouter, Anthropic, etc.)

## Key Features Implemented

### 1. Multi-Persona Support
- Load personas from `~/.sage/personas/`
- Each persona has `.mq` (compressed personality) and `.yml` (config) files
- Support for different AI models and endpoints
- Default personas: Omni, Claude Code, Trisha, Aye, Helpful

### 2. Markqant Compression
- Compress persona definitions by 70-90%
- Token-based compression for repeated patterns
- Optional zlib for additional compression
- Maintains semantic meaning perfectly

### 3. Context Management
- Project-specific `.sage_proj/` directories
- Interaction logging in JSONL format
- Context persistence in compressed .m8 format
- Recent command history tracking

### 4. Beautiful UI
- Rich terminal tables showing pane status
- Colorful progress indicators
- Clear status messages
- Real-time monitoring display

## API Configuration

### Persona YAML Structure
```yaml
api_endpoint: https://openrouter.ai/api/v1/chat/completions
model: openai/gpt-4
api_key: your-api-key
temperature: 0.7
max_tokens: 500
tools:
  - git
  - docker
mcp_tools:
  - code_analysis
```

### Supported Endpoints
- OpenRouter (multiple models)
- Anthropic Claude API
- Any OpenAI-compatible endpoint

## Aye, Hue & Trisha Integration

The enhanced Sage fully embraces the Aye, Hue & Trisha philosophy:

### Trisha's Contributions
- Colorful terminal output everywhere! 🌈
- Fun status messages and emoji
- Sassy error messages
- Making monitoring enjoyable

### Omni's Wisdom
- Philosophical command suggestions
- Water metaphors in messages
- Deep insights about idle time
- "Like waves on a shore..." 🌊

### Hot Tub Mode
- Collaborative debugging with personas
- Each persona brings unique perspective
- Visual monitoring with ASCII art
- Fun and productive sessions

## Usage Examples

```bash
# List available personas
python sage.py --list

# Use specific persona
python sage.py omni
python sage.py trisha --session dev

# Create custom persona
python sage.py --create

# Set default session
export SAGE_SESSION=my-dev-session
python sage.py claude-code
```

## Development Workflow

1. **Adding New Personas**:
   - Create personality in Markqant format
   - Define API configuration
   - Use `PersonaManager.create_persona()`

2. **Testing Changes**:
   - Run with different personas
   - Check interaction logs
   - Verify context persistence

3. **Debugging**:
   - Check `.sage_proj/sage_*.log` files
   - Review `interactions.jsonl`
   - Use rich console for debugging

## Future Enhancements

1. **MCP Tool Integration**: Full support for Model Context Protocol tools
2. **Voice Feedback**: Kokoro TTS integration for announcements
3. **Multi-Session**: Monitor multiple tmux sessions
4. **Web Dashboard**: Real-time visualization
5. **Distributed Monitoring**: Cross-machine support

## Safety Considerations

- API keys stored in YAML files - keep secure
- All interactions logged for audit
- Commands shown before execution
- No auto-execution of dangerous commands
- Rate limiting recommended

Remember: Sage with personas is like having a team of specialized AI assistants watching your terminal, each bringing their unique perspective and expertise! 🧙✨