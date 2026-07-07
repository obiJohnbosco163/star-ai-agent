# S.T.A.R. Frontend

A React + TypeScript single-page app for the S.T.A.R. research copilot.

## Setup

1. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```
2. Create a local environment file from the example:
   ```bash
   cp .env.example .env
   ```
3. Run the app:
   ```bash
   npm run dev
   ```

## Notes

- The frontend calls the backend proxy at `VITE_API_BASE_URL`.
- Do not add any API keys or secrets to this repo.
