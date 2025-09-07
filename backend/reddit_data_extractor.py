import asyncpraw
import textwrap
import os
from dotenv import load_dotenv

load_dotenv()


async def get_reddit_data(subreddits=None):
    reddit_read_only = asyncpraw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        user_agent=os.getenv("REDDIT_USER_AGENT"),
    )

    if subreddits is None:
        subreddits = ["saas"]

    posts_dict = []
    posts_comments = []

    for i, subreddit_name in enumerate(subreddits):
        print(f"Processing subreddit {i + 1}/{len(subreddits)}: {subreddit_name}")

        try:
            subreddit = await reddit_read_only.subreddit(subreddit_name)
            posts_list = []
            async for post in subreddit.new(limit=20):
                posts_list.append(post)

            for post in posts_list:
                posts_dict.append(
                    {
                        "post_id": post.id,
                        "data": {
                            "title": post.title,
                            "post_text": textwrap.shorten(
                                post.selftext, width=100, placeholder="..."
                            ),
                            "url": post.url,
                        },
                        "subreddit": subreddit_name,
                    }
                )

            for post in posts_list:
                try:
                    submission = await reddit_read_only.submission(id=post.id)
                    await submission.comments.replace_more(limit=0)
                    for comment in submission.comments:
                        posts_comments.append(
                            {
                                "comment_id": comment.id,
                                "data": {
                                    "comment_text": textwrap.shorten(
                                        comment.body, width=200, placeholder="..."
                                    ),
                                },
                                "subreddit": subreddit_name,
                            }
                        )
                except Exception as e:
                    print(f"Error processing comments for post {post.id}: {e}")
                    continue

        except Exception as e:
            print(f"Error processing subreddit {subreddit_name}: {e}")
            continue

    await reddit_read_only.close()

    print(f"Extracted {len(posts_dict)} posts and {len(posts_comments)} comments")
    return posts_dict, posts_comments
