import boto3
import os

client = boto3.client("rds-data", region_name="us-east-1")

script_dir = os.path.dirname(os.path.abspath(__file__))
sql_file_path = os.path.join(script_dir, "aurora_sql.sql")

# Read SQL file (optional — not used directly)
with open(sql_file_path) as f:
    sql_commands = f.read()

statements = [
    # 1. Vector extension
    "CREATE EXTENSION IF NOT EXISTS vector;",

    # 2. Schema for Bedrock KB
    "CREATE SCHEMA IF NOT EXISTS bedrock_integration;",

    # 3. Create bedrock_user if missing
    """
    DO $$ 
    BEGIN 
        CREATE ROLE bedrock_user LOGIN; 
    EXCEPTION 
        WHEN duplicate_object THEN 
            RAISE NOTICE 'Role already exists'; 
    END 
    $$;
    """,

    # 4. Grant schema permissions
    "GRANT ALL ON SCHEMA bedrock_integration TO bedrock_user;",

    # ⚠️ Removed: SET SESSION AUTHORIZATION bedrock_user;
    # (RDS Data API cannot switch roles inside execution)

    # 5. Create table
    """
    CREATE TABLE IF NOT EXISTS bedrock_integration.bedrock_kb (
        id uuid PRIMARY KEY,
        embedding vector(1536),
        chunks text,
        metadata json
    );
    """,

    # 6. Vector index (HNSW)
    """
    CREATE INDEX IF NOT EXISTS bedrock_kb_embedding_idx 
    ON bedrock_integration.bedrock_kb 
    USING hnsw (embedding vector_cosine_ops);
    """,

    # 7. REQUIRED — Full-text GIN index for Bedrock
    """
    CREATE INDEX IF NOT EXISTS bedrock_kb_chunks_fts_idx
    ON bedrock_integration.bedrock_kb
    USING gin (to_tsvector('english', chunks));
    """
]

for stmt in statements:
    stmt = stmt.strip()
    if not stmt:
        continue

    response = client.execute_statement(
        resourceArn="arn:aws:rds:us-east-1:769078151975:cluster:udacity-aurora-serverless",
        secretArn="arn:aws:secretsmanager:us-east-1:769078151975:secret:udacity-aurora-serverless-chSsqp",
        database="udacity_app",
        sql=stmt
    )

    print(f"Executed: {stmt.splitlines()[0]}...")
