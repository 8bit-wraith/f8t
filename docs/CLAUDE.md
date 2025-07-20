# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with the Sage project - a tmux session monitoring tool that uses AI to suggest commands when panes are idle.

## Project Overview

Sage is a Python-based tmux automation tool that:
- Monitors multiple tmux panes for idle state
- Captures pane content when all panes have been idle for a threshold period
- Sends summaries to an AI API (OpenAI) for command suggestions
- Executes suggested commands in the main tmux pane

## Build/Run Commands

### Python Project Setup
- Create virtual environment: `python -m venv .venv`
- Activate environment: `source .venv/bin/activate` (Unix/macOS) or `.venv\Scripts\activate` (Windows)
- Install dependencies: `pip install -r requirements.txt` (create this file first)
- Run the script: `python ss.py`

### Development Commands
- Lint: `ruff check .`
- Format: `black .`
- Type check: `mypy .`
- Run tests: `pytest` (when tests are added)

## Code Structure

### Main Components

1. **ss.py** - The main script containing:
   - `list_panes()` - Lists all tmux panes in the session
   - `get_pane_content()` - Captures content from a specific pane
   - `is_idle()` - Checks if a pane is idle (has a shell prompt)
   - `get_summary()` - Gets the last 5 lines from a pane
   - `query_openai()` - Interfaces with OpenAI API (currently mocked)
   - `send_to_pane()` - Sends commands to a tmux pane
   - `main()` - Main loop that monitors and coordinates actions

### Configuration
- `SESSION = "my-session"` - The tmux session name to monitor
- `IDLE_THRESHOLD_RANGE = (10, 20)` - Random idle time range in seconds
- `CHECK_INTERVAL = 1` - How often to check pane states (seconds)

## Dependencies

### Required Python Packages
```
openai>=1.0.0
```

### System Requirements
- tmux installed and running
- Python 3.8+
- Active tmux session named "my-session"

## Aye, Hue & Trisha Guidelines for Sage

### Trisha's Take on Sage
"Think of Sage like having an AI assistant watching over your shoulder in the terminal - but in a helpful way, not creepy! It's like having a really smart rubber duck that can actually type commands for you. When all your tmux panes take a coffee break, Sage springs into action with suggestions. It's the accounting equivalent of auto-completing journal entries based on past patterns!" 

### Enhancement Ideas with Personality
- Add colorful ANSI output to show which pane is being monitored
- Include witty status messages like "All panes are napping... time for AI magic! ✨"
- Error messages with personality: "Oops! Tmux session 'my-session' is playing hide and seek. 🙈"
- Add sound effects using the Kokoro TTS when commands are executed

### Hot Tub Mode Integration
When debugging Sage issues:
- Use tmux's capture-pane feature to create a "time-lapse" of pane activity
- Visualize idle patterns with ASCII art waves 🌊
- Have Omni provide philosophical insights about the nature of idle time
- "Like waves on a shore, idle moments create space for AI assistance to flow in"

### Suggested Improvements

1. **Create requirements.txt**:
   ```
   openai>=1.0.0
   python-dotenv>=1.0.0  # For API key management
   rich>=13.0.0          # For beautiful terminal output
   ```

2. **Add Configuration File Support**:
   - Support for `.sage.yml` or `sage.toml` configuration
   - Environment-specific settings
   - Multiple session monitoring

3. **Implement Proper OpenAI Integration**:
   ```python
   def query_openai(prompt):
       """Query OpenAI with proper error handling and retry logic"""
       try:
           response = client.chat.completions.create(
               model="gpt-4",
               messages=[{"role": "user", "content": prompt}],
               temperature=0.7
           )
           return response.choices[0].message.content
       except Exception as e:
           print(f"AI had a hiccup: {e} 🤧")
           return "echo 'AI is taking a break, try again later!'"
   ```

4. **Add Logging with Style**:
   ```python
   from rich.console import Console
   from rich.table import Table
   
   console = Console()
   
   def log_pane_status(panes_status):
       """Display pane status in a beautiful table"""
       table = Table(title="Tmux Pane Status 🖥️")
       table.add_column("Pane ID", style="cyan")
       table.add_column("Status", style="green")
       table.add_column("Idle Time", style="yellow")
       # ... populate and display
   ```

5. **Add Test Suite**:
   ```python
   # tests/test_sage.py
   def test_is_idle_detects_bash_prompt():
       """Test that common shell prompts are detected as idle"""
       assert is_idle_with_content("user@host:~$ ")
       assert is_idle_with_content(">>> ")  # Python REPL
       assert is_idle_with_content("❯ ")     # Modern prompts
   ```

## Safety and Best Practices

1. **Command Validation**: Always validate AI-suggested commands before execution
2. **Sandboxing**: Consider running in a restricted environment first
3. **Logging**: Log all AI suggestions and executed commands for audit
4. **Rate Limiting**: Implement rate limiting for API calls
5. **Error Recovery**: Gracefully handle tmux session disconnections

## Development Workflow

1. **Before Making Changes**:
   - Check that tmux session exists: `tmux ls | grep my-session`
   - Ensure virtual environment is activated
   - Pull latest changes if working with version control

2. **Testing Changes**:
   - Create a test tmux session: `tmux new -s test-session`
   - Run with debug output: `python ss.py --debug`
   - Monitor behavior in real-time

3. **Committing Changes**:
   ```
   [Feature]: Add colorful pane status display 🌈
   - Added: Rich library for beautiful terminal tables
   - Updated: get_summary() to include ANSI colors
   - Fixed: Idle detection for zsh prompts
   Pro Tip: Now you can see which pane is thinking the hardest!
   Aye, Aye! 🚢
   ```

## Integration with Mem8

If integrating with the Mem8 memory system:
- Store command patterns as wave memories
- Learn from successful command executions
- Build context-aware suggestions based on past interactions
- Create "muscle memory" for common command sequences

## Future Roadmap

1. **Multi-Session Support**: Monitor multiple tmux sessions simultaneously
2. **Web Dashboard**: Real-time visualization of pane activity
3. **Plugin System**: Allow custom idle detectors and command processors
4. **Voice Integration**: Use Kokoro TTS to announce important events
5. **Distributed Mode**: Monitor tmux sessions across multiple machines

Remember: Sage is like a wise AI friend watching your terminal garden, ready to water it with helpful commands when things get too quiet! 🌱