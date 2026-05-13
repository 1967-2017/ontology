Set-Location "E:\AAA\Project\Ontology\backend"
& "D:\AAA\miniconda3\envs\ontology-dev\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
