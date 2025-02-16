from dataclasses import dataclass

@dataclass
class NewsArticle:
    title: str
    body: str
    url: str
    published: str
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, NewsArticle):
            return False
        return (self.url == other.url and 
            self.title == other.title and 
            self.body == other.body)
