from sqlalchemy import create_engine, text
engine = create_engine("postgresql://neondb_owner:npg_omMf6bdDV7sY@ep-flat-lab-b17zvgp3-pooler.c-5.eu-central-1.aws.neon.tech/neondb?sslmode=require")
with engine.connect() as conn:
    res = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='file_uploads';"))
    print("FileUploads:", [r[0] for r in res.fetchall()])
