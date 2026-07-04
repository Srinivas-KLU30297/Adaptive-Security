# Workspace Instructions: Running and Configuring CyberShield AI Platform

This workspace contains a Python (FastAPI) backend and a React (Vite + TypeScript) frontend. 

When a user asks you to "run the project", "set up the workspace", "start the frontend and backend", or any similar command, you MUST automatically perform the following setup, installation, migration, and run operations without requiring manual execution by the user:

---

## 1. Database Setup Check & Update
Before running the backend, check and configure the MySQL database connection:
1. Verify if the `backend/.env` file exists. If it does not, copy `backend/.env.example` to `backend/.env`.
2. The default configuration uses:
   `DATABASE_URL=mysql+aiomysql://root:%40Sinu8541@localhost:3306/cybershield_db`
   *Note: `%40` is the URL-encoded `@` character.*
3. Ask the user if they have MySQL running on `localhost:3306` with the username `root` and password `@Sinu8541`. If they have a different password/username, edit `backend/.env` to reflect their credentials.
4. Execute/propose a terminal command to ensure the MySQL database exists:
   ```sql
   CREATE DATABASE IF NOT EXISTS cybershield_db;
   ```
   *(You can run this via MySQL command line if MySQL is in the PATH, or instruct the user to run it, or connect using a temporary script).*

---

## 2. Backend Setup & Run
Run the backend server using the following sequence:
1. Check if the `.venv` directory exists in the workspace root or `backend/venv`.
2. Activate the virtual environment:
   * **Windows Powershell**: `.venv\Scripts\activate` or `backend\venv\Scripts\activate`
   * **Windows CMD**: `.venv\Scripts\activate.bat` or `backend\venv\Scripts\activate.bat`
   * **Linux/macOS**: `source .venv/bin/activate` or `source backend/venv/bin/activate`
3. If no virtual environment exists, create one:
   ```bash
   python -m venv .venv
   ```
4. Install/update python dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```
5. Apply database migrations using Alembic:
   Ensure you are in the `backend` directory (by setting Cwd to `backend`) and run:
   ```bash
   alembic upgrade head
   ```
6. Start the backend server as a background task. Set the Cwd to `backend` and run:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
   *Note: Allow up to 10 seconds synchronous wait before going async to let the AI weights load.*

---

## 3. Frontend Setup & Run
Run the React frontend using the following sequence:
1. Navigate to the `frontend` directory (set Cwd to `frontend`).
2. Run `npm install` to ensure all packages are installed.
3. Start the Vite development server as a background task:
   ```bash
   npm run dev
   ```

---

## 4. Default Verification & Status
After starting the servers, check the status:
1. Ping `http://localhost:8000/api/v1/health` to confirm the backend is up.
2. Confirm the frontend server port (usually `http://localhost:3000` or `http://localhost:5173`).
3. Inform the user that the project is running and they can log in with:
   * **Email:** `admin@cybershield.ai`
   * **Password:** `Admin@123`
