class Task:
    def __init__(self, notion_data: dict):
        props = notion_data["properties"]
        self.chapter = self._get_text(props.get("title", {}), key="title")
        self.task = self._get_text(props.get("task", {}), key="rich_text")
        self.memo = self._get_text(props.get("memo", {}), key="rich_text")

    def _get_text(self, field: dict, key: str) -> str:
        try:
            return field.get(key, [{}])[0].get("plain_text", "")
        except (IndexError, AttributeError):
            return ""

    def __repr__(self):
        return f"Task(chapter={self.chapter}, work={self.work}, memo={self.memo})"
