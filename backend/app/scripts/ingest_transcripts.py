"""
One-time ingestion script: chunk all transcript markdown files, embed them,
and store in Supabase pgvector table `transcript_chunks`.

Usage:
    cd backend && python -m app.scripts.ingest_transcripts
"""
import os, sys, glob, time, logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
logger = logging.getLogger(__name__)

# Ensure the backend package is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")

import openai
from supabase import create_client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_SERVICE_KEY = os.environ["SUPABASE_SERVICE_KEY"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

TRANSCRIPTS_DIR = Path(__file__).resolve().parent.parent.parent.parent / "openai_transcripts_markdown"
CHUNK_SIZE = 500      # target tokens per chunk (approx 4 chars/token)
CHUNK_OVERLAP = 50    # overlap tokens between chunks
EMBED_MODEL = "text-embedding-3-small"
EMBED_BATCH_SIZE = 100


def estimate_tokens(text: str) -> int:
    return len(text) // 4


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Split text into overlapping chunks by approximate token count."""
    char_chunk = chunk_size * 4
    char_overlap = overlap * 4
    chunks = []
    start = 0
    while start < len(text):
        end = start + char_chunk
        chunk = text[start:end]
        if chunk.strip():
            chunks.append(chunk.strip())
        start += char_chunk - char_overlap
    return chunks


def embed_batch(client: openai.OpenAI, texts: list[str]) -> list[list[float]]:
    resp = client.embeddings.create(model=EMBED_MODEL, input=texts)
    return [d.embedding for d in resp.data]


def main():
    oai = openai.OpenAI(api_key=OPENAI_API_KEY)
    sb = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

    # Clear existing data
    logger.info("Clearing existing transcript_chunks...")
    sb.table("transcript_chunks").delete().neq("id", 0).execute()

    md_files = sorted(glob.glob(str(TRANSCRIPTS_DIR / "*_en.md")))
    logger.info(f"Found {len(md_files)} transcript files")

    all_rows: list[dict] = []
    for fpath in md_files:
        fname = os.path.basename(fpath)
        text = Path(fpath).read_text(encoding="utf-8")
        if not text.strip():
            continue
        chunks = chunk_text(text)
        for i, chunk in enumerate(chunks):
            all_rows.append({
                "content": chunk,
                "source_file": fname,
                "chunk_index": i,
                "token_count": estimate_tokens(chunk),
            })

    logger.info(f"Total chunks to embed: {len(all_rows)}")

    # Embed in batches
    total_embedded = 0
    for batch_start in range(0, len(all_rows), EMBED_BATCH_SIZE):
        batch = all_rows[batch_start:batch_start + EMBED_BATCH_SIZE]
        texts = [r["content"] for r in batch]

        embeddings = embed_batch(oai, texts)
        for row, emb in zip(batch, embeddings):
            row["embedding"] = emb

        total_embedded += len(batch)
        logger.info(f"Embedded {total_embedded}/{len(all_rows)} chunks")
        time.sleep(0.2)  # rate-limit courtesy

    # Insert into Supabase in batches of 50
    logger.info("Inserting into Supabase...")
    insert_batch = 50
    for i in range(0, len(all_rows), insert_batch):
        batch = all_rows[i:i + insert_batch]
        sb.table("transcript_chunks").insert(batch).execute()
        logger.info(f"Inserted {min(i + insert_batch, len(all_rows))}/{len(all_rows)}")

    logger.info("Ingestion complete!")


if __name__ == "__main__":
    main()
