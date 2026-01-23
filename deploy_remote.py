import paramiko
import time
import sys

HOST = "45.248.37.175"
USER = "root"
PASS = "39010302233Aaa"

def run_command(ssh, command, stream_output=True):
    print(f"\n[SERVER] Executing: {command}")
    stdin, stdout, stderr = ssh.exec_command(command)
    
    output = ""
    # Live output streaming
    while True:
        line = stdout.readline()
        if not line:
            break
        if stream_output:
            print(line.strip())
        output += line
        
    exit_status = stdout.channel.recv_exit_status()
    if exit_status != 0:
        err = stderr.read().decode()
        print(f"Error: {err}")
        return False, err
    return True, output

def main():
    print(f"🔄 Connecting to {HOST}...")
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(HOST, username=USER, password=PASS)
        print(f"✅ Connected successfully.")

        # 1. Locate Project
        # Try to find a directory that contains 'backend' and 'docker-compose.yml'
        search_cmd = "find ~ -type d -name 'backend' -maxdepth 3 2>/dev/null"
        success, out = run_command(ssh, search_cmd, stream_output=False)
        
        backend_dir = None
        if success and out.strip():
            # e.g. /root/miniapp/backend
            backend_dir = out.strip().split('\n')[0]
            print(f"📂 Found backend at: {backend_dir}")
        else:
            # Fallback
            print("⚠️ 'backend' directory not found via find. Checking 'miniapp' folder...")
            success, out = run_command(ssh, "ls -d ~/miniapp/backend", stream_output=False)
            if success:
                backend_dir = "~/miniapp/backend"
            else:
                print("❌ Could not locate project directory. Aborting.")
                return

        project_root = backend_dir.replace("/backend", "")
        
        # 2. Deployment Sequence
        # Try 'docker compose' (v2) first, fallback to 'docker-compose' if needed, but assuming v2 given the error.
        dc = "docker compose"
        
        commands = [
            f"cd {project_root} && git fetch --all",
            f"cd {project_root} && git reset --hard origin/main",
            f"cd {backend_dir} && {dc} down",
            f"cd {backend_dir} && {dc} build indicator-engine",
            f"cd {backend_dir} && {dc} up -d --remove-orphans",
            f"cd {backend_dir} && {dc} ps"
        ]

        for cmd in commands:
            success, _ = run_command(ssh, cmd)
            if not success:
                print("❌ Deployment failed.")
                break
        
        print("🚀 Deployment to remote server finished.")
        ssh.close()

    except Exception as e:
        print(f"❌ Connection failed: {e}")

if __name__ == "__main__":
    main()
