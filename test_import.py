import sys
import traceback

# Add backend to path
sys.path.append("./backend")

try:
    import app.main
    print("SUCCESS")
except Exception as e:
    print("FAILED")
    traceback.print_exc()
