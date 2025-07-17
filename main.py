import asyncio
import time
from src.bot import Bot, start_bot

def main():
    start = time.time()
    bot = Bot()
    asyncio.run(start_bot(bot))
    end = time.time()
    print(f"Total run time: {end - start:.2f}s")

if __name__ == "__main__":
    main()
