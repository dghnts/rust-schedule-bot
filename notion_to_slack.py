import os
import datetime
from notion_client import Client as NotionClient
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv

load_dotenv()

notion = NotionClient(auth=os.getenv("NOTION_TOKEN"))
slack = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))
db_id = os.getenv("NOTION_DATABASE_ID")
channel = os.getenv("SLACK_CHANNEL")

today = datetime.date.today().isoformat()

db = notion.databases.retrieve(database_id=db_id)

for prop, config in db["properties"].items():
    print(f"{prop}: {config['type']}")

# 今日の学習タスクを取得
response = notion.databases.query(
    database_id=db_id,
    filter={
        "property": "日付",
        "date": {
            "equals": today
        }
    }
)


# Slack通知
for page in response["results"]:
    props = page["properties"]
    for k, v in props.items():
        print(k, v)
    title = props["章"][props["章"]["type"]][0]["text"]["content"]
    status = props["ステータス"]["status"]["name"]

    # if status == "完了":
    task = props["作業内容"]["rich_text"][0]["plain_text"]
    memo = props["メモ"]["rich_text"][0]["plain_text"] if props["メモ"]["rich_text"] else ""

    message = f"""
    ✅ Rust学習ステータス更新

    📘 章: {title}
    🗂 作業内容: {task}
    📌 ステータス: {status}
    📝 メモ: {memo}

    🔗 <https://www.notion.so/{db_id.replace('-', '')}|Notionページを開く>
    """

print(message)
print(channel)
try:
    slack.chat_postMessage(channel=channel, text=message)
    print("✅ Slack通知成功")
except SlackApiError as e:
    print("❌ Slack通知エラー:", e.response["error"])

with open("logs/execution.log", "a", encoding="utf-8") as f:
    f.write(f"[{datetime.datetime.now()}] Slack通知完了\n")
