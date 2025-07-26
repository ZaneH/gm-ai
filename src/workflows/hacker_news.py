import asyncio
import aiohttp
from typing import List, Dict, Any

async def fetch_hacker_news_top_stories(limit: int = 60) -> List[Dict[str, Any]]:
    """
    Fetch top stories from Hacker News.
    Gets first 2 pages worth of stories (30 per page typically).
    """
    async with aiohttp.ClientSession() as session:
        # Get list of top story IDs
        top_stories_url = "https://hacker-news.firebaseio.com/v0/topstories.json"
        async with session.get(top_stories_url) as response:
            story_ids = await response.json()

        # Limit to first 60 stories (approximately 2 pages)
        story_ids = story_ids[:limit]
        
        # Fetch details for each story
        stories = []
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
                    stories.append(story)

        return stories

async def get_hacker_news_summary(logger, limit: int = 20) -> str:
    """
    Get top Hacker News stories formatted for daily brief.
    Returns a formatted string with the most interesting stories.
    """
    logger.info(f"Fetching top {limit} Hacker News stories")
    
    try:
        stories = await fetch_hacker_news_top_stories(limit)
        
        if not stories:
            return "No Hacker News stories available."
        
        # Filter out stories with very low scores (likely not interesting)
        interesting_stories = [s for s in stories if s['score'] >= 50]
        
        # Take top stories by score, limit to reasonable number for brief
        top_stories = sorted(interesting_stories, key=lambda x: x['score'], reverse=True)[:15]
        
        # Format stories for the brief
        formatted_stories = []
        for i, story in enumerate(top_stories, 1):
            title = story['title']
            score = story['score']
            hn_url = story['hn_url']
            external_url = story.get('url', '')
            
            # Format the story entry
            story_text = f"{i}. **{title}** ({score} points)"
            if external_url:
                story_text += f"\n   Link: {external_url}"
            story_text += f"\n   Discussion: {hn_url}\n"
            
            formatted_stories.append(story_text)
        
        # Create summary
        total_score = sum(s['score'] for s in top_stories)
        avg_score = total_score / len(top_stories) if top_stories else 0
        
        summary = f"""TOP HACKER NEWS STORIES ({len(top_stories)} stories, avg score: {avg_score:.0f}):

{chr(10).join(formatted_stories)}"""
        
        logger.info(f"Successfully formatted {len(top_stories)} interesting stories")
        return summary
        
    except Exception as e:
        logger.error(f"Error fetching Hacker News stories: {e}")
        return f"Error fetching Hacker News stories: {e}"
