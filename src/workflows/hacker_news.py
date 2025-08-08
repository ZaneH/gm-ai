import aiohttp
from typing import List, Dict, Any

async def fetch_hacker_news_top_posts(limit: int = 60) -> List[Dict[str, Any]]:
    """
    Fetch top posts from Hacker News.
    """
    async with aiohttp.ClientSession() as session:
        # Get list of top story IDs
        top_stories_url = "https://hacker-news.firebaseio.com/v0/topstories.json"
        async with session.get(top_stories_url) as response:
            story_ids = await response.json()

        # Limit to first 60 posts (approximately 2 pages)
        story_ids = story_ids[:limit]
        
        # Fetch details for each story
        posts = []
        for story_id in story_ids:
            story_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
            async with session.get(story_url) as response:
                story_data = await response.json()
                
                if story_data and story_data.get('type') == 'story':
                    # Clean up and structure the story data
                    story = {
                        'id': story_data.get('id'),
                        'title': story_data.get('title'),
                        'url': story_data.get('url'),
                        'score': story_data.get('score', 0),
                        'by': story_data.get('by'),
                        'time': story_data.get('time'),
                        'descendants': story_data.get('descendants', 0),  # comment count
                        'text': story_data.get('text', ''),
                        'hn_url': f"https://news.ycombinator.com/item?id={story_id}"
                    }
                    posts.append(story)

        return posts

async def get_hacker_news_summary(logger, limit: int = 20) -> str:
    """
    Get top Hacker News posts formatted for daily brief.
    Returns a formatted string with the most interesting posts.
    """
    logger.info(f"Fetching top {limit} Hacker News posts")
    
    try:
        posts = await fetch_hacker_news_top_posts(limit)
        
        if not posts:
            return "No Hacker News posts available."

        # Sort by score
        top_stories = sorted(posts, key=lambda x: x['score'], reverse=True)
        
        # Format posts for the brief
        formatted_stories = []
        for i, story in enumerate(top_stories, 1):
            title = story['title']
            score = story['score']
            hn_url = story['hn_url']
            external_url = story.get('url', '')
            
            # Format the story entry
            story_text = f"{i}. [{title}]({external_url}) ({score} points)"
            if external_url:
                story_text += f"\n- Link: {external_url}"
            story_text += f"\n- Discussion: {hn_url}"

            formatted_stories.append(story_text)
        
        # Create output string
        total_score = sum(s['score'] for s in top_stories)
        avg_score = total_score / len(top_stories) if top_stories else 0
        
        summary = f"""({len(top_stories)} posts, avg score: {avg_score:.0f}):

{chr(10).join(formatted_stories)}"""
        
        logger.info(f"Successfully formatted {len(top_stories)} interesting posts")
        return summary
        
    except Exception as e:
        logger.error(f"Error fetching Hacker News posts: {e}")
        return f"Error fetching Hacker News posts: {e}"
