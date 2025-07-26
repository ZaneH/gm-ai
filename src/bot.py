from mcp_agent.app import MCPApp
from mcp_agent.agents.agent import Agent
from mcp_agent.workflows.llm.augmented_llm import RequestParams
from mcp_agent.workflows.llm.augmented_llm_openai import OpenAIAugmentedLLM
from src.workflows.read_notes import get_journal_file_paths, read_note_contents
from src.workflows.hacker_news import get_hacker_news_summary
from src.config import config

app = MCPApp(name="gm_ai_app")

class Bot:
    def __init__(self):
        self.personality = ""
        self.memory = {}
        self.recent_notes = []
        self.goals = config["goals"]
        self.logger = app.logger
    
    async def generate_daily_brief(self) -> str:
        """Generate a personalized daily brief using direct agent execution."""
        try:
            self.logger.info("Gathering data for daily brief...")
            
            # Get journal entries (full content)
            journal_paths = get_journal_file_paths(limit=2)
            notes_content = read_note_contents(journal_paths)
            
            # Get Hacker News stories
            hn_summary = await get_hacker_news_summary(self.logger)
            
            # Create the briefing agent
            briefing_agent = Agent(
                name="daily_briefer",
                instruction="""You are a supportive friend who gives personalized daily briefings. You read through someone's recent journal entries, 
                check out relevant tech/startup news, and help them focus on what matters based on their goals.

                Your tone should be:
                - Warm and encouraging (like texting a good friend)
                - Substantive but focused
                - Practical and actionable
                - Honest but motivating
                - Skip generic advice - everything should be based on their actual content
                - Skip meta wording (e.g. Based on your journal entries I notice...)

                Structure your brief like this. <example> tags contain an example of the formatting you should use:

                🌅 **Good morning!** 
                [Personal greeting that reflects their recent journaling themes, mood, or concerns]

                📖 **What I noticed from your recent thoughts:**
                [Specific insights from their journal entries - patterns, concerns, wins, progress, decisions they're wrestling with]

                🎯 **Today's focus areas aligned with your goals:**
                [Based on their goals AND recent journal entries, suggest specific, actionable things to work on today. Connect these explicitly to their stated goals.]

                🔥 **Tech/startup news that caught my eye for you:**
                [Pick HN stories (provided in the HACKER NEWS SUMMARY section) that would genuinely interest them based on their goals, recent thoughts, or technical interests. Format like this example:]
                <example>
                1. Example title here (420 points)
                   - Link: https://example.com/
                   - Discussion: https://news.ycombinator.com/item?id=123
                2. Example title 2 here (69 points)
                   - Link: https://example2.com/
                   - Discussion: https://news.ycombinator.com/item?id=456
                </example>

                💪 **Daily motivation:**
                [Encouraging message that ties together their goals, recent journal insights, and today's opportunities. Make this personal and specific - not generic motivation.]

                CRITICAL:
                - Base everything on their actual journal content and goals. If their journal entries mention specific projects, concerns, wins, or decisions, reference those specifically. Don't make up generic advice.
                - Do not include URLs unless they've been referenced in the context. Don't just make up URLs.
                - Never advertise to me, I don't need booking sites, or any other random URLs like that in my briefs.
                """,
            )

            # Prepare the message with full journal content (no truncation)
            journal_content = "\n".join(f"=== {filename} ===\n{content}" for filename, content in notes_content.items())
            
            goals_text = "\n".join(f"- {goal}" for goal in self.goals)
            
            message = f"""Here's the data for today's brief:

RECENT JOURNAL ENTRIES:
{journal_content}

PERSONAL GOALS:
{goals_text}

HACKER NEWS SUMMARY:
{hn_summary}

Please generate a personalized daily brief based on this information."""

            async with briefing_agent:
                llm = await briefing_agent.attach_llm(OpenAIAugmentedLLM)
                result = await llm.generate_str(message, request_params=RequestParams(maxTokens=32_000))
            
            self.logger.info("Daily brief generated successfully")
            return result
            
        except Exception as e:
            self.logger.error(f"Error generating daily brief: {str(e)}")
            return f"Sorry, I couldn't generate your daily brief today. Error: {str(e)}"

async def start_bot(bot):
    async with app.run() as gmai_app:
        logger = gmai_app.logger
        bot.logger = logger
        
        try:
            brief = await bot.generate_daily_brief()
            
            logger.info("Daily brief generated successfully")
            print("\n" + "="*24)
            print("📱 YOUR DAILY BRIEF")
            print("="*24)
            print(brief)
            print("="*24 + "\n")
            
        except Exception as e:
            logger.error(f"Error generating daily brief: {e}")
            raise
