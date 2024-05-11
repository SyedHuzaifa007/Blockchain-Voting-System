import os
import pyodbc
from fastapi import FastAPI, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
import jwt
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize the FastAPI app
app = FastAPI()

# Define the allowed origins for CORS
origins = [
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connect to the SQL Server database
conn = None
cursor = None

try:
    conn = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=' + os.environ['SQL_SERVER_HOST'] + ';'
        'DATABASE=' + os.environ['SQL_SERVER_DB'] + ';'
        'UID=' + os.environ['SQL_SERVER_USER'] + ';'
        'PWD=' + os.environ['SQL_SERVER_PASSWORD'] + ';'
    )
    cursor = conn.cursor()
except pyodbc.Error as err:
    print("SQL Server connection error:", err)

# Define the authentication middleware
async def authenticate(request: Request):
    try:
        api_key = request.headers.get('authorization').replace("Bearer ", "")
        cursor.execute("SELECT * FROM voters WHERE voter_id = ?", (api_key,))
        if api_key not in [row[0] for row in cursor.fetchall()]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Forbidden"
            )
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Forbidden"
        )

# Define the POST endpoint for login
@app.get("/login")
async def login(request: Request, voter_id: str, password: str):
    await authenticate(request)
    role = await get_role(voter_id, password)

    # Assuming authentication is successful, generate a token
    token = jwt.encode({'password': password, 'voter_id': voter_id, 'role': role}, os.environ['SECRET_KEY'], algorithm='HS256')

    return {'token': token, 'role': role}

# Replace 'admin' with the actual role based on authentication
async def get_role(voter_id, password):
    try:
        cursor.execute("SELECT role FROM voters WHERE voter_id = ? AND password = ?", (voter_id, password,))
        role = cursor.fetchone()
        if role:
            return role[0]
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid voter id or password"
            )
    except pyodbc.Error as err:
        print("SQL Server query error:", err)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error"
        )
    except KeyboardInterrupt:
        # Handle keyboard interrupt gracefully
        if conn:
            conn.close()
        raise