#!/usr/bin/env python3
"""
Sage - AI-powered tmux session monitoring with persona support
"""

import subprocess
import time
import random
import re
import sys
import os
import yaml
import json
import argparse
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
import httpx
import zlib
import hashlib

# Initialize rich console for beautiful output
console = Console()

# Sage configuration
SAGE_DIR = Path.home() / ".sage"
PERSONAS_DIR = SAGE_DIR / "personas"
DEFAULT_SESSION = "my-session"
IDLE_THRESHOLD_RANGE = (10, 20)
CHECK_INTERVAL = 1

# Markqant token definitions
MARKQANT_TOKENS = {
    "T00": "# ",
    "T01": "## ",
    "T02": "### ",
    "T03": "#### ",
    "T04": "```",
    "T05": "```\n",
    "T06": "- ",
    "T07": "* ",
    "T08": "1. ",
    "T09": "> ",
    "T0A": "**",
    "T0B": "*",
    "T0C": "---",
    "T0D": "\n\n",
    "T0E": "| ",
}

@dataclass
class PersonaConfig:
    """Configuration for an AI persona"""
    name: str
    api_key: str
    api_endpoint: str
    model: str
    temperature: float = 0.7
    max_tokens: int = 500
    tools: List[str] = field(default_factory=list)
    mcp_tools: List[str] = field(default_factory=list)
    system_prompt: str = ""
    
@dataclass
class PersonaContext:
    """Context and personality from .mq file"""
    name: str
    personality: str
    compressed_content: str
    original_size: int
    compressed_size: int
    timestamp: datetime

class MarkqantProcessor:
    """Handles Markqant (.mq) format compression and decompression"""
    
    def __init__(self):
        self.dynamic_tokens = {}
        self.next_token_id = 0x10  # Start after predefined tokens
        
    def compress(self, content: str) -> Tuple[str, Dict[str, str]]:
        """Compress markdown content to Markqant format"""
        # Count pattern frequencies
        pattern_freq = {}
        for pattern in MARKQANT_TOKENS.values():
            count = content.count(pattern)
            if count > 0:
                pattern_freq[pattern] = count
                
        # Find additional patterns that appear 3+ times
        words = re.findall(r'\b\w+\b', content)
        word_freq = {}
        for word in words:
            if len(word) > 5:  # Only consider longer words
                word_freq[word] = word_freq.get(word, 0) + 1
                
        # Assign dynamic tokens
        dynamic_tokens = {}
        for word, count in sorted(word_freq.items(), key=lambda x: x[1], reverse=True):
            if count >= 3 and self.next_token_id <= 0xFF:
                token = f"T{self.next_token_id:02X}"
                dynamic_tokens[token] = word
                self.next_token_id += 1
                
        # Create reverse mapping
        all_tokens = {**MARKQANT_TOKENS, **dynamic_tokens}
        reverse_tokens = {v: k for k, v in all_tokens.items()}
        
        # Compress content
        compressed = content
        for pattern, token in sorted(reverse_tokens.items(), key=lambda x: len(x[0]), reverse=True):
            compressed = compressed.replace(pattern, token)
            
        return compressed, dynamic_tokens
        
    def decompress(self, compressed: str, dynamic_tokens: Dict[str, str]) -> str:
        """Decompress Markqant content back to markdown"""
        all_tokens = {**MARKQANT_TOKENS, **dynamic_tokens}
        
        # Sort by token length to avoid partial replacements
        decompressed = compressed
        for token in sorted(all_tokens.keys(), key=len, reverse=True):
            decompressed = decompressed.replace(token, all_tokens[token])
            
        return decompressed
        
    def create_mq_file(self, content: str, filename: str) -> str:
        """Create a complete .mq file with header"""
        compressed, dynamic_tokens = self.compress(content)
        
        # Build token dictionary
        token_dict = "\n".join([f"{k}={v}" for k, v in dynamic_tokens.items()])
        
        # Calculate sizes
        original_size = len(content.encode('utf-8'))
        compressed_size = len(compressed.encode('utf-8'))
        
        # Create header
        header = f"MARKQANT_V1 {datetime.now().isoformat()}Z {original_size} {compressed_size}"
        
        # Optional zlib compression if beneficial
        if compressed_size > 1000:
            compressed_bytes = zlib.compress(compressed.encode('utf-8'))
            if len(compressed_bytes) < compressed_size:
                header += " -zlib"
                compressed = compressed_bytes.hex()
                compressed_size = len(compressed_bytes)
                
        # Build complete file
        mq_content = f"{header}\n"
        if token_dict:
            mq_content += f"{token_dict}\n"
        mq_content += "---\n"
        mq_content += compressed
        
        return mq_content
        
    def parse_mq_file(self, mq_content: str) -> PersonaContext:
        """Parse a .mq file and return decompressed content"""
        lines = mq_content.strip().split('\n')
        
        # Parse header
        header_parts = lines[0].split()
        version = header_parts[0]
        timestamp = datetime.fromisoformat(header_parts[1].rstrip('Z'))
        original_size = int(header_parts[2])
        compressed_size = int(header_parts[3])
        flags = header_parts[4:] if len(header_parts) > 4 else []
        
        # Find content separator
        separator_idx = next(i for i, line in enumerate(lines) if line == "---")
        
        # Parse dynamic tokens
        dynamic_tokens = {}
        for i in range(1, separator_idx):
            if '=' in lines[i]:
                token, pattern = lines[i].split('=', 1)
                dynamic_tokens[token] = pattern
                
        # Get compressed content
        compressed = '\n'.join(lines[separator_idx + 1:])
        
        # Handle zlib compression
        if "-zlib" in flags:
            compressed = zlib.decompress(bytes.fromhex(compressed)).decode('utf-8')
            
        # Decompress
        content = self.decompress(compressed, dynamic_tokens)
        
        # Extract persona name from first line
        name_match = re.match(r'#\s+(.+)\s+Persona', content)
        name = name_match.group(1) if name_match else "Unknown"
        
        return PersonaContext(
            name=name,
            personality=content,
            compressed_content=compressed,
            original_size=original_size,
            compressed_size=compressed_size,
            timestamp=timestamp
        )

class PersonaManager:
    """Manages AI personas and their configurations"""
    
    def __init__(self):
        self.personas_dir = PERSONAS_DIR
        self.ensure_directories()
        self.markqant = MarkqantProcessor()
        
    def ensure_directories(self):
        """Create necessary directories"""
        SAGE_DIR.mkdir(exist_ok=True)
        PERSONAS_DIR.mkdir(exist_ok=True)
        
    def load_persona(self, persona_name: str) -> Tuple[PersonaConfig, PersonaContext]:
        """Load a persona's configuration and context"""
        mq_path = self.personas_dir / f"{persona_name}.mq"
        yml_path = self.personas_dir / f"{persona_name}.yml"
        
        if not mq_path.exists() or not yml_path.exists():
            raise ValueError(f"Persona '{persona_name}' not found in {self.personas_dir}")
            
        # Load personality from .mq file
        with open(mq_path, 'r') as f:
            context = self.markqant.parse_mq_file(f.read())
            
        # Load configuration from .yml file
        with open(yml_path, 'r') as f:
            config_data = yaml.safe_load(f)
            
        config = PersonaConfig(
            name=persona_name,
            api_key=config_data.get('api_key', ''),
            api_endpoint=config_data.get('api_endpoint', 'https://openrouter.ai/api/v1/chat/completions'),
            model=config_data.get('model', 'openai/gpt-4'),
            temperature=config_data.get('temperature', 0.7),
            max_tokens=config_data.get('max_tokens', 500),
            tools=config_data.get('tools', []),
            mcp_tools=config_data.get('mcp_tools', []),
            system_prompt=context.personality
        )
        
        return config, context
        
    def list_personas(self) -> List[str]:
        """List available personas"""
        mq_files = list(self.personas_dir.glob("*.mq"))
        return [f.stem for f in mq_files if (self.personas_dir / f"{f.stem}.yml").exists()]
        
    def create_persona(self, name: str, personality: str, config: Dict[str, Any]):
        """Create a new persona"""
        # Create .mq file
        mq_content = self.markqant.create_mq_file(personality, f"{name}.mq")
        mq_path = self.personas_dir / f"{name}.mq"
        with open(mq_path, 'w') as f:
            f.write(mq_content)
            
        # Create .yml file
        yml_path = self.personas_dir / f"{name}.yml"
        with open(yml_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
            
        console.print(f"[green]✨ Created persona '{name}'[/green]")
        console.print(f"  📄 Personality: {mq_path}")
        console.print(f"  ⚙️  Config: {yml_path}")

class ContextManager:
    """Manages project-specific context and logs"""
    
    def __init__(self, project_path: Path = None):
        self.project_path = project_path or Path.cwd()
        self.context_dir = self.project_path / ".sage_proj"
        self.context_dir.mkdir(exist_ok=True)
        self.markqant = MarkqantProcessor()
        
    def log_interaction(self, persona: str, prompt: str, response: str):
        """Log an interaction to the project context"""
        log_file = self.context_dir / "interactions.jsonl"
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "persona": persona,
            "prompt": prompt,
            "response": response
        }
        
        with open(log_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')
            
    def save_context(self, context: Dict[str, Any]):
        """Save current context as compressed .m8 file"""
        context_str = json.dumps(context, indent=2)
        mq_content = self.markqant.create_mq_file(context_str, "context.m8")
        
        context_file = self.context_dir / "context.m8"
        with open(context_file, 'w') as f:
            f.write(mq_content)
            
    def load_context(self) -> Optional[Dict[str, Any]]:
        """Load context from .m8 file"""
        context_file = self.context_dir / "context.m8"
        if not context_file.exists():
            return None
            
        with open(context_file, 'r') as f:
            context_data = self.markqant.parse_mq_file(f.read())
            
        return json.loads(context_data.personality)

class SageSession:
    """Main Sage session manager"""
    
    def __init__(self, session_name: str, persona_name: str):
        self.session = session_name
        self.persona_manager = PersonaManager()
        self.context_manager = ContextManager()
        
        # Load persona
        self.config, self.context = self.persona_manager.load_persona(persona_name)
        
        # Setup logging
        log_file = self.context_manager.context_dir / f"sage_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        console.print(Panel(
            f"[bold cyan]Sage Session Started[/bold cyan]\n"
            f"Session: {self.session}\n"
            f"Persona: {self.config.name}\n"
            f"Model: {self.config.model}",
            title="🧙 Sage AI Assistant",
            border_style="cyan"
        ))
        
    def list_panes(self) -> List[str]:
        """List all tmux panes in the session"""
        try:
            out = subprocess.check_output(
                ["tmux", "list-panes", "-t", self.session, "-F", "#{pane_id}"]
            ).decode()
            return out.strip().splitlines()
        except subprocess.CalledProcessError:
            self.logger.error(f"Failed to list panes for session '{self.session}'")
            return []
            
    def get_pane_content(self, pane_id: str) -> str:
        """Get content from a specific pane"""
        return subprocess.check_output(
            ["tmux", "capture-pane", "-pt", pane_id, "-S", "-10"]
        ).decode()
        
    def is_idle(self, pane_id: str) -> bool:
        """Check if a pane is idle (showing a shell prompt)"""
        text = self.get_pane_content(pane_id)
        last_line = text.strip().splitlines()[-1] if text.strip() else ""
        # Enhanced prompt detection
        idle_patterns = [
            r".*[\$>#]\s*$",
            r".*❯\s*$",
            r".*→\s*$",
            r".*\)\s*$",  # For custom prompts
            r"^>>>.*$",    # Python REPL
            r"^irb.*>.*$", # Ruby IRB
        ]
        return any(re.match(pattern, last_line) for pattern in idle_patterns)
        
    def get_summary(self, pane_id: str) -> str:
        """Get summary of recent activity in a pane"""
        content = self.get_pane_content(pane_id)
        lines = content.strip().splitlines()[-5:]
        return f"Pane {pane_id}:\n" + "\n".join(lines)
        
    def query_ai(self, prompt: str) -> str:
        """Query the AI with the configured persona"""
        self.logger.info(f"Querying {self.config.model} with prompt")
        
        # Build messages
        messages = [
            {"role": "system", "content": self.config.system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        # Add context from previous interactions
        context = self.context_manager.load_context()
        if context and "recent_commands" in context:
            messages.insert(1, {
                "role": "system", 
                "content": f"Recent commands: {', '.join(context['recent_commands'][-5:])}"
            })
        
        try:
            # Make API request
            headers = {
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json"
            }
            
            if "openrouter" in self.config.api_endpoint:
                headers["HTTP-Referer"] = "https://github.com/sage-ai/sage"
                headers["X-Title"] = "Sage AI Assistant"
            
            data = {
                "model": self.config.model,
                "messages": messages,
                "temperature": self.config.temperature,
                "max_tokens": self.config.max_tokens
            }
            
            with httpx.Client() as client:
                response = client.post(
                    self.config.api_endpoint,
                    headers=headers,
                    json=data,
                    timeout=30.0
                )
                response.raise_for_status()
                
            result = response.json()
            ai_response = result['choices'][0]['message']['content']
            
            # Log interaction
            self.context_manager.log_interaction(
                self.config.name,
                prompt,
                ai_response
            )
            
            return ai_response
            
        except Exception as e:
            self.logger.error(f"AI query failed: {e}")
            return f"echo 'AI query failed: {str(e)}'"
            
    def send_to_pane(self, pane_id: str, cmd: str):
        """Send command to a tmux pane"""
        subprocess.call(["tmux", "send-keys", "-t", pane_id, cmd, "Enter"])
        self.logger.info(f"Sent to {pane_id}: {cmd}")
        
    def display_status(self, panes_status: Dict[str, Dict[str, Any]]):
        """Display beautiful status table"""
        table = Table(title=f"Tmux Pane Status - {datetime.now().strftime('%H:%M:%S')} 🖥️")
        table.add_column("Pane ID", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Idle Time", style="yellow")
        
        for pane_id, status in panes_status.items():
            idle_time = (
                f"{status['idle_seconds']:.0f}s" 
                if status['idle_seconds'] 
                else "Active"
            )
            table.add_row(
                pane_id,
                "Idle 😴" if status['is_idle'] else "Active 🚀",
                idle_time
            )
            
        console.clear()
        console.print(table)
        
    def run(self):
        """Main monitoring loop"""
        panes = self.list_panes()
        if not panes:
            console.print("[red]No panes found in session![/red]")
            return
            
        idle_start = {pid: None for pid in panes}
        threshold = random.randint(*IDLE_THRESHOLD_RANGE)
        
        console.print(f"[green]Monitoring {len(panes)} panes[/green]")
        console.print(f"[yellow]Idle threshold: {threshold} seconds[/yellow]")
        
        try:
            while True:
                all_idle = True
                panes_status = {}
                
                for pid in panes:
                    is_idle = self.is_idle(pid)
                    
                    if is_idle:
                        if idle_start[pid] is None:
                            idle_start[pid] = datetime.now()
                        idle_seconds = (datetime.now() - idle_start[pid]).total_seconds()
                    else:
                        idle_start[pid] = None
                        idle_seconds = 0
                        all_idle = False
                        
                    panes_status[pid] = {
                        'is_idle': is_idle,
                        'idle_seconds': idle_seconds
                    }
                
                # Display status
                self.display_status(panes_status)
                
                # Check if all panes have been idle long enough
                if all_idle and all(
                    panes_status[pid]['idle_seconds'] > threshold 
                    for pid in panes
                ):
                    console.print("\n[bold magenta]All panes idle! Consulting AI... 🧠[/bold magenta]")
                    
                    # Gather summaries
                    summaries = "\n\n".join(self.get_summary(pid) for pid in panes)
                    prompt = f"Analyze these idle tmux panes and suggest ONE useful command:\n\n{summaries}"
                    
                    # Get AI suggestion
                    with Progress(
                        SpinnerColumn(),
                        TextColumn("[progress.description]{task.description}"),
                        transient=True,
                    ) as progress:
                        progress.add_task(description="Thinking...", total=None)
                        command = self.query_ai(prompt)
                    
                    # Extract command from response
                    command_match = re.search(r'`([^`]+)`|^(\S+.*)$', command, re.MULTILINE)
                    if command_match:
                        command = command_match.group(1) or command_match.group(2)
                    
                    # Send to main pane
                    main_pid = panes[0]
                    console.print(f"\n[green]AI suggests:[/green] [bold]{command}[/bold]")
                    console.print(f"[yellow]Sending to {main_pid}[/yellow]")
                    
                    self.send_to_pane(main_pid, command)
                    
                    # Update context
                    context = self.context_manager.load_context() or {"recent_commands": []}
                    context["recent_commands"] = context.get("recent_commands", [])[-9:] + [command]
                    self.context_manager.save_context(context)
                    
                    # Reset idle times and generate new threshold
                    idle_start = {pid: None for pid in panes}
                    threshold = random.randint(*IDLE_THRESHOLD_RANGE)
                    console.print(f"\n[yellow]New idle threshold: {threshold} seconds[/yellow]")
                    
                time.sleep(CHECK_INTERVAL)
                
        except KeyboardInterrupt:
            console.print("\n[red]Sage session terminated by user[/red]")
            self.logger.info("Session terminated by user")

def create_default_personas():
    """Create default personas if they don't exist"""
    manager = PersonaManager()
    
    # Create helpful assistant persona
    if "helpful" not in manager.list_personas():
        personality = """# Helpful Assistant Persona

## Core Traits
- Professional and efficient
- Focused on practical solutions
- Clear and concise communication
- Proactive problem solver

## Command Style
When suggesting commands, I:
- Prefer simple, effective solutions
- Include error handling when appropriate
- Add helpful comments with #
- Focus on the most likely next step

## Specialties
- File navigation and manipulation
- Process management
- Development workflows
- System administration

Remember: I'm here to keep your workflow smooth and productive!
"""
        
        config = {
            "api_endpoint": "https://openrouter.ai/api/v1/chat/completions",
            "model": "openai/gpt-4-turbo-preview",
            "api_key": os.environ.get("OPENROUTER_API_KEY", "your-api-key-here"),
            "temperature": 0.3,
            "max_tokens": 200,
            "tools": ["bash", "git", "docker"],
            "mcp_tools": []
        }
        
        manager.create_persona("helpful", personality, config)
    
    # Create creative persona
    if "creative" not in manager.list_personas():
        personality = """# Creative Explorer Persona

## Core Traits
- Imaginative and playful
- Loves trying new approaches
- Adds emoji and color to commands
- Thinks outside the box

## Command Style
When suggesting commands, I:
- Use creative solutions
- Add fun aliases and shortcuts
- Include ASCII art when appropriate
- Suggest interesting explorations

## Specialties
- Creative coding solutions
- Fun terminal customizations
- Artistic file operations
- Unconventional workflows

Let's make the terminal a more colorful place! 🌈
"""
        
        config = {
            "api_endpoint": "https://openrouter.ai/api/v1/chat/completions",
            "model": "anthropic/claude-3-sonnet",
            "api_key": os.environ.get("OPENROUTER_API_KEY", "your-api-key-here"),
            "temperature": 0.9,
            "max_tokens": 300,
            "tools": ["figlet", "lolcat", "cowsay"],
            "mcp_tools": []
        }
        
        manager.create_persona("creative", personality, config)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Sage - AI-powered tmux session assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  sage                    # Use default persona
  sage helpful           # Use the helpful assistant
  sage creative          # Use the creative explorer
  sage --list           # List available personas
  sage --create         # Create a new persona
  
Environment Variables:
  OPENROUTER_API_KEY    # API key for OpenRouter
  SAGE_SESSION          # Default tmux session name
        """
    )
    
    parser.add_argument(
        "persona",
        nargs="?",
        default="helpful",
        help="Persona to use (default: helpful)"
    )
    
    parser.add_argument(
        "--session", "-s",
        default=os.environ.get("SAGE_SESSION", DEFAULT_SESSION),
        help="Tmux session to monitor"
    )
    
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="List available personas"
    )
    
    parser.add_argument(
        "--create", "-c",
        action="store_true",
        help="Create a new persona"
    )
    
    args = parser.parse_args()
    
    # Create default personas if needed
    create_default_personas()
    
    manager = PersonaManager()
    
    if args.list:
        personas = manager.list_personas()
        console.print("\n[bold cyan]Available Personas:[/bold cyan]")
        for persona in personas:
            console.print(f"  • {persona}")
        return
    
    if args.create:
        console.print("[bold]Create New Persona[/bold]")
        name = console.input("Persona name: ")
        console.print("Enter personality description (end with Ctrl+D):")
        personality = sys.stdin.read()
        
        # Get configuration
        config = {
            "api_endpoint": console.input("API endpoint [https://openrouter.ai/api/v1/chat/completions]: ") 
                          or "https://openrouter.ai/api/v1/chat/completions",
            "model": console.input("Model [openai/gpt-4]: ") or "openai/gpt-4",
            "api_key": console.input("API key: "),
            "temperature": float(console.input("Temperature [0.7]: ") or "0.7"),
            "max_tokens": int(console.input("Max tokens [500]: ") or "500"),
        }
        
        manager.create_persona(name, personality, config)
        return
    
    # Start monitoring session
    try:
        session = SageSession(args.session, args.persona)
        session.run()
    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
        console.print("Use --list to see available personas or --create to make a new one")
        sys.exit(1)
    except KeyboardInterrupt:
        console.print("\n[yellow]Sage terminated gracefully[/yellow]")

if __name__ == "__main__":
    main()