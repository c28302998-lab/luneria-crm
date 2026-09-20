import requests
import re

html = requests.get("https://luneryagency.vercel.app/login").text
chunks = re.findall(r'src="/_next/static/chunks/([^"]+)"', html)

for chunk in set(chunks):
    url = f"https://luneryagency.vercel.app/_next/static/chunks/{chunk}"
    js = requests.get(url).text
    if "localhost" in js:
        print(f"Found localhost in {chunk}!")
    if "onrender" in js:
        print(f"Found onrender in {chunk}!")
