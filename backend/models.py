from sqlalchemy import String, Boolean, TEXT, Column, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime

class Base(DeclarativeBase):
    pass

class SubredditToScan(Base):
    __tablename__ = "subreddits_to_scan"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True,
        doc="Name of the subreddit, e.g., 'forhire'",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        doc="Set to False to temporarily stop scanning this subreddit",
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Subreddit name='{self.name}' active={self.is_active}>"

class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[int] = mapped_column(primary_key=True)
    post_id: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(500))
    post_text: Mapped[str | None] = mapped_column(TEXT)
    url: Mapped[str] = mapped_column(String(500))
    subreddit_name: Mapped[str] = mapped_column(String(100), index=True)
    category: Mapped[str] = mapped_column(String(20), default="neutral", index=True)  # hot, cold, neutral
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Lead post_id='{self.post_id}' title='{self.title[:30]}...'>"

class Comment(Base):  # New model for comments as leads
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True)
    comment_id: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    text: Mapped[str] = mapped_column(TEXT)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Comment comment_id='{self.comment_id}' text='{self.text[:30]}...'>"
