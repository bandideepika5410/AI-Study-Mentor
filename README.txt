STUDYMENTOR - HACKATHON UPGRADED VERSION
========================================

TRACK
VibeX Codes Track 4: Smart AI Helpers for Coding, Work & Student Learning.

WHAT IS INCLUDED
- Responsive student learning dashboard
- Five-topic skill confidence assessment
- Adaptive study plan generated from low-confidence topics
- Add tasks and mark them complete
- Career path selection
- Assessment history, average score and task progress
- Python local server and SQLite database (persistent storage)

HOW TO RUN ON WINDOWS
1. Extract this ZIP file.
2. Make sure Python 3 is installed.
   - Open Command Prompt and type: py --version
   - If not found, install Python 3 from python.org and tick "Add Python to PATH".
3. Open the extracted folder.
4. Double-click START_APP.bat.
5. A black command window opens and the app opens in your browser at:
   http://127.0.0.1:8000
6. Keep the black command window open while using the website.
7. To stop the app, click the black window and press Ctrl+C.

NO THIRD-PARTY PYTHON PACKAGES REQUIRED
The backend uses Python standard library only. SQLite is included with Python.

DATABASE
A file named studymentor.db is created automatically in this folder.
It stores the student profile, assessment attempts, career choice and study tasks.
Keep this file with the project if you want to retain saved progress.

IMPORTANT HONEST DESCRIPTION
This version includes an adaptive, rule-based recommendation engine. It evaluates assessment scores by topic and creates study tasks for low-confidence topics. It is NOT a trained machine-learning model or a connected generative-AI service. Describe it accurately in your PPT/demo. You can add a real AI API integration as a future enhancement.

DEMO FLOW
1. Start with START_APP.bat.
2. Complete the five-question skill assessment.
3. Show score and weak topics.
4. Open Study Planner; tick a task and add a custom task.
5. Return to Dashboard to show updated progress and assessment history.
6. Open Career Guidance and choose a path.
7. Close browser, reopen the URL while server is running; saved information remains in SQLite.

SUBMISSION CHECKLIST FROM THE PROVIDED VIBEX CODES GUIDE
- 8-10 slide PPT/PDF is mandatory.
- Working code link (GitHub/GitLab) is mandatory.
- 2-3 minute live demo video is optional and offers up to 15 bonus points.
