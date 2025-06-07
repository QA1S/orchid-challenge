# Orchids SWE Intern Challenge Template

This project consists of a backend built with FastAPI and a frontend built with Next.js and TypeScript.

## Backend
To run the backend:
1. Navigate to the backend folder:

```bash
cd backend
```

2. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
```

3. Install the dependencies:

```bash
pip install -r requirements.txt
playwright install
```

4. Create a `.env` file with your Anthropic API key:

```env
ANTHROPIC_API_KEY=sk-your-api-key-here
```

## 🚀 Running the Backend

To start the FastAPI server locally:

```bash
uvicorn main:app --reload
```

The server will start on: [http://localhost:8000](http://localhost:8000)


## Frontend

The frontend is built with Next.js and TypeScript.

### Installation

To install the frontend dependencies, navigate to the frontend project directory and run:

```bash
npm install
```

### Running the Frontend

To start the frontend development server, run:

```bash
npm run dev
```
