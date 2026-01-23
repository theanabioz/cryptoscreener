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
    print(f"🔥 STARTING FULL BACKEND REBUILD ON {HOST}...")
    print("⚠️  This will delete the 'backend' folder on the server and rebuild from Git.")
    print("🛡️  Database volumes will be PRESERVED.")
    
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(HOST, username=USER, password=PASS)
        print(f"✅ Connected successfully.")

        # 1. Locate Project
        backend_dir = "/root/cryptoscreener/backend"
        project_root = "/root/cryptoscreener"
        
        # 2. Rebuild Sequence
        dc = "docker compose"
        
        commands = [
            # 1. Stop everything safely
            f"cd {backend_dir} && {dc} down",
            
            # 2. NUCLEAR OPTION: Delete the dirty backend folder
            # We move to root, delete backend, then verify it's gone
            f"cd {project_root} && rm -rf backend",
            f"echo '🗑️ Backend folder deleted.'",
            
            # 3. Restore Clean State from GitHub
            f"cd {project_root} && git fetch --all",
            f"cd {project_root} && git reset --hard origin/main",
            f"echo '✨ Code restored from GitHub.'",
            
            # 4. Verify local lib presence (Debug step)
            f"ls -l {backend_dir}/pandas_ta-0.4.71b0.tar.gz",
            
            # 5. Clean Docker Builder Cache (Fixes pip cache issues)
            f"docker builder prune -f",
            
            # 6. Build and Start
            # We force build to ensure the local tarball is used
            f"cd {backend_dir} && {dc} up -d --build --remove-orphans",
            
            # 7. Check Status
            f"cd {backend_dir} && {dc} ps"
        ]

        for cmd in commands:
            success, _ = run_command(ssh, cmd)
            if not success:
                print("❌ REBUILD FAILED. Please check logs.")
                break
        
        print("🚀 Full Rebuild Complete!")
        ssh.close()

    except Exception as e:
        print(f"❌ Connection failed: {e}")

if __name__ == "__main__":
    main()