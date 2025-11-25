provider "aws" {
  region = "us-east-1"  
}

module "bedrock_kb" {
  source = "../modules/bedrock_kb"

  knowledge_base_name        = "my-bedrock-kb"
  knowledge_base_description = "Knowledge base connected to Aurora Serverless database"

  aurora_arn        = "arn:aws:rds:us-east-1:769078151975:cluster:udacity-aurora-serverless"
  aurora_db_name    = "udacity_app"  # this is the database name you used in Stack 1
  aurora_endpoint   = "udacity-aurora-serverless.cluster-cfurf9jqrkxr.us-east-1.rds.amazonaws.com"
  aurora_table_name = "bedrock_integration.bedrock_kb"
  aurora_primary_key_field = "id"
  aurora_metadata_field = "metadata"
  aurora_text_field = "chunks"
  aurora_verctor_field = "embedding"
  aurora_username   = "adminuser"  # master username you used in Stack 1
  aurora_secret_arn = "arn:aws:secretsmanager:us-east-1:769078151975:secret:udacity-aurora-serverless-Gi6ajB"
  s3_bucket_arn    = "arn:aws:s3:::udacity-bedrock-kb-769078151975"
}
