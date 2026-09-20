import uvicorn
from multiprocessing import Process
import time
import requests

def run_server():
    uvicorn.run("app.main:app", host="127.0.0.1", port=8001, log_level="critical")

if __name__ == "__main__":
    p = Process(target=run_server)
    p.start()
    time.sleep(2)
    try:
        r = requests.get("http://127.0.0.1:8001/api/v1/auth/login")
        print("API is running, status:", r.status_code)
    except Exception as e:
        print("Error:", e)
    finally:
        p.terminate()
        p.join()
