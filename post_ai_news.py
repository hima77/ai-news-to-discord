import os, textwrap, time
import feedparser
import requests

# ---- 환경설정 ----
# 한국어 뉴스(구글 뉴스 RSS, 한국 로케일)
# 검색어: 인공지능 OR AI OR 생성형 AI
RSS_URL = (
    "https://news.google.com/rss/search?"
    "q=%EC%9D%B8%EA%B3%B5%EC%A7%80%EB%8A%A5%20OR%20AI%20OR%20%EC%83%9D%EC%84%B1%ED%98%95%20AI"
    "&hl=ko&gl=KR&ceid=KR:ko"
)
MAX_ITEMS = int(os.getenv("MAX_ITEMS", "4"))  # 보낼 뉴스 개수(기본 4)
WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]  # 깃허브 시크릿으로 주입

def fetch_news():
    feed = feedparser.parse(RSS_URL)
    entries = feed.entries[:MAX_ITEMS]
    items = []
    for e in entries:
        title = e.get("title", "").strip()
        link = e.get("link", "").strip()
        published = e.get("published", "").strip()
        items.append((title, link, published))
    return items

def build_message(items):
    if not items:
        return "오늘은 관련 뉴스를 찾지 못했습니다."

    lines = ["**📰 오늘의 AI 뉴스**"]
    for i, (title, link, published) in enumerate(items, start=1):
        # 디스코드 글자수 제한(2,000자) 내에서 안전하게
        safe_title = title.replace("\n", " ").strip()
        # 마크다운 링크 포맷
        lines.append(f"{i}. [{safe_title}]({link})")
    return "\n".join(lines)

def post_to_discord(content):
    payload = {"content": content}
    resp = requests.post(WEBHOOK_URL, json=payload, timeout=20)
    if resp.status_code >= 300:
        raise RuntimeError(f"Discord Webhook Error {resp.status_code}: {resp.text}")

def main():
    items = fetch_news()
    msg = build_message(items)
    # 너무 짧으면 디스코드가 스팸으로 보는 경우가 있어 약간의 지연을 둘 수도 있음
    time.sleep(1)
    post_to_discord(msg)

if __name__ == "__main__":
    main()

