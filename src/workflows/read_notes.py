import gnupg
import os
import glob
from typing import List, Dict, Any
from mcp_agent.app import MCPApp
from src.config import config

def get_journal_file_paths(limit: int = 5) -> List[str]:
    """Get paths to recent journal entries, most recent first."""
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
    
    return files[:limit]

def read_and_decrypt_journal_entry(file_path: str) -> str:
    """Read and decrypt a journal entry file."""
    try:
        with open(file_path, 'rb') as f:
            contents = f.read()

        # Check if we need to decrypt
        if file_path.endswith('.gpg') and config.get("journal", {}).get("gpg_password"):
            password = config['journal']['gpg_password']
            gpg = gnupg.GPG()
            decrypted = gpg.decrypt(contents, passphrase=password)

            if decrypted.ok:
                contents = str(decrypted)
            else:
                raise Exception(f"Failed to decrypt: {decrypted.status}")
        else:
            # For non-encrypted files, decode bytes to string
            contents = contents.decode('utf-8')

        return contents
    except Exception as e:
        raise Exception(f"Failed to read {file_path}: {e}")

def read_note_contents(file_paths: List[str]) -> Dict[str, str]:
    """Read and decrypt multiple journal entries, returning a dict of path -> content."""
    results = {}
    
    for file_path in file_paths:
        try:
            content = read_and_decrypt_journal_entry(file_path)
            # Use just the filename as the key for cleaner output
            filename = os.path.basename(file_path)
            results[filename] = content
        except Exception as e:
            # Log error but continue with other files
            results[os.path.basename(file_path)] = f"Error reading file: {e}"
    
    return results

async def read_notes(app: MCPApp):
    """Legacy function - reads most recent note only."""
    logger = app.logger
    logger.info("Reading journal notes")

    try:
        file_paths = get_journal_file_paths(limit=1)
        if not file_paths:
            raise FileNotFoundError("No journal entries found")
        
        content = read_and_decrypt_journal_entry(file_paths[0])
        return content
    except Exception as e:
        logger.error(f"Error reading journal notes: {e}")
        raise
