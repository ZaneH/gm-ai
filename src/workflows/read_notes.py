import gnupg
import os
import glob
from pathlib import Path
from mcp_agent.app import MCPApp
from mcp_agent.agents.agent import Agent
from mcp_agent.workflows.llm.augmented_llm_openai import OpenAIAugmentedLLM
from mcp_agent.workflows.router.router_llm_openai import OpenAILLMRouter
from src.config import config

def get_most_recent_journal_entry():
    """Find the most recent journal entry in the configured journal path."""
    journal_path = config['journal']['path']

    # Look for .org.gpg files (or .org files)
    pattern = os.path.join(journal_path, "*.org.gpg")
    files = glob.glob(pattern)

    if not files:
        # Fallback to .org files if no .gpg files found
        pattern = os.path.join(journal_path, "*.org")
        files = glob.glob(pattern)

    if not files:
        raise FileNotFoundError(f"No journal entries found in {journal_path}")

    # Sort by modification time, most recent first
    files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    most_recent = files[0]

    print(f"Found most recent journal entry: {most_recent}")
    return most_recent

def read_and_decrypt_journal_entry(file_path: str):
    """Read and decrypt a journal entry file."""
    try:
        with open(file_path, 'rb') as f:
            contents = f.read()

        # Check if we need to decrypt
        if file_path.endswith('.gpg') and config.get("journal", {}).get("gpg_password"):
            print("Decrypting journal entry...")
            password = config['journal']['gpg_password']
            gpg = gnupg.GPG()
            decrypted = gpg.decrypt(contents, passphrase=password)

            if decrypted.ok:
                contents = str(decrypted)
                print("Successfully decrypted journal entry")
                print(decrypted)
            else:
                raise Exception(f"Failed to decrypt: {decrypted.status}")

        return contents

    except Exception as e:
        print(f"Error reading journal entry: {e}")
        raise

async def read_notes(app: MCPApp):
    logger = app.logger

    logger.info("Reading journal notes")

    try:
        # Just call our functions directly since they handle everything
        recent_file = get_most_recent_journal_entry()
        contents = read_and_decrypt_journal_entry(recent_file)

        logger.info(f"Successfully read journal entry: {recent_file}")
        logger.info(f"Content length: {len(contents)} characters")

        return contents

    except Exception as e:
        logger.error(f"Error reading journal notes: {e}")
        raise
