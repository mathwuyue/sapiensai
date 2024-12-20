# Environment
Modify env.local, and rename it as .env. You should keep STORAGE_PATH and BLOOM_KEY same as ...

# Installation
Create a Python virtual environment and install requirement.txt
```
python -m venv emmabloom
source emmabloom/bin/activate  # On Linux/Mac
venv\Scripts\activate     # On Windows
pip install -r requirements.txt
```

# Database
You may need to setup PostgreSQL 16 for proper user, database and privilege. Also, vector plugin is necessary. Check related documentation for setup PGVector or pgvecto.rs
> When using pgvecto.rs, needs to grant privilege to <user> for accessing vector schema in the database.

Move db_migrate.py in infra/ directory to emma/ directory and run `python db_migrate.py` to setup tables in database

# Running
In emma/ directory
```
uvicorn server:app --host 0.0.0.0 --port <port>
```