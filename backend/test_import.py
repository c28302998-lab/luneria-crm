import sys
import traceback

sys.path.append(".")

try:
    import app.main
    print("SUCCESS")
except Exception as e:
    print("FAILED")
    traceback.print_exc()
