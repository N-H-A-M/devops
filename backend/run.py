import os
import sys
import subprocess
from alembic.config import Config
from alembic import command
import uvicorn

# 1. Base directories dynamically computed relative to run.py location
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BACKEND_DIR, ".."))

# Make sure backend modules (app, etc.) are importable
sys.path.insert(0, BACKEND_DIR)


def run_other_script(script_relative_path: str):
    """
    Executes setup scripts dynamically relative to PROJECT_ROOT.
    """
    script_path = os.path.abspath(os.path.join(PROJECT_ROOT, script_relative_path))
    
    print(f"--- Running Setup Script: {script_relative_path} ---")
    if not os.path.exists(script_path):
        print(f"Error: Script not found at {script_path}")
        sys.exit(1)

    if script_path.endswith('.sh'):
        try:
            subprocess.run(["chmod", "+x", script_path], check=True)
        except Exception:
            pass
        runner_cmd = ["/bin/bash", script_path]
    else:
        runner_cmd = [sys.executable, script_path]
        
    # Execute with working directory set to PROJECT_ROOT so .env is located automatically
    result = subprocess.run(runner_cmd, cwd=PROJECT_ROOT, capture_output=False)
    
    if result.returncode != 0:
        print(f"Error: Script {script_relative_path} failed with exit code {result.returncode}!")
        sys.exit(1)
        
    print(f"--- {script_relative_path} Completed Successfully ---")


def run_migrations():
    print("--- Starting Database Migrations ---")
    alembic_ini_path = os.path.join(BACKEND_DIR, "alembic.ini")
    
    if not os.path.exists(alembic_ini_path):
        raise FileNotFoundError(f"Could not find alembic.ini at {alembic_ini_path}")

    # Point Alembic directly to backend/migrations
    alembic_cfg = Config(alembic_ini_path)
    migrations_dir = os.path.join(BACKEND_DIR, "migrations")
    alembic_cfg.set_main_option("script_location", migrations_dir)

    try:
        command.upgrade(alembic_cfg, "head")
        print("--- Migrations completed successfully! ---")
    except Exception as e:
        print(f"Migration failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # 1. Run bash setup scripts via new 'deploy/scripts/' directory
    run_other_script("deploy/scripts/setup_db.sh")
    run_other_script("deploy/scripts/startup.sh")
    
    # 2. Run migrations dynamically
    run_migrations()
    
    # 3. Launch FastAPI server targeting app.main:app inside backend/
    print("--- Starting FastAPI Server ---")
    uvicorn.run("app.card_comparison:app", host="0.0.0.0", port=8000, reload=True)