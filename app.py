
from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime, date
app = Flask(__name__)

DATABASE = "medication.db"


# 連接資料庫
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# 建立資料庫
def init_db():
    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS medications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            time TEXT NOT NULL,
            note TEXT NOT NULL
        )
    """)

    # 建立服藥紀錄資料表
    conn.execute("""
        CREATE TABLE IF NOT EXISTS medication_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            medication_id INTEGER NOT NULL,
            record_date TEXT NOT NULL,
            status TEXT NOT NULL,
            recorded_at TEXT NOT NULL,
            UNIQUE(medication_id, record_date),
            FOREIGN KEY (medication_id)
                REFERENCES medications(id)
        )
    """)

    conn.commit()
    conn.close()


# 系統首頁

# 系統首頁
@app.route("/")
def home():

    today = date.today().isoformat()

    conn = get_db_connection()

    # 計算目前用藥項目總數
    total_count = conn.execute("""
        SELECT COUNT(*)
        FROM medications
    """).fetchone()[0]

    # 計算今天已服用的數量
    taken_count = conn.execute("""
        SELECT COUNT(*)
        FROM medication_records
        WHERE record_date = ?
        AND status = '已服用'
        AND medication_id IN (
            SELECT id FROM medications
        )
    """, (today,)).fetchone()[0]

    # 計算今天稍後處理的數量
    later_count = conn.execute("""
        SELECT COUNT(*)
        FROM medication_records
        WHERE record_date = ?
        AND status = '稍後處理'
        AND medication_id IN (
            SELECT id FROM medications
        )
    """, (today,)).fetchone()[0]

    pending_count = total_count - taken_count - later_count

    conn.close()

    return render_template(
        "index.html",
        total_count=total_count,
        taken_count=taken_count,
        later_count=later_count,
        pending_count=pending_count
    )



# 用藥清單與新增藥品
@app.route("/medication", methods=["GET", "POST"])
def medication():

    # 使用者按下儲存按鈕
    if request.method == "POST":
        name = request.form.get("medicine_name", "").strip()
        time = request.form.get("medicine_time", "").strip()
        note = request.form.get("medicine_note", "").strip()

        # 確認欄位都有填寫
        if name and time and note:
            conn = get_db_connection()

            conn.execute(
                "INSERT INTO medications (name, time, note) VALUES (?, ?, ?)",
                (name, time, note)
            )

            conn.commit()
            conn.close()

        return redirect(url_for("medication"))

    # 讀取所有藥品
    conn = get_db_connection()

    medications = conn.execute(
        "SELECT * FROM medications ORDER BY time ASC"
    ).fetchall()

    conn.close()

    return render_template(
        "medication.html",
        medications=medications
    )


# 刪除藥品
@app.route("/medication/delete/<int:medicine_id>", methods=["POST"])
def delete_medication(medicine_id):

    conn = get_db_connection()

    conn.execute(
        "DELETE FROM medications WHERE id = ?",
        (medicine_id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("medication"))


# 修改藥品
@app.route("/medication/edit/<int:medicine_id>", methods=["GET", "POST"])
def edit_medication(medicine_id):

    conn = get_db_connection()

    # 查詢要修改的藥品
    medicine = conn.execute(
        "SELECT * FROM medications WHERE id = ?",
        (medicine_id,)
    ).fetchone()

    # 找不到藥品
    if medicine is None:
        conn.close()
        return "找不到這筆藥品資料", 404

    # 使用者送出修改資料
    if request.method == "POST":

        name = request.form.get("medicine_name", "").strip()
        time = request.form.get("medicine_time", "").strip()
        note = request.form.get("medicine_note", "").strip()

        # 確認欄位都有填寫
        if not name or not time or not note:
            conn.close()
            return "請填寫所有欄位", 400

        # 更新資料庫
        conn.execute(
            """
            UPDATE medications
            SET name = ?, time = ?, note = ?
            WHERE id = ?
            """,
            (name, time, note, medicine_id)
        )

        conn.commit()
        conn.close()

        return redirect(url_for("medication"))

    conn.close()

    # 顯示修改頁面
    return render_template(
        "edit_medication.html",
        medicine=medicine
    )


# 用藥提醒頁面

# 用藥提醒頁面

# 用藥提醒頁面

# 用藥提醒頁面

# 用藥提醒頁面
@app.route("/reminder")
def reminder():

    today = date.today().isoformat()

    conn = get_db_connection()

    # 讀取用藥時程與今日狀態
    medications = conn.execute("""
        SELECT
            m.id,
            m.name,
            m.time,
            m.note,
            r.status,
            r.recorded_at
        FROM medications m
        LEFT JOIN medication_records r
            ON m.id = r.medication_id
            AND r.record_date = ?
        ORDER BY m.time ASC
    """, (today,)).fetchall()

    # 讀取今日服藥紀錄
    records = conn.execute("""
        SELECT
            m.name,
            m.time,
            r.status,
            r.recorded_at
        FROM medication_records r
        JOIN medications m
            ON r.medication_id = m.id
        WHERE r.record_date = ?
        ORDER BY r.recorded_at DESC
    """, (today,)).fetchall()

    # 計算今日用藥統計
    total_count = len(medications)

    taken_count = sum(
        1 for medicine in medications
        if medicine["status"] == "已服用"
    )

    later_count = sum(
        1 for medicine in medications
        if medicine["status"] == "稍後處理"
    )

    pending_count = total_count - taken_count - later_count

    conn.close()


    # 將 SQLite Row 轉換為一般字典
    medications = [dict(medicine) for medicine in medications]

    return render_template(
        "reminder.html",
        medications=medications,
        records=records,
        today=today,
        total_count=total_count,
        taken_count=taken_count,
        later_count=later_count,
        pending_count=pending_count
    )


    today = date.today().isoformat()

    conn = get_db_connection()

    # 讀取用藥時程與今日狀態
    medications = conn.execute("""
        SELECT
            m.id,
            m.name,
            m.time,
            m.note,
            r.status,
            r.recorded_at
        FROM medications m
        LEFT JOIN medication_records r
            ON m.id = r.medication_id
            AND r.record_date = ?
        ORDER BY m.time ASC
    """, (today,)).fetchall()

    # 讀取今天有操作紀錄的藥品
    records = conn.execute("""
        SELECT
            m.name,
            m.time,
            r.status,
            r.recorded_at
        FROM medication_records r
        JOIN medications m
            ON r.medication_id = m.id
        WHERE r.record_date = ?
        ORDER BY r.recorded_at DESC
    """, (today,)).fetchall()

    conn.close()

    return render_template(
        "reminder.html",
        medications=medications,
        records=records,
        today=today
    )


    today = date.today().isoformat()

    conn = get_db_connection()

    medications = conn.execute("""
        SELECT
            m.id,
            m.name,
            m.time,
            m.note,
            r.status,
            r.recorded_at
        FROM medications m
        LEFT JOIN medication_records r
            ON m.id = r.medication_id
            AND r.record_date = ?
        ORDER BY m.time ASC
    """, (today,)).fetchall()

    conn.close()

    return render_template(
        "reminder.html",
        medications=medications
    )


    # 連接 SQLite 資料庫
    conn = get_db_connection()

    # 讀取所有藥品，依照服藥時間排序
    medications = conn.execute(
        "SELECT * FROM medications ORDER BY time ASC"
    ).fetchall()

    conn.close()

    # 將藥品資料傳送到提醒頁面
    return render_template(
        "reminder.html",
        medications=medications
    )


# 記錄已服用
@app.route("/medication/taken/<int:medicine_id>", methods=["POST"])
def mark_taken(medicine_id):

    # 取得今天日期與目前時間
    today = date.today().isoformat()
    now = datetime.now().isoformat(timespec="seconds")

    conn = get_db_connection()

    # 確認藥品存在
    medicine = conn.execute(
        "SELECT id FROM medications WHERE id = ?",
        (medicine_id,)
    ).fetchone()

    if medicine is None:
        conn.close()
        return "找不到這筆藥品", 404

    # 儲存或更新今日服藥紀錄
    conn.execute("""
        INSERT INTO medication_records
        (medication_id, record_date, status, recorded_at)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(medication_id, record_date)
        DO UPDATE SET
            status = excluded.status,
            recorded_at = excluded.recorded_at
    """, (medicine_id, today, "已服用", now))

    conn.commit()
    conn.close()

    return redirect(url_for("reminder"))

# 稍後處理
@app.route("/medication/later/<int:medicine_id>", methods=["POST"])
def mark_later(medicine_id):

    today = date.today().isoformat()
    now = datetime.now().isoformat(timespec="seconds")

    conn = get_db_connection()

    # 確認藥品存在
    medicine = conn.execute(
        "SELECT id FROM medications WHERE id = ?",
        (medicine_id,)
    ).fetchone()

    if medicine is None:
        conn.close()
        return "找不到這筆藥品", 404

    # 新增或更新今日狀態
    conn.execute("""
        INSERT INTO medication_records
        (medication_id, record_date, status, recorded_at)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(medication_id, record_date)
        DO UPDATE SET
            status = excluded.status,
            recorded_at = excluded.recorded_at
    """, (medicine_id, today, "稍後處理", now))

    conn.commit()
    conn.close()

    return redirect(url_for("reminder"))

# 服藥歷史紀錄查詢
@app.route("/history")
def history():

    # 取得使用者選擇的日期，預設今天
    selected_date = request.args.get(
        "date", date.today().isoformat()
    )

    # 檢查日期格式
    try:
        date.fromisoformat(selected_date)
    except ValueError:
        selected_date = date.today().isoformat()

    conn = get_db_connection()

    # 查詢指定日期的服藥紀錄
    records = conn.execute("""
        SELECT
            m.name,
            m.time,
            r.status,
            r.recorded_at
        FROM medication_records r
        JOIN medications m
            ON r.medication_id = m.id
        WHERE r.record_date = ?
        ORDER BY r.recorded_at DESC
    """, (selected_date,)).fetchall()

    conn.close()

    return render_template(
        "history.html",
        records=records,
        selected_date=selected_date
    )


# 啟動 Flask 網站前，先初始化資料庫
init_db()

if __name__ == "__main__":
    app.run(debug=True)
