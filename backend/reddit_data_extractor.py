import asyncpraw
import textwrap
import os
from dotenv import load_dotenv
from job_tracker import SearchJob

load_dotenv()


async def get_reddit_data(subreddits=None, job: SearchJob = None):
    reddit_read_only = asyncpraw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        user_agent=os.getenv("REDDIT_USER_AGENT"),
    )

    if subreddits is None:
        subreddits = ["saas"]

    posts_dict = []
    posts_comments = []

    total_subreddits = len(subreddits)
    for i, subreddit_name in enumerate(subreddits):
        print(f"Processing subreddit {i + 1}/{total_subreddits}: {subreddit_name}")
        
        # Update progress based on subreddit processing
        if job:
            # Progress from 10% to 40% during subreddit processing
            progress = 10 + int((i / total_subreddits) * 30)
            job.update_progress(progress)

        try:
            subreddit = await reddit_read_only.subreddit(subreddit_name)
            posts_list = []
            
            # Collect posts
            post_count = 0
            async for post in subreddit.new(limit=60):
                posts_list.append(post)
                post_count += 1
                # Update progress periodically during post collection
                if job and post_count % 10 == 0:
                    # Calculate progress: 10% base + (subreddit progress * 0.5) + (post progress * 0.5)
                    subreddit_progress = int((i / total_subreddits) * 15)
                    post_progress = int((post_count / 60) * 15)
                    progress = 10 + subreddit_progress + post_progress
                    # Ensure progress doesn't go backwards and stays within bounds
                    current_progress = job.progress
                    if progress > current_progress:
                        job.update_progress(min(progress, 25))  # Cap at 25% during post collection

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

            # Process comments
            comment_count = 0
            total_posts = len(posts_list)
            for j, post in enumerate(posts_list):
                try:
                    submission = await reddit_read_only.submission(id=post.id)
                    await submission.comments.replace_more(limit=0)
                    for comment in submission.comments:
                        posts_comments.append(
                            {
                                "comment_id": comment.id,
                                "post_id": post.id,  # Add post_id to comments
                                "data": {
                                    "comment_text": textwrap.shorten(
                                        comment.body, width=200, placeholder="..."
                                    ),
                                },
                                "subreddit": subreddit_name,
                            }
                        )
                    comment_count += 1
                    # Update progress periodically during comment processing
                    if job and comment_count % 5 == 0:
                        # Calculate progress: 25% base + comment processing progress (15% total)
                        comment_progress = int((comment_count / len(posts_list)) * 15)
                        progress = 25 + comment_progress
                        # Ensure progress doesn't go backwards and stays within bounds
                        current_progress = job.progress
                        if progress > current_progress:
                            job.update_progress(min(progress, 39))  # Cap at 39%
                except Exception as e:
                    print(f"Error processing comments for post {post.id}: {e}")
                    continue

        except Exception as e:
            print(f"Error processing subreddit {subreddit_name}: {e}")
            continue

    await reddit_read_only.close()

    print(f"Extracted {len(posts_dict)} posts and {len(posts_comments)} comments")
    return posts_dict, posts_comments
