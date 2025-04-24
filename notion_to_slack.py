import os
import datetime
from logging import debug
from collections import defaultdict

from notion_client import Client as NotionClient
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv

from tasks import Task

# 環境変数の読み込み
load_dotenv()

# 環境変数を取り込む
notion = NotionClient(auth=os.getenv("NOTION_TOKEN"))
slack = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))
db_id = os.getenv("NOTION_DATABASE_ID")
channel = os.getenv("SLACK_CHANNEL")

# 今日の日付を取得
today = datetime.date.today().isoformat()

db = notion.databases.retrieve(database_id=db_id)

'''
for prop, config in db["properties"].items():
    print(f"{prop}: {config['type']}")
'''

# 今日の学習タスクを取得
response = notion.databases.query(
    database_id=db_id,
    filter={
        "and": [
            {
                "property": "date",
                "date": {
                    "on_or_before": today
                }
            }
            ,
            {
                "property": "status",
                "status": {
                    "does_not_equal": "完了"
                }
            }

        ]
    }
)

args = defaultdict(str)

tasks_grouped_by_chapter = defaultdict(list)

# Slack通知
for db_row in response["results"]:
    # print(db_row["properties"])
    task = Task(db_row)

    # print(task.chapter)

    tasks_grouped_by_chapter[task.chapter].append([task.task, task.memo])

task_count = len(response["results"]) # taskの個数

work = "" # task一覧

for chapter,tasks in sorted(tasks_grouped_by_chapter.items(),key=lambda c:c[0]):
    work += chapter
    work += "\n"

    for task in tasks:
        work += f"- {task[0]} \n memo : {task[1]} \n"
    work += "\n"

message = f"""
📁 {today}：今日のTask\n
{work}
今日は{task_count}個のtaskがあります。
頑張りましょう！ \n

🔗 <https://doc.rust-jp.rs/book-ja/ch01-00-getting-started.html|テキストを開く>
🔗 <https://www.notion.so/{db_id.replace('-', '')}|Notionページを開く>
"""

try:
    slack.chat_postMessage(channel=channel, text=message)
    print("✅ Slack通知成功")
except SlackApiError as e:
    print("❌ Slack通知エラー:", e.response["error"])