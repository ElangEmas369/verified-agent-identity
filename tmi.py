#!/usr/bin/env python3
"""
TRADING MODE ISOLATED - Quick Access
Usage: python3 /root/TRADING_MODE_ISOLATED/tmi.py [command]

Commands:
  status    - Show bot status
  balance   - Check MEXC balance
  log       - Show recent log
  start     - Start bot
  stop      - Stop bot
  config    - Show full config
  api       - Show API keys
  files     - Show files map
  skills    - Show active skills
  help      - Show this help
"""

import json, os, sys, subprocess

CONFIG_PATH = "/root/TRADING_MODE_ISOLATED/config/MASTER_CONFIG.json"

def load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)

def show_status():
    config = load_config()
    result = subprocess.run(["ps", "aux"], capture_output=True, text=True)
    bot_lines = [l for l in result.stdout.split("\n") if "predator_v5" in l and "grep" not in l]
    
    print("="*60)
    print("🔍 TRADING MODE ISOLATED - STATUS")
    print("="*60)
    
    if bot_lines:
        for line in bot_lines:
            parts = line.split()
            pid = parts[1]
            print(f"✅ Bot RUNNING (PID: {pid})")
    else:
        print("❌ Bot NOT running")
    
    print(f"\n💰 Capital: ${config['trading_config']['capital']}")
    print(f"⚡ Leverage: {config['trading_config']['leverage']}x")
    print(f"📊 Session: {config['trading_config']['session']} ({config['trading_config']['session_wib']} WIB)")
    print(f"🎯 Session Active: {config['trading_config']['session_active']}")
    print(f"🔑 MEXC API: {config['api_keys']['mexc']['status']}")
    print(f"🤖 Primary Provider: {config['providers']['primary']}")

def show_balance():
    config = load_config()
    AK = config['api_keys']['mexc']['key']
    SK = config['api_keys']['mexc']['secret']
    BASE = config['api_keys']['mexc']['endpoints']['backup']
    
    import time, hmac, hashlib, requests
    
    ts = str(int(time.time() * 1000))
    sig = hmac.new(SK.encode(), (AK + ts).encode(), hashlib.sha256).hexdigest()
    H = {"ApiKey": AK, "Request-Time": ts, "Signature": sig, "Content-Type": "application/json"}
    
    print("="*60)
    print("💰 MEXC FUTURES BALANCE")
    print("="*60)
    
    try:
        r = requests.get(f"{BASE}/api/v1/private/account/assets", headers=H, timeout=10, verify=False)
        if r.status_code == 200 and r.json().get('success'):
            for a in r.json().get('data', []):
                if a.get('currency') == 'USDT':
                    print(f"   Equity: ${a.get('equity', 0)}")
                    print(f"   Available: ${a.get('availableBalance', 0)}")
                    print(f"   Unrealized PnL: ${a.get('unrealisedPnl', 0)}")
        else:
            print(f"   Error: {r.json().get('message', 'Unknown')}")
    except Exception as e:
        print(f"   Error: {e}")

def show_log(lines=30):
    log_file = load_config()['files_map']['log_file']
    print("="*60)
    print(f"📋 LAST {lines} LOG LINES")
    print("="*60)
    result = subprocess.run(["tail", "-n", str(lines), log_file], capture_output=True, text=True)
    print(result.stdout)

def show_config():
    config = load_config()
    print(json.dumps(config, indent=2))

def show_api():
    config = load_config()
    print("="*60)
    print("🔑 API KEYS")
    print("="*60)
    print(f"\nMEXC:")
    print(f"   Key: {config['api_keys']['mexc']['key'][:10]}...")
    print(f"   Secret: {config['api_keys']['mexc']['secret'][:10]}...")
    print(f"   Status: {config['api_keys']['mexc']['status']}")
    print(f"   Endpoints: {list(config['api_keys']['mexc']['endpoints'].values())}")
    
    print(f"\nProviders:")
    for name, p in config['providers'].items():
        if isinstance(p, dict) and 'status' in p:
            print(f"   {name}: {p['status']}")

def show_files():
    config = load_config()
    print("="*60)
    print("📁 FILES MAP")
    print("="*60)
    for name, path in config['files_map'].items():
        print(f"   {name}: {path}")

def show_skills():
    config = load_config()
    print("="*60)
    print("🧠 ACTIVE SKILLS")
    print("="*60)
    for skill in config['skills']['active']:
        print(f"   ✅ {skill}")
    print(f"\nDir: {config['skills']['dir']}")

def start_bot():
    print("="*60)
    print("🚀 STARTING BOT...")
    print("="*60)
    subprocess.Popen(
        ["python3", "-u", "/root/mexc-scalper/predator_v5.py"],
        cwd="/root/mexc-scalper",
        stdout=open("/tmp/predator_v5_live.log", "w"),
        stderr=subprocess.STDOUT
    )
    print("✅ Bot started! Check: python3 /root/TRADING_MODE_ISOLATED/tmi.py status")

def stop_bot():
    print("="*60)
    print("🛑 STOPPING BOT...")
    print("="*60)
    subprocess.run(["pkill", "-f", "predator_v5"])
    print("✅ Bot stopped!")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)
    
    cmd = sys.argv[1].lower()
    
    commands = {
        "status": show_status,
        "balance": show_balance,
        "log": show_log,
        "config": show_config,
        "api": show_api,
        "files": show_files,
        "skills": show_skills,
        "start": start_bot,
        "stop": stop_bot,
    }
    
    if cmd in commands:
        commands[cmd]()
    elif cmd == "help":
        print(__doc__)
    else:
        print(f"Unknown command: {cmd}")
        print("Use: python3 /root/TRADING_MODE_ISOLATED/tmi.py help")
