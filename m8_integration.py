#!/usr/bin/env python3
"""
M8 Integration for f8t - Connect f8t to 8q-is quantum context storage
"""

import httpx
import json
import zlib
import base64
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import logging
import asyncio
import websocket
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class M8Client:
    """Client for interacting with 8q-is M8C Nexus API"""
    base_url: str = "http://localhost:8420"
    timeout: int = 30
    
    def __post_init__(self):
        self.client = httpx.Client(timeout=self.timeout)
        self.async_client = httpx.AsyncClient(timeout=self.timeout)
    
    def upload_context(self, text: str, importance: int = 7) -> Dict[str, Any]:
        """Upload text context to M8 nexus"""
        try:
            # Upload as plain text
            files = {'file': ('context.txt', text.encode(), 'text/plain')}
            response = self.client.post(
                f"{self.base_url}/upload/text",
                files=files
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to upload context: {e}")
            raise
    
    def upload_marqant(self, marqant_data: bytes) -> Dict[str, Any]:
        """Upload Marqant compressed data"""
        try:
            files = {'file': ('data.mq', marqant_data, 'application/octet-stream')}
            response = self.client.post(
                f"{self.base_url}/upload/marqant",
                files=files
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to upload marqant: {e}")
            raise
    
    def retrieve_container(self, wave_signature: str) -> Optional[str]:
        """Retrieve container content by wave signature"""
        try:
            response = self.client.get(f"{self.base_url}/container/{wave_signature}")
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.error(f"Failed to retrieve container: {e}")
            return None
    
    def get_latest_context(self) -> Optional[Dict[str, Any]]:
        """Get the latest language memory context"""
        try:
            response = self.client.get(f"{self.base_url}/mem8/context/latest")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get latest context: {e}")
            return None
    
    def get_stats(self) -> Optional[Dict[str, Any]]:
        """Get nexus and MEM8 statistics"""
        try:
            response = self.client.get(f"{self.base_url}/mem8/stats")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return None
    
    async def connect_auctioneer(self, on_event_callback):
        """Connect to the auctioneer WebSocket for live events"""
        ws_url = f"ws://localhost:8420/auctioneer/live"
        
        def on_message(ws, message):
            try:
                data = json.loads(message)
                on_event_callback(data)
            except Exception as e:
                logger.error(f"Failed to process auctioneer message: {e}")
        
        def on_error(ws, error):
            logger.error(f"WebSocket error: {error}")
        
        def on_close(ws):
            logger.info("WebSocket connection closed")
        
        ws = websocket.WebSocketApp(
            ws_url,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close
        )
        
        # Run in background
        import threading
        wst = threading.Thread(target=ws.run_forever)
        wst.daemon = True
        wst.start()
        
        return ws


class M8ContextManager:
    """Enhanced context manager using 8q-is backend"""
    
    def __init__(self, project_dir: Path):
        self.project_dir = project_dir
        self.context_dir = project_dir / ".sage_proj"
        self.context_dir.mkdir(exist_ok=True)
        self.m8_client = M8Client()
        self.wave_signatures: Dict[str, str] = {}
        self._load_signature_cache()
    
    def _load_signature_cache(self):
        """Load cached wave signatures"""
        cache_file = self.context_dir / "wave_signatures.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    self.wave_signatures = json.load(f)
            except:
                self.wave_signatures = {}
    
    def _save_signature_cache(self):
        """Save wave signatures cache"""
        cache_file = self.context_dir / "wave_signatures.json"
        with open(cache_file, 'w') as f:
            json.dump(self.wave_signatures, f, indent=2)
    
    def save_context(self, context: Dict[str, Any]) -> Optional[str]:
        """Save context to 8q-is and return wave signature"""
        try:
            # Convert context to formatted text
            context_text = self._format_context(context)
            
            # Upload to 8q-is
            result = self.m8_client.upload_context(context_text, importance=8)
            
            if result.get('success'):
                wave_signature = result.get('wave_signature')
                if wave_signature:
                    # Cache the signature
                    timestamp = datetime.now().isoformat()
                    self.wave_signatures[timestamp] = wave_signature
                    self._save_signature_cache()
                    
                    # Also save a local reference
                    ref_file = self.context_dir / "latest_wave.txt"
                    ref_file.write_text(wave_signature)
                    
                    return wave_signature
            
            return None
        except Exception as e:
            logger.error(f"Failed to save context to 8q-is: {e}")
            return None
    
    def load_context(self) -> Optional[Dict[str, Any]]:
        """Load context from 8q-is"""
        try:
            # Try to get latest wave signature
            ref_file = self.context_dir / "latest_wave.txt"
            if ref_file.exists():
                wave_signature = ref_file.read_text().strip()
                content = self.m8_client.retrieve_container(wave_signature)
                if content:
                    return self._parse_context(content)
            
            # Fallback to latest language memory
            latest = self.m8_client.get_latest_context()
            if latest and latest.get('text'):
                return self._parse_context(latest['text'])
            
            return None
        except Exception as e:
            logger.error(f"Failed to load context from 8q-is: {e}")
            return None
    
    def _format_context(self, context: Dict[str, Any]) -> str:
        """Format context dict as text for storage"""
        lines = [
            "# Sage Context",
            f"## Session: {context.get('session', 'unknown')}",
            f"## Timestamp: {context.get('timestamp', datetime.now().isoformat())}",
            "",
            "### Recent Commands",
        ]
        
        for cmd in context.get('recent_commands', []):
            lines.append(f"- {cmd}")
        
        lines.extend([
            "",
            "### Current State",
            f"Panes: {context.get('pane_count', 0)}",
            f"Active Pane: {context.get('active_pane', 'unknown')}",
            f"Working Directory: {context.get('cwd', 'unknown')}",
        ])
        
        if context.get('custom_data'):
            lines.extend([
                "",
                "### Custom Data",
                json.dumps(context['custom_data'], indent=2)
            ])
        
        return "\n".join(lines)
    
    def _parse_context(self, text: str) -> Dict[str, Any]:
        """Parse text back into context dict"""
        context = {
            'session': 'unknown',
            'timestamp': datetime.now().isoformat(),
            'recent_commands': [],
            'pane_count': 0,
            'active_pane': 'unknown',
            'cwd': 'unknown',
            'custom_data': {}
        }
        
        lines = text.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if line.startswith('## Session:'):
                context['session'] = line.split(':', 1)[1].strip()
            elif line.startswith('## Timestamp:'):
                context['timestamp'] = line.split(':', 1)[1].strip()
            elif line.startswith('### Recent Commands'):
                current_section = 'commands'
            elif line.startswith('### Current State'):
                current_section = 'state'
            elif line.startswith('### Custom Data'):
                current_section = 'custom'
            elif current_section == 'commands' and line.startswith('- '):
                context['recent_commands'].append(line[2:])
            elif current_section == 'state':
                if line.startswith('Panes:'):
                    context['pane_count'] = int(line.split(':', 1)[1].strip())
                elif line.startswith('Active Pane:'):
                    context['active_pane'] = line.split(':', 1)[1].strip()
                elif line.startswith('Working Directory:'):
                    context['cwd'] = line.split(':', 1)[1].strip()
        
        return context
    
    def announce_event(self, event_type: str, data: Dict[str, Any]):
        """Send an event to the auctioneer for commentary"""
        # This would be used to announce tmux events to the live feed
        # For now, we'll just log it
        logger.info(f"Auctioneer event: {event_type} - {data}")


class M8TmuxSession:
    """Enhanced tmux session management with 8q-is integration"""
    
    def __init__(self, session_name: str, context_manager: M8ContextManager):
        self.session_name = session_name
        self.context_manager = context_manager
        self.m8_client = context_manager.m8_client
    
    def save_session_state(self):
        """Save current tmux session state to 8q-is"""
        import subprocess
        
        # Get tmux session info
        try:
            # List all panes with format
            result = subprocess.run(
                ['tmux', 'list-panes', '-t', self.session_name, '-F', 
                 '#{pane_id}:#{pane_current_path}:#{pane_current_command}'],
                capture_output=True, text=True
            )
            
            panes = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = line.split(':')
                    panes.append({
                        'id': parts[0],
                        'path': parts[1] if len(parts) > 1 else '',
                        'command': parts[2] if len(parts) > 2 else ''
                    })
            
            # Get recent commands from history
            history_result = subprocess.run(
                ['tmux', 'capture-pane', '-t', self.session_name, '-p', '-S', '-50'],
                capture_output=True, text=True
            )
            
            recent_commands = [
                line.strip() for line in history_result.stdout.split('\n')[-10:]
                if line.strip() and not line.startswith('#')
            ]
            
            # Build context
            context = {
                'session': self.session_name,
                'timestamp': datetime.now().isoformat(),
                'pane_count': len(panes),
                'panes': panes,
                'recent_commands': recent_commands,
                'active_pane': panes[0]['id'] if panes else 'unknown',
                'cwd': panes[0]['path'] if panes else 'unknown'
            }
            
            # Save to 8q-is
            wave_signature = self.context_manager.save_context(context)
            if wave_signature:
                logger.info(f"Session state saved with wave signature: {wave_signature}")
                
                # Announce to auctioneer
                self.context_manager.announce_event('session_saved', {
                    'session': self.session_name,
                    'wave_signature': wave_signature,
                    'pane_count': len(panes)
                })
            
            return wave_signature
            
        except Exception as e:
            logger.error(f"Failed to save session state: {e}")
            return None
    
    def restore_session_state(self, wave_signature: Optional[str] = None):
        """Restore tmux session state from 8q-is"""
        context = self.context_manager.load_context()
        if context:
            logger.info(f"Restored context for session: {context.get('session')}")
            # Here you could recreate panes, set directories, etc.
            return context
        return None


# Monkey-patch the sage.py ContextManager to use our M8 version
def integrate_m8_context(sage_module):
    """Replace sage's context manager with M8-integrated version"""
    original_init = sage_module.SageSession.__init__
    
    def new_init(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        # Replace context manager
        self.context_manager = M8ContextManager(Path.cwd())
        # Add tmux session manager
        self.tmux_manager = M8TmuxSession(self.session, self.context_manager)
    
    sage_module.SageSession.__init__ = new_init
    
    # Also patch save/load methods
    def new_save_context(self):
        return self.tmux_manager.save_session_state()
    
    def new_load_context(self):
        return self.tmux_manager.restore_session_state()
    
    sage_module.SageSession.save_context = new_save_context
    sage_module.SageSession.load_context = new_load_context


if __name__ == "__main__":
    # Test the integration
    import sage
    integrate_m8_context(sage)
    
    print("M8 Integration loaded! f8t will now use 8q-is for context storage.")
    print("Make sure 8q-is server is running at http://localhost:8420")