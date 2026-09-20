with open("app/main.py", "r") as f:
    content = f.read()

content = "from dotenv import load_dotenv\nload_dotenv()\n" + content

with open("app/main.py", "w") as f:
    f.write(content)
