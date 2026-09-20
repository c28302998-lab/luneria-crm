import requests
import re

html = requests.get("https://luneryagency.vercel.app/login").text
chunks = re.findall(r'src="/_next/static/chunks/([^"]+)"', html)

found_localhost = False
found_onrender = False

for chunk in set(chunks):
    url = f"https://luneryagency.vercel.app/_next/static/chunks/{chunk}"
    js = requests.get(url).text
    if "localhost:8000" in js:
        print(f"Found localhost in {chunk}!")
        found_localhost = True
    if "onrender.com" in js:
        print(f"Found onrender in {chunk}!")
        found_onrender = True

if not found_localhost and not found_onrender:
    print("Neither found in chunks.")
