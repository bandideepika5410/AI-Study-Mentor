#!/usr/bin/env python3
"""StudyMentor local application server. Uses only Python standard library + SQLite."""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse
import json, sqlite3, datetime, threading, webbrowser, os

ROOT = Path(__file__).resolve().parent
DB = ROOT / "studymentor.db"
LOCK = threading.Lock()
TOPICS = ["Python", "Mathematics", "SQL", "Communication", "Problem Solving"]
DEFAULT_TASKS = [
    ("Revise one topic from your weakest subject", "25 min"),
    ("Practice 3 questions related to that topic", "30 min"),
    ("Learn one new concept or skill", "20 min"),
    ("Write a short summary of what you learned", "10 min"),
]

def connect():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    with connect() as con:
        con.executescript("""
        CREATE TABLE IF NOT EXISTS profile(id INTEGER PRIMARY KEY CHECK(id=1), name TEXT NOT NULL DEFAULT 'Student', goal TEXT NOT NULL DEFAULT '', career TEXT NOT NULL DEFAULT '');
        INSERT OR IGNORE INTO profile(id) VALUES(1);
        CREATE TABLE IF NOT EXISTS assessments(id INTEGER PRIMARY KEY AUTOINCREMENT, score INTEGER NOT NULL, weak_topics TEXT NOT NULL, created_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS tasks(id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, duration TEXT NOT NULL DEFAULT 'Personal', done INTEGER NOT NULL DEFAULT 0, created_at TEXT NOT NULL);
        """)
        count = con.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
        if count == 0:
            now = datetime.datetime.now().isoformat(timespec="seconds")
            con.executemany("INSERT INTO tasks(title,duration,created_at) VALUES(?,?,?)", [(t,d,now) for t,d in DEFAULT_TASKS])

def recommendation(weak):
    if weak:
        return {"title": f"Focus on {weak[0]}", "message": f"Your assessment shows that {', '.join(weak)} may need more practice. Start with short lessons and beginner exercises."}
    return {"title":"Keep building your skills", "message":"Your answers show a good starting point. Practice consistently and try a slightly harder challenge next."}

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)
    def log_message(self, fmt, *args):
        print("[StudyMentor] " + fmt % args)
    def send_json(self, obj, status=200):
        raw = json.dumps(obj).encode()
        self.send_response(status); self.send_header("Content-Type","application/json; charset=utf-8")
        self.send_header("Content-Length",str(len(raw))); self.send_header("Cache-Control","no-store"); self.end_headers(); self.wfile.write(raw)
    def body(self):
        n=int(self.headers.get("Content-Length","0"))
        return json.loads(self.rfile.read(n) or b"{}")
    def do_GET(self):
        path=urlparse(self.path).path
        if path=="/api/dashboard":
            with connect() as con:
                p=con.execute("SELECT * FROM profile WHERE id=1").fetchone()
                attempts=[dict(r) for r in con.execute("SELECT score,created_at,weak_topics FROM assessments ORDER BY id DESC")]
                tasks=con.execute("SELECT COUNT(*) total, SUM(done) completed FROM tasks").fetchone()
                weak=[]
                if attempts:
                    weak=json.loads(attempts[0]["weak_topics"])
                total=tasks["total"] or 0; completed=tasks["completed"] or 0
                avg=round(sum(a["score"] for a in attempts)/len(attempts)) if attempts else 0
                self.send_json({"name":p["name"],"goal":p["goal"],"career":p["career"],"attempts":attempts,"average":avg,"completed_tasks":completed,"progress":round(completed/total*100) if total else 0,"recommendation":recommendation(weak) if attempts else None})
            return
        if path=="/api/tasks":
            with connect() as con:
                rows=[dict(r) for r in con.execute("SELECT * FROM tasks ORDER BY id")]
            self.send_json({"tasks":rows,"total":len(rows),"completed":sum(r["done"] for r in rows)});return
        if path.startswith("/api/"):
            self.send_json({"error":"API route not found"},404);return
        return super().do_GET()
    def do_POST(self):
        path=urlparse(self.path).path
        try: data=self.body()
        except Exception: self.send_json({"error":"Invalid JSON body"},400);return
        if path=="/api/assessment":
            name=str(data.get("name","Student")).strip()[:35] or "Student"
            answers=data.get("answers",[])
            if not isinstance(answers,list) or len(answers)!=5 or any(a not in (1,2,3) for a in answers):
                self.send_json({"error":"Please answer all five questions."},400);return
            score=round(sum(answers)/(5*3)*100)
            weak=[TOPICS[i] for i,a in enumerate(answers) if a==1]
            now=datetime.datetime.now().isoformat(timespec="seconds")
            with connect() as con:
                con.execute("UPDATE profile SET name=?,goal=? WHERE id=1",(name,str(data.get("goal",""))[:100]))
                con.execute("INSERT INTO assessments(score,weak_topics,created_at) VALUES(?,?,?)",(score,json.dumps(weak),now))
                # Create a fresh adaptive plan from the lowest-confidence topics.
                con.execute("DELETE FROM tasks")
                focus=weak[0] if weak else "your selected subject"
                tasks=[
                    (f"Revise {focus} fundamentals using notes or a short lesson","25 min"),
                    (f"Solve 3 beginner practice questions in {focus}","30 min"),
                    (f"Learn one new concept for: {name}'s goal","20 min"),
                    ("Explain today's learning in your own words","10 min")]
                con.executemany("INSERT INTO tasks(title,duration,created_at) VALUES(?,?,?)",[(t,d,now) for t,d in tasks])
            self.send_json({"score":score,"weak_topics":weak,"recommendation":recommendation(weak)});return
        if path=="/api/tasks":
            title=str(data.get("title","")).strip()[:120]
            if not title:self.send_json({"error":"Task cannot be empty."},400);return
            with connect() as con:
                cur=con.execute("INSERT INTO tasks(title,duration,created_at) VALUES(?,?,?)",(title,"Personal",datetime.datetime.now().isoformat(timespec="seconds")))
                task_id=cur.lastrowid
            self.send_json({"id":task_id,"title":title},201);return
        if path=="/api/career":
            career=str(data.get("career","")).strip()[:80]
            with connect() as con: con.execute("UPDATE profile SET career=? WHERE id=1",(career,))
            self.send_json({"message":f"{career} saved as your selected career direction. Choose one skill from the list and build a small practice project."});return
        self.send_json({"error":"API route not found"},404)
    def do_PATCH(self):
        path=urlparse(self.path).path
        if path.startswith("/api/tasks/"):
            try: task_id=int(path.rsplit("/",1)[1]); data=self.body()
            except Exception: self.send_json({"error":"Invalid task request"},400);return
            with connect() as con:
                cur=con.execute("UPDATE tasks SET done=? WHERE id=?",(1 if data.get("done") else 0,task_id))
            if not cur.rowcount:self.send_json({"error":"Task not found"},404)
            else:self.send_json({"updated":True})
            return
        self.send_json({"error":"API route not found"},404)

if __name__=="__main__":
    init_db()
    host="127.0.0.1";port=8000
    url=f"http://{host}:{port}"
    print("\n==============================================")
    print("  StudyMentor is running!")
    print(f"  Open in your browser: {url}")
    print("  Keep this window open while using the app.")
    print("  Press Ctrl+C to stop the server.")
    print("==============================================\n")
    threading.Timer(1.0,lambda:webbrowser.open(url)).start()
    try: ThreadingHTTPServer((host,port),Handler).serve_forever()
    except KeyboardInterrupt: print("\nStudyMentor server stopped.")
