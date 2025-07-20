#!/usr/bin/env python3
"""
Sage with M8 Integration - AI-powered tmux monitoring using 8q-is for context storage
"""

# Import the original sage module
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sage import *
from m8_integration import (
    M8Client, M8ContextManager, M8TmuxSession, integrate_m8_context
)
import asyncio
from rich.panel import Panel
from rich.text import Text

# Apply the M8 integration
integrate_m8_context(sys.modules['sage'])

class M8SageSession(SageSession):
    """Enhanced Sage session with 8q-is integration"""
    
    def __init__(self, persona_name: str = "claude-code", session: str = DEFAULT_SESSION):
        super().__init__(persona_name, session)
        
        # Initialize M8 components
        self.m8_client = M8Client()
        self.m8_context = M8ContextManager(Path.cwd())
        self.m8_tmux = M8TmuxSession(session, self.m8_context)
        
        # Connect to auctioneer for live commentary
        self.auctioneer_connected = False
        self._connect_auctioneer()
        
        console.print(Panel(
            Text.from_markup(
                "[bold cyan]🌊 M8-Enhanced Sage Active![/bold cyan]\n\n"
                "[green]Connected to 8q-is quantum context storage[/green]\n"
                f"[yellow]Session:[/yellow] {session}\n"
                f"[yellow]Persona:[/yellow] {persona_name}\n\n"
                "[dim]Context stored in wave-based memory patterns[/dim]"
            ),
            title="[bold magenta]Quantum Sage[/bold magenta]",
            border_style="bright_blue"
        ))
    
    def _connect_auctioneer(self):
        """Connect to the auctioneer live feed"""
        def on_auctioneer_event(event):
            # Display auctioneer commentary in the console
            if 'event' in event and 'AuctioneerComment' in event['event']:
                comment = event['event']['AuctioneerComment']
                excitement = comment.get('excitement_level', 5)
                message = comment.get('message', '')
                
                # Color based on excitement
                if excitement >= 8:
                    style = "bold red"
                elif excitement >= 6:
                    style = "bold yellow"
                else:
                    style = "cyan"
                
                console.print(f"\n[{style}]🎪 Auctioneer: {message}[/{style}]\n")
        
        try:
            # Run WebSocket connection in background
            asyncio.create_task(
                self.m8_context.m8_client.connect_auctioneer(on_auctioneer_event)
            )
            self.auctioneer_connected = True
        except Exception as e:
            console.print(f"[yellow]Note: Auctioneer not connected ({e})[/yellow]")
    
    def save_context(self):
        """Save context using 8q-is"""
        try:
            # Get current tmux state
            wave_signature = self.m8_tmux.save_session_state()
            
            if wave_signature:
                console.print(
                    f"[green]✓ Context saved to 8q-is[/green]\n"
                    f"[dim]Wave signature: {wave_signature[:16]}...[/dim]"
                )
                
                # Get stats from 8q-is
                stats = self.m8_client.get_stats()
                if stats:
                    total_containers = stats.get('total_containers', 0)
                    console.print(
                        f"[cyan]Total quantum containers: {total_containers}[/cyan]"
                    )
            else:
                console.print("[yellow]⚠ Failed to save context to 8q-is[/yellow]")
                
        except Exception as e:
            console.print(f"[red]Error saving context: {e}[/red]")
    
    def load_context(self):
        """Load context from 8q-is"""
        try:
            context = self.m8_tmux.restore_session_state()
            
            if context:
                console.print(
                    Panel(
                        Text.from_markup(
                            f"[bold green]✓ Context Restored[/bold green]\n\n"
                            f"[yellow]Session:[/yellow] {context.get('session', 'unknown')}\n"
                            f"[yellow]Timestamp:[/yellow] {context.get('timestamp', 'unknown')}\n"
                            f"[yellow]Panes:[/yellow] {context.get('pane_count', 0)}\n\n"
                            "[cyan]Recent Commands:[/cyan]\n" +
                            "\n".join(f"  • {cmd}" for cmd in context.get('recent_commands', [])[-5:])
                        ),
                        title="[bold blue]Quantum Memory Restored[/bold blue]",
                        border_style="green"
                    )
                )
            else:
                console.print("[yellow]No previous context found in quantum storage[/yellow]")
                
        except Exception as e:
            console.print(f"[red]Error loading context: {e}[/red]")
    
    def monitor_tmux(self):
        """Enhanced monitoring with quantum events"""
        console.print("\n[bold cyan]Starting quantum-enhanced tmux monitoring...[/bold cyan]\n")
        
        # Announce monitoring start
        self.m8_context.announce_event('monitoring_started', {
            'session': self.session,
            'persona': self.current_persona.name if self.current_persona else 'unknown'
        })
        
        # Load previous context
        self.load_context()
        
        # Run the original monitoring
        super().monitor_tmux()
        
        # Save context on exit
        self.save_context()


def main():
    """Run M8-enhanced Sage"""
    parser = argparse.ArgumentParser(
        description="M8-Enhanced Sage - Quantum tmux monitoring"
    )
    parser.add_argument(
        "persona",
        nargs="?",
        default="claude-code",
        help="Persona name to use (default: claude-code)"
    )
    parser.add_argument(
        "--session",
        default=os.environ.get("SAGE_SESSION", DEFAULT_SESSION),
        help=f"Tmux session name (default: {DEFAULT_SESSION})"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available personas"
    )
    parser.add_argument(
        "--m8-stats",
        action="store_true",
        help="Show 8q-is statistics"
    )
    
    args = parser.parse_args()
    
    # Handle special commands
    if args.list:
        manager = PersonaManager()
        personas = manager.list_personas()
        
        table = Table(title="Available Personas", show_header=True)
        table.add_column("Name", style="cyan")
        table.add_column("Model", style="green")
        table.add_column("Endpoint", style="yellow")
        
        for name, config in personas:
            table.add_row(
                name,
                config.get("model", "Unknown"),
                config.get("api_endpoint", "Unknown")[:30] + "..."
            )
        
        console.print(table)
        return
    
    if args.m8_stats:
        # Show 8q-is statistics
        client = M8Client()
        stats = client.get_stats()
        
        if stats:
            console.print(Panel(
                Text.from_markup(
                    f"[bold cyan]8q-is Quantum Storage Statistics[/bold cyan]\n\n"
                    f"[yellow]Total Containers:[/yellow] {stats.get('total_containers', 0)}\n"
                    f"[yellow]Memory Stats:[/yellow]\n"
                    f"  • Total Memories: {stats.get('mem8_stats', {}).get('total_memories', 0)}\n"
                    f"  • Grid Size: {stats.get('mem8_stats', {}).get('grid_dimensions', 'unknown')}\n\n"
                    "[green]Container Types:[/green]\n" +
                    "\n".join(f"  • {k}: {v}" for k, v in stats.get('type_counts', {}).items())
                ),
                title="[bold magenta]Quantum Context Stats[/bold magenta]",
                border_style="bright_blue"
            ))
        else:
            console.print("[red]Failed to connect to 8q-is server[/red]")
        return
    
    # Create and run M8-enhanced session
    try:
        session = M8SageSession(args.persona, args.session)
        session.monitor_tmux()
    except KeyboardInterrupt:
        console.print("\n[yellow]Monitoring stopped by user[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise


if __name__ == "__main__":
    main()