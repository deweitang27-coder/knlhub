import subprocess

result = subprocess.run(
    ["wsl", "bash", "-c", 'sudo -u postgres psql -c "ALTER USER postgres WITH PASSWORD \'postgres\';"'],
    capture_output=True,
    text=True
)
print(result.stdout)
print(result.stderr)
