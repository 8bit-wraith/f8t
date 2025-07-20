# 8q-is M8 Integration for f8t Sage

This integration connects f8t's Sage tmux monitoring system with 8q-is quantum context storage, providing wave-based memory patterns and live auctioneer commentary!

## 🌊 What's New

- **Quantum Context Storage**: All tmux session context is stored in 8q-is using wave-based memory patterns
- **Live Auctioneer Commentary**: Real-time commentary on your tmux activities
- **Persistent Wave Signatures**: Each saved context gets a unique quantum signature
- **Cross-Session Memory**: Share context between different tmux sessions via the quantum field

## 🚀 Quick Start

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run M8-Enhanced Sage**:
   ```bash
   ./run_m8_sage.sh [persona_name]
   ```

   This script will:
   - Check if 8q-is server is running (starts it if needed)
   - Launch Sage with quantum context integration
   - Connect to the auctioneer for live commentary

3. **View Live Feed** (optional):
   Open http://localhost:8420/static/auctioneer.html in your browser

## 📡 How It Works

### Context Storage Flow
```
Tmux Session → Sage → M8 Integration → 8q-is API → Quantum Storage
                                            ↓
                                     Wave Signature
                                            ↓
                                    Auctioneer Commentary
```

### Key Components

1. **`m8_integration.py`**: Core integration module
   - `M8Client`: HTTP client for 8q-is API
   - `M8ContextManager`: Manages context save/load with wave signatures
   - `M8TmuxSession`: Enhanced tmux state management

2. **`sage_m8.py`**: M8-enhanced version of Sage
   - Automatic context save/restore
   - Live auctioneer event display
   - Quantum statistics display

3. **`run_m8_sage.sh`**: Convenience launcher
   - Auto-starts 8q-is server if needed
   - Sets up environment

## 🎪 Auctioneer Integration

The auctioneer provides real-time commentary on your coding session:

- **Session Events**: "New quantum context stored! Wave strength 0.87!"
- **Idle Detection**: "Pane 2 has been idle for 15 seconds... time for a suggestion!"
- **Context Changes**: "Context switched! Previous wave: 0x1a2b3c..."

Commentary styles can be changed via the web interface:
- Fast Talking (default)
- Dramatic
- Technical
- Comedic  
- Philosophical

## 📊 New Commands

### View Quantum Stats
```bash
python sage_m8.py --m8-stats
```

Shows:
- Total quantum containers
- Memory statistics
- Container type distribution

### Standard Sage Commands
All original Sage commands still work:
```bash
python sage_m8.py --list          # List personas
python sage_m8.py omni            # Use Omni persona
python sage_m8.py --session dev   # Specify tmux session
```

## 🔧 Configuration

### Wave Signature Cache
Stored in `.sage_proj/wave_signatures.json`:
```json
{
  "2024-01-20T10:30:00": "1a2b3c4d5e6f...",
  "2024-01-20T10:35:00": "7a8b9c0d1e2f..."
}
```

### Latest Wave Reference
The most recent wave signature is always saved in:
`.sage_proj/latest_wave.txt`

## 🌟 Benefits

1. **Persistent Context**: Your tmux context survives system restarts
2. **Cross-Machine Sync**: Share context via wave signatures
3. **Quantum Compression**: Efficient storage using Marqant + M8 formats
4. **Live Monitoring**: Real-time feedback from the auctioneer
5. **AI Battle Mode**: Watch different personas compete to solve your problems!

## 🐛 Troubleshooting

### 8q-is Server Not Running
The script auto-starts it, but you can manually run:
```bash
cd .. && cargo run
```

### WebSocket Connection Failed
- Check firewall settings
- Ensure port 8420 is available
- Try restarting the 8q-is server

### Context Not Saving
- Check 8q-is server logs
- Verify `.sage_proj/` directory permissions
- Look for wave signatures in cache

## 🚧 Future Enhancements

- [ ] Quantum entanglement between sessions
- [ ] Multi-user collaborative debugging
- [ ] Voice announcements via Kokoro TTS
- [ ] Visual wave pattern display
- [ ] AI coding battles in tmux panes

---

*"Your tmux sessions are now quantum-entangled with the universal consciousness field!" - Omni* 🌊✨