
import logging
import os
import telegram
from datetime import datetime, timedelta, timezone

# Create logger
logger = logging.getLogger("__main__.telegram_handler")

# Function to read and write checkpoint file
def checkpoint_utils(mode, data=None):
    checkpoint_file = 'checkpoint/telegram_checkpoint.txt'
    if mode == 'r':
        if os.path.exists(checkpoint_file):
            with open(checkpoint_file, 'r') as file:
                return file.read().splitlines()
        return []
    elif mode == 'w':
        with open(checkpoint_file, 'w') as file:
            file.write('\n'.join(data))
    elif mode == 'd':
        if os.path.exists(checkpoint_file):
            os.remove(checkpoint_file)

async def send_posts_to_channel(posts):
    # Start Telegram bot
    bot = telegram.Bot(os.getenv("TELEGRAM_BOT_TOKEN"))
    
    # Get sent posts and last post date to get new posts
    sent_posts = checkpoint_utils('r')
    if sent_posts:
        last_post = list(sent_posts)[-1].strip()
        last_post_date_str = last_post.split(",")[-1]
        last_post_date = datetime.fromisoformat(last_post_date_str).astimezone(timezone.utc)
    else:
        last_post_date = (datetime.utcnow() - timedelta(days=1)).astimezone(timezone.utc)
    
    logger.info("Looking for new Instagram posts")
    channel_id = os.getenv("TELEGRAM_CHANNEL_ID")
    new_posts = []
    for post in posts:
        if post.taken_at > last_post_date and f'{post.pk},{post.code},{post.taken_at}' not in sent_posts:
            if post.media_type == 1:
                logger.info("Sending new picture post to Telegram channel")
                photo = post.thumbnail_url
                caption = post.caption_text
                await bot.send_photo(chat_id=channel_id, photo=photo, caption=caption)
            if post.media_type == 2:
                logger.info("Sending new video post to Telegram channel")
                video = post.video_url
                caption = post.caption_text
                await bot.send_video(chat_id=channel_id, video=video, caption=caption)
            elif post.media_type == 8:
                logger.info("Sending new album post to Telegram channel")
                media_group = []
                caption = post.caption_text
                caption_added = False
                for p in post.resources:
                    if p.media_type == 1:
                        if not caption_added:
                            media_group.append(telegram.InputMediaPhoto(p.thumbnail_url, caption=caption))
                            caption_added = True
                        else:
                            media_group.append(telegram.InputMediaPhoto(p.thumbnail_url))
                    elif p.media_type == 2:
                        if not caption_added:
                            media_group.append(telegram.InputMediaVideo(p.video_url, caption=caption))
                            caption_added = True
                        else:
                            media_group.append(telegram.InputMediaVideo(p.video_url))
                        
                await bot.send_media_group(chat_id=channel_id, media=media_group)

            # Append new posts to sent posts list
            new_posts.append(f'{post.pk},{post.code},{post.taken_at}')

    # Sort new posts to keep them sorted in the checkpoint file
    new_posts_sorted = sorted(new_posts, key=lambda x: datetime.fromisoformat(x.split(",")[-1]))
    checkpoint_utils('w', new_posts_sorted)
    checkpoint_utils('d')