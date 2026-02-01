#!/usr/bin/env python3
"""
Refactored IDP Filler Entrypoint.
Dispatches to either configure_participant.py or configure_dataspace.py
based on IDP_MODE environment variable.

Modes:
- 'organization' -> configure_participant.py
- 'daps'         -> configure_dataspace.py (Legacy name for Data Space Identity Provider)
"""

import os
import sys
import subprocess
from configure_dataspace import main as configure_dataspace_main
from configure_participant import main as configure_participant_main

def run_script(script_name, env_vars):
    # Construct absolute path in case CWD varies, though usually /home/app
    script_path = os.path.join(os.path.dirname(__file__), script_name)
    
    print(f"--- Launching {script_name} ---", file=sys.stderr)
    
    # Merge env
    current_env = os.environ.copy()
    current_env.update(env_vars)
    
    try:
        proc = subprocess.run([sys.executable, script_path], env=current_env, check=True)
        print(f"--- {script_name} completed successfully ---", file=sys.stderr)
    except subprocess.CalledProcessError as e:
        print(f"--- {script_name} failed with exit code {e.returncode} ---", file=sys.stderr)
        sys.exit(e.returncode)

def main():
    mode = os.environ.get("IDP_MODE", "daps")
    run_flag = os.environ.get("RUN_SCRIPT", "1")
    
    if run_flag != "1":
        print("RUN_SCRIPT is not 1, skipping execution.", file=sys.stderr)
        return

    if mode == "organization":
        print("=== Running Participant Organization Configuration ===")
        configure_participant_main()
        
    elif mode == "daps":        
        print("=== Running Data Space Identity Provider Configuration ===")
        configure_dataspace_main()
        
    else:
        print(f"Error: Unknown IDP_MODE '{mode}'. Supported: 'organization', 'daps'.", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
