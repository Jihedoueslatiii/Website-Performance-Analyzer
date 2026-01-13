import os
import subprocess
import sys

# Set cache path
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = os.path.join(os.getcwd(), ".playwright")
print(f"Installing browsers to: {os.environ['PLAYWRIGHT_BROWSERS_PATH']}")

# Install browser
result = subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], 
                       capture_output=True, text=True)
print("STDOUT:", result.stdout)
print("STDERR:", result.stderr)
print("Return code:", result.returncode)
