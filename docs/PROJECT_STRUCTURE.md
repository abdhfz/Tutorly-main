# Project Structure and Architecture

This project is currently a compact full-stack prototype. It works as a single repository with a Flask backend and a Vite + React frontend.

## Current Layout

```text
app.py
run_server.py
requirements.txt
package.json
index.html
src/
  App.jsx
  main.jsx
  styles.css
static/
  index.html
  favicon.ico
  logo.png
  assets/
uploads/
```

## Runtime Folders

- `.venv/` contains the local Python virtual environment.
- `node_modules/` contains Node dependencies.
- `tutorly.db` is the local SQLite database.
- `server.out.log` and `server.err.log` are local server logs.
- `uploads/` is reserved for runtime uploads and should not contain tracked user files.

These are intentionally excluded from source control.

## Backend Architecture

`app.py` currently contains:

- Flask app creation and configuration
- SQLite table setup
- Gemini API service logic
- image processing
- auth routes
- assignment routes
- chat routes
- progress routes
- teacher routes
- static frontend serving

This is acceptable for a prototype, but it should be split before the app grows much more.

Recommended future backend split:

```text
backend/
  __init__.py
  app.py
  config.py
  db.py
  routes/
    auth.py
    assignments.py
    chat.py
    progress.py
    teachers.py
  services/
    gemini.py
    images.py
```

## Frontend Architecture

`src/App.jsx` currently contains most of the React app:

- API client
- auth screen
- shell/navigation
- dashboard
- chat page
- tasks page
- assignments page
- shared helpers

Recommended future frontend split:

```text
src/
  App.jsx
  main.jsx
  services/
    api.js
  components/
    AppShell.jsx
    Icon.jsx
    MessageContent.jsx
    StatCard.jsx
  pages/
    Auth.jsx
    Dashboard.jsx
    ChatbotPage.jsx
    TasksPage.jsx
    AssignmentsPage.jsx
  utils/
    formatting.js
  styles/
    index.css
```

## Static Assets

Vite currently builds production files directly into `static/` so Flask can serve them. This works, but over time hashed files in `static/assets/` can accumulate.

A cleaner future option is:

```text
static/
  favicon.ico
  logo.png
  dist/
```

Then configure Vite to build into `static/dist/` and update Flask to serve the app from that folder.

## Next Refactor Order

1. Extract the frontend API client from `src/App.jsx` into `src/services/api.js`.
2. Split React pages into `src/pages/`.
3. Split reusable UI pieces into `src/components/`.
4. Move backend database helpers into `backend/db.py`.
5. Move Gemini and image processing into `backend/services/`.
6. Move Flask routes into route modules or blueprints.
