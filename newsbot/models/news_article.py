import json
from dataclasses import dataclass


@dataclass
class NewsArticle:
    title: str
    body: str
    url: str
    published: str
    category: str = "general"

    def __str__(self) -> str:
        return json.dumps(
            {
                "title": self.title,
                "body": self.body,
                "url": self.url,
                "published": self.published,
                "category": self.category,
            }
        )
