# EduReach PDF Notes Changes

Implemented only the PDF Notes flow requested:

- Added `pdf_url` to the StudyNote backend model and response.
- Added a safe SQLite migration for existing `study_notes` tables.
- Added FastAPI PDF upload using multipart/form-data.
- PDFs are stored in `backend/uploads/` and served at `/uploads/<file>`.
- Added PDF selection to the teacher upload dialogs.
- Added `StudyNote.pdfUrl` and API response parsing in Flutter.
- Added API fetch/upload calls for notes.
- Existing standard filtering and LearnPage structure are preserved.
- Note cards now use a PDF icon and open the returned PDF URL.
- Added `http`, `file_picker`, and `url_launcher` dependencies.

Run backend from the `backend` folder:

`python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`

Then in the Flutter project:

`flutter pub get`

For Flutter Web on the same computer, the API uses `http://localhost:8000/api/v1`.
For an Android emulator, it uses `http://10.0.2.2:8000/api/v1`.
For a physical phone, change the host in `ApiService.baseUrl` to the computer's LAN IP, for example `http://192.168.x.x:8000/api/v1`.
