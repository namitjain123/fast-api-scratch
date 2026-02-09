##This is the fast-api end points(CRUD) for the practise purpose 

To setup env
python -m venv venv
venv\Scripts\activate

jwt.encode(payload, SECRET_KEY, algorithm="HS256")
does three things:

Takes your payload (user_id, username, exp)

Uses SECRET_KEY + algorithm (HS256)

Creates a digital signature
The token looks like this:

header.payload.signature


The signature is generated using the secret key.
┌────────────┐
│  Frontend  │
│  (React)   │
└─────┬──────┘
      │ 1. Login (username + password)
      ▼
┌────────────┐
│  /token    │
│  FastAPI   │
└─────┬──────┘
      │ 2. authenticate_user()
      │ 3. create_access_token()
      ▼
┌────────────────────────────┐
│ JWT TOKEN                  │
│ header.payload.signature   │
└───────────┬────────────────┘
            │
            │ 4. Store token
            ▼
┌────────────────────────────┐
│ Browser / App              │
│ localStorage / cookie      │
└───────────┬────────────────┘
            │
            │ 5. API call
            │ Authorization: Bearer <token>
            ▼
┌────────────────────────────┐
│ Protected Endpoint         │
│ /todos                     │
└───────────┬────────────────┘
            │
            │ oauth2_bearer
            ▼
┌────────────────────────────┐
│ get_current_user()         │
│ - verify signature         │
│ - check exp                │
│ - fetch user               │
└───────────┬────────────────┘
            │
            ▼
┌────────────────────────────┐
│ Request allowed ✅         │
└────────────────────────────┘

db_dependency = Annotated[Session, Depends(get_db)]

“Whenever I write db: db_dependency, FastAPI should:
call get_db()
get a database Session
inject it here
and close it after the request”

user_dependency = Annotated[auth.Users, Depends(get_current_user)]

“Whenever I write user: user_dependency, FastAPI should:
extract the JWT token
verify it
find the logged-in user
inject the Users object here”


With dependencies ✅

centralized auth
centralized DB lifecycle
clean endpoints
fewer bugs

1️⃣ user.id

Comes from JWT authentication
Extracted inside get_current_user
Based on the token you issued at login
Cannot be changed by the client


###for testing 
test_todos.py
Full flow (important mental model)

Test starts

FastAPI endpoint calls Depends(get_db)

FastAPI sees an override

override_get_db() runs instead

SQLite test DB is used

Test finishes

Session closes


## login page to todo-page cookies concept
Login success
↓
Browser stores access_token cookie
↓
User clicks link / redirect
↓
Browser sends request
↓
Cookie is attached automatically
↓
Backend reads request.cookies
↓
User authenticated


Browser
 └─ Cookie (access_token)
      └─ get_token_from_request
            └─ get_current_user
                  └─ user_dependency
                        └─ user available in route