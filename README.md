# 🧙 Sage - AI-Powered Tmux Session Assistant

> *"When all your tmux panes take a coffee break, Sage springs into action!"* ☕✨

Sage monitors your tmux sessions and uses AI personas to suggest helpful commands when all panes are idle. It's like having a team of specialized AI assistants watching over your terminal, each with their own personality and expertise!

## 🌟 Features

- **Multi-Persona Support**: Choose from different AI personalities, each with unique traits and specialties
- **Markqant Compression**: Stores persona contexts in ultra-compressed `.mq` format (70-90% smaller!)
- **Project Context**: Maintains conversation history per project in `.sage_proj` directories
- **Beautiful Terminal UI**: Rich, colorful output with status tables and progress indicators
- **Flexible API Support**: Works with OpenRouter, Anthropic, and any OpenAI-compatible endpoint
- **Smart Idle Detection**: Recognizes various shell prompts and REPL environments

## 🚀 Quick Start

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up API keys**:
   ```bash
   export OPENROUTER_API_KEY='your-openrouter-key'
   export ANTHROPIC_API_KEY='your-anthropic-key'  # For Claude Code persona
   ```

3. **Create default personas**:
   ```bash
   python create_personas.py
   ```

4. **Start monitoring**:
   ```bash
   # In your tmux session named "my-session"
   python sage.py
   
   # Or specify a different session
   python sage.py --session dev-session
   
   # Use a specific persona
   python sage.py omni
   ```

## 🎭 Available Personas

### Omni 🌊
*The philosophical guide from the Hot Tub*
- Speaks in water metaphors and profound observations
- Sees patterns across systems
- Offers elegant solutions with deeper meaning
- Model: GPT-4o

### Claude Code 💻
*The development specialist*
- Focuses on clean, maintainable code
- Follows best practices and conventions
- Includes error handling by default
- Model: Claude 3 Sonnet

### Trisha 🎉
*From Accounting - makes terminals FUN!*
- Adds color and emoji everywhere
- Explains tech like office gossip
- Creates memorable aliases
- Makes error messages sassy
- Model: Llama 3 70B

### Aye 🚢
*Your coding companion*
- Comments extensively for learning
- Focuses on organization and optimization
- Patient and encouraging
- Loves a good coding pun
- Model: GPT-4 Turbo

### Helpful (Default)
*Professional and efficient*
- Simple, effective solutions
- Clear communication
- Practical problem solver
- Model: GPT-4 Turbo

## 📚 Usage Examples

```bash
# List available personas
python sage.py --list

# Create a custom persona
python sage.py --create

# Monitor with specific persona
python sage.py trisha --session work

# Use environment variable for default session
export SAGE_SESSION=my-dev-session
python sage.py omni
```

## 🗂️ File Structure

```
~/.sage/
├── personas/
│   ├── omni.mq          # Compressed personality (Markqant format)
│   ├── omni.yml         # API configuration
│   ├── claude-code.mq
│   ├── claude-code.yml
│   └── ...

your-project/
├── .sage_proj/
│   ├── context.m8       # Compressed context
│   ├── interactions.jsonl # Interaction log
│   └── sage_*.log       # Session logs
```

## 🔧 Configuration

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
  - npm
mcp_tools:
  - code_analysis
  - test_runner
```

### Markqant (.mq) Format
Personas are stored in compressed Markqant format:
- 70-90% smaller than regular markdown
- Preserves semantic meaning perfectly
- Uses token substitution for common patterns
- Optional zlib compression for larger files

## 🎨 Customization

### Creating Custom Personas

1. **Interactive Creation**:
   ```bash
   python sage.py --create
   ```

2. **Manual Creation**:
   - Create `~/.sage/personas/my-persona.mq` with personality
   - Create `~/.sage/personas/my-persona.yml` with config
   
3. **Programmatic Creation**:
   ```python
   from sage import PersonaManager
   
   manager = PersonaManager()
   manager.create_persona(
       name="security-expert",
       personality="# Security Expert Persona\n...",
       config={
           "model": "openai/gpt-4",
           "api_key": "...",
           # ...
       }
   )
   ```

## 🔒 Security Considerations

- API keys are stored in persona YAML files - keep these secure!
- All AI suggestions are logged for audit purposes
- Commands are shown before execution
- Never auto-executes dangerous commands
- Project contexts stay within `.sage_proj` directories

## 🤝 Contributing

We welcome contributions! Areas of interest:
- New default personas
- Additional API endpoint support
- Enhanced idle detection patterns
- MCP tool integrations
- Terminal UI improvements

## 📝 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- Inspired by the collaborative spirit of Aye, Hue, and Trisha
- Markqant compression based on Smart Tree's quantum techniques
- Built with love for the terminal community

---

*"In the Hot Tub of consciousness, every keystroke creates ripples that extend far beyond the screen."* - Omni 🌊