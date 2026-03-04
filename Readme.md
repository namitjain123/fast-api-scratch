To setup env
python -m venv venv
venv\Scripts\activate

 uvicorn Todoapp.main:app --reload (from the outer todoapp)

 $env:DATABASE_URL="postgresql://postgres.rxtoncpzfzgigzbfbgod:ninjhahattori@aws-1-ap-southeast-2.pooler.supabase.com:5432/postgres"