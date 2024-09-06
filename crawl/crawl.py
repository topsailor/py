import requests  # pip install requests 필요
from bs4 import BeautifulSoup  # pip install bs4

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36"
}
data = requests.get("https://www.naver.com", headers=headers)
soup = BeautifulSoup(data.text, "html.parser")

blind = soup.select("body .blind")

# 결과를 파일로 저장
with open("scraping_results.txt", "a", encoding="utf-8") as file:
    for b in blind:
        file.write(b.text + "\n")
