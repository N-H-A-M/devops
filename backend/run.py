# /home/devwork/devops project/devops/run.py
import os
import sys, subprocess
from alembic.config import Config
from alembic import command
import uvicorn

# 1. Force Python to see the root directory (fixes ModuleNotFoundError)
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def run_other_script(script_relative_path: str):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.abspath(os.path.join(base_dir, script_relative_path))
    
    print(f"--- Running Setup Script: {script_relative_path} ---")
    if not os.path.exists(script_path):
        print(f"Error: Script not found at {script_path}")
        sys.exit(1)
        
    if script_path.endswith('.sh'):
        # Make sure the shell script is executable (for Linux/macOS)
        try:
            subprocess.run(["chmod", "+x", script_path], check=True)
        except Exception:
            pass
        # Run it strictly with Bash
        runner_cmd = ["/bin/bash", script_path]
    else:
        # Run Python scripts with the current Python executable
        runner_cmd = [sys.executable, script_path]

    # Run the script as a subprocess using the current Python environment
    result = subprocess.run(runner_cmd, cwd=base_dir, capture_output=False)
    
    if result.returncode != 0:
        print(f"Error: Script {script_relative_path} failed with exit code {result.returncode}!")
        sys.exit(1) # Stop the app from starting if setup fails
    print(f"--- {script_relative_path} Completed Successfully ---")



def run_migrations():
    print("--- Starting Database Migrations ---")
    
    # 2. Locate the alembic.ini relative to this script
    base_dir = os.path.dirname(os.path.abspath(__file__))
    alembic_ini_path = os.path.join(base_dir, "src", "card_src", "alembic.ini")
    
    if not os.path.exists(alembic_ini_path):
        raise FileNotFoundError(f"Could not find alembic.ini at {alembic_ini_path}")

    # 3. Load configuration and point it explicitly to the migrations folder
    alembic_cfg = Config(alembic_ini_path)
    migrations_dir = os.path.join(base_dir, "src", "card_src", "migrations")
    alembic_cfg.set_main_option("script_location", migrations_dir)

    # 4. Run the upgrade
    try:
        command.upgrade(alembic_cfg, "head")
        print("--- Migrations completed successfully! ---")
    except Exception as e:
        print(f"Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Run the migrations first
    run_other_script("config/scripts/setup_db.sh")
    run_other_script("config/scripts/startup.sh")
    run_migrations()
    
    # Start the FastAPI server
    print("--- Starting FastAPI Server ---")
    # Change "src.card_src.main:app" to match your actual main file import path
    uvicorn.run("src.card_src.main:app", host="0.0.0.0", port=8000, reload=True)

