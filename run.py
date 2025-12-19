import os
import sys
import uvicorn

if __name__ == "__main__":
    # Force unbuffered output
    sys.stdout.reconfigure(line_buffering=True)
    
    print("--- Starting Application Wrapper ---", flush=True)
    
    # 1. Debug Environment
    port_env = os.environ.get("PORT")
    print(f"DEBUG: PORT environment variable raw value: '{port_env}'", flush=True)
    
    # 2. Parse Port
    port = 8080 # Default
    if port_env:
        try:
            port = int(port_env)
        except ValueError:
            print(f"WARNING: PORT '{port_env}' is not a valid integer. Using default 8080.", flush=True)
            port = 8080
    else:
         print("WARNING: PORT variable not found. Using default 8080.", flush=True)
         
    print(f"DEBUG: Final binding port: {port}", flush=True)
    
    try:
        # 3. Start Uvicorn
        print("INFO: Launching Uvicorn...", flush=True)
        uvicorn.run("app.main:app", host="0.0.0.0", port=port, log_level="info")
    except Exception as e:
        print(f"CRITICAL: Failed to start uvicorn: {e}", flush=True)
        sys.exit(1)
