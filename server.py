import json
import os
import sqlite3
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = Path(os.environ.get("DATA_DIR", BASE_DIR))
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / "labor_service.db"


DEMANDS = [
    {
        "company": "柳东注塑厂（耀世）",
        "role": "注塑包装普工",
        "type": "短期工",
        "location": "柳东",
        "start": "2026-05-13",
        "end": "2026-06-13",
        "headcount": 30,
        "signed": 0,
        "salary": "16+1元/小时，综合5000-5500元",
        "age": "20-45岁",
        "notes": "男女不限，初中及以上，身体健康，无近视、色盲，两班倒8:30-20:30/20:30-8:30。主要剪水口、修毛边、打包装，小件产品，部分坐班。白班包工作餐，夜班无餐补贴5元/班，提供住宿。1元需做满一个月。面试穿长裤、运动鞋，女生扎头发，谢绝短裤、背心、拖鞋、凉鞋、披头散发。",
    },
    {
        "company": "柳东物流公司（方达）",
        "role": "物流普工",
        "type": "长期工",
        "location": "柳东",
        "start": "2026-05-13",
        "end": "",
        "headcount": 40,
        "signed": 0,
        "salary": "17元/小时，204元/天，综合5000-6000元",
        "age": "18-45岁",
        "notes": "男女不限，两班倒8:00-20:00/20:00-8:00，吃饭算工时。包吃包住，自助餐食堂，水电平摊。面试时间下午3:30，驻厂欧主管15677228332。",
    },
    {
        "company": "柳东官塘内饰厂（精特）",
        "role": "包覆工",
        "type": "长期工",
        "location": "柳东官塘",
        "start": "2026-05-13",
        "end": "",
        "headcount": 25,
        "signed": 0,
        "salary": "熟练工20元/小时，新手17元/小时，熟手1个月内转计件，计件可1万+",
        "age": "20-53岁",
        "notes": "男性优先，熟手年龄可放宽。每周可预支500元。包工作餐，提供集体宿舍，水电费平摊。面试必须带身份证原件，上午9点面试。",
    },
    {
        "company": "柳东花岭注塑厂（飞塑）",
        "role": "质检/普工/全检",
        "type": "短期工",
        "location": "柳东花岭",
        "start": "2026-05-13",
        "end": "2026-06-13",
        "headcount": 45,
        "signed": 0,
        "salary": "全检16元/小时，其他岗位面议",
        "age": "20-40岁",
        "notes": "坐班，可周结，不用体检，工作轻松，氛围好，智能管理车间。男女不限，能接受倒班。岗位：质检无需经验女工，普工无需经验男女不限，全检需经验16元/小时。包工作餐，住宿150元/月，水电平摊，宿舍安合华庭在厂区对面。上班时间8:30-20:30/20:30-8:30，上午11点面试。",
    },
    {
        "company": "柳东汽配厂（龙发）",
        "role": "上下挂岗位",
        "type": "长期工",
        "location": "柳东",
        "start": "2026-05-13",
        "end": "",
        "headcount": 20,
        "signed": 0,
        "salary": "17元/小时",
        "age": "20-45岁",
        "notes": "长白班，白班8-12小时，只要男性。包工作餐，包住宿，水电费平摊，员工宿舍在厂内。暂时不体检，不用经验，要求服从安排、吃苦耐劳、反应灵敏。吃饭不算工时。上午8:50面试，面试不通过不报销来回路费、油费、餐费等。",
    },
    {
        "company": "柳东汽配厂（震法）",
        "role": "手包管/开机学徒/套管打胶带",
        "type": "长期工",
        "location": "柳东",
        "start": "2026-05-13",
        "end": "",
        "headcount": 12,
        "signed": 0,
        "salary": "16-17元/小时，部分岗位后期计件",
        "age": "25-38岁",
        "notes": "长白班。手包管急招，28-38岁男女不限，16元/小时，适合有手工经验、耐心、手灵活，做满三个月后须计件，上班8:30-17:00，中午吃饭半小时不算工时，不加班，计件后不定时加班。挤出线开机学徒1名，28-38岁，有开机经验优先，17元/小时，吃饭不扣工时，8:30-17:30不定时加班。套管打胶带1名男生，25-35岁，人灵活，8:30-17:00，不定时加班。包吃，提供住宿安合华庭，骑车15分钟。下午2点面试。",
    },
    {
        "company": "柳东花岭装配岗位（超力）",
        "role": "装配工",
        "type": "短期工",
        "location": "柳东花岭",
        "start": "2026-05-13",
        "end": "2026-06-13",
        "headcount": 35,
        "signed": 0,
        "salary": "17元/小时，每天有效工时10小时",
        "age": "20-48岁",
        "notes": "长白班，可周结，男工。包吃，提供住宿，住宿走路5分钟。上班8:00-20:00，公司包吃两餐；上两小时休息10分钟，中午吃饭1小时，下午吃饭40分钟。第一个月自备全黑色劳保鞋，第二个月公司发劳保用品。工期稳定，工价不变。先试岗后体检，一个月内体检报告也可以。生产交换器总成和空调总成。上午11点面试。",
    },
    {
        "company": "柳东汽配厂（新纪元）",
        "role": "注塑操作工/检验员",
        "type": "长期工",
        "location": "柳州市鱼峰区车园",
        "start": "2026-05-13",
        "end": "",
        "headcount": 30,
        "signed": 0,
        "salary": "17+1元/小时，约216元/天，转正购买五险",
        "age": "20-45岁",
        "notes": "注塑操作工20-45岁，倒班，手脚麻利，服从安排。检验员1名，25-40岁女工，倒班，认真负责，有注塑件外观检验经验优先。每天10-12小时，吃饭算工时，两班倒。试工一天后体检，有体检报告也行。下午2点面试。面试穿长裤、运动鞋，女生扎头发，谢绝短裤、裙子、拖鞋、凉鞋、高跟鞋。",
    },
    {
        "company": "柳东花岭（星心）",
        "role": "注塑工",
        "type": "长期工",
        "location": "柳东花岭",
        "start": "2026-05-13",
        "end": "",
        "headcount": 35,
        "signed": 0,
        "salary": "17元/小时",
        "age": "18-45岁",
        "notes": "开注塑机生产产品。男女不限，能适应两班倒，有汽配注塑行业经验优先，有经验可放宽年龄。主要剪水口、修毛边、打包装，工作简单易上手。白班提供两餐，夜宵有牛奶面包等食物。下午3点面试。面试穿长裤、运动鞋，女生扎头发，谢绝短裤、背心、拖鞋、凉鞋、披头散发。",
    },
    {
        "company": "柳东花玲车标厂（贝驰）",
        "role": "车标生产岗位",
        "type": "短期工",
        "location": "柳东花玲",
        "start": "2026-05-13",
        "end": "2026-06-13",
        "headcount": 40,
        "signed": 0,
        "salary": "17元/小时，夜班补贴15元/晚，综合5000-5500元",
        "age": "20-45岁",
        "notes": "周结，空调车间，坐班，两班倒8:30-20:30/20:30-8:30。主要生产汽车小件车标。女工优先，手脚灵活，熟手年龄可放宽。包工作餐，提供住宿，宿舍走路2分钟。上午10点面试。",
    },
    {
        "company": "柳东官塘汽配厂（成华）",
        "role": "抛光工/普工/质检/备料员/河西售后",
        "type": "短期工",
        "location": "柳东官塘",
        "start": "2026-05-13",
        "end": "2026-06-13",
        "headcount": 80,
        "signed": 0,
        "salary": "普工/质检/备料员/河西售后16元/小时，2个月后加1元；抛光工27元/小时",
        "age": "17-50岁",
        "notes": "大量招聘，不用体检，男女不限，不能有纹身，两班倒。主要生产汽车塑料保险杠。提供宿舍安合华庭，包吃。中午吃饭休息半小时，下午半小时，每天有效工时11小时。可以周结，不扣工时。下午2点面试，面试者需要带身份证复印件。",
    },
    {
        "company": "柳东花岭新能源（奥德永兴）",
        "role": "激光焊/打磨工/悬挂焊/普工",
        "type": "季节工",
        "location": "柳东花岭",
        "start": "2026-04-24",
        "end": "2026-07-31",
        "headcount": 100,
        "signed": 0,
        "salary": "激光焊25+3元/小时，打磨工19+3元/小时，悬挂焊21+3元/小时，普工17+3元/小时",
        "age": "18-53岁",
        "notes": "负责新能源汽车电池壳装配生产。入职满一个月+3元/小时，用工单价调整自2026年4月24日至2026年7月31日止，入职不满一个月离职不享受调整后单价。两班倒8对8，工作8-12小时。工厂食堂扣2元/餐，宿舍150元/月，水电费平摊。男工，女工可做普工，18-48岁，不用体检，新手也可以。上午10:30面试，人多下午也可安排。",
    },
]

WORKERS = [
    {
        "name": "张伟",
        "location": "柳东",
        "available": "现在可到岗",
        "period": "长期稳定",
        "salary": "5000以上",
        "score": 92,
        "tags": "注塑经验, 接受夜班, 需要住宿, 到岗率高",
    },
    {
        "name": "李娜",
        "location": "柳东花岭",
        "available": "本周可到岗",
        "period": "1-3个月",
        "salary": "17元/小时以上",
        "score": 86,
        "tags": "质检, 女工, 坐班, 稳定",
    },
    {
        "name": "王强",
        "location": "柳东官塘",
        "available": "现在可到岗",
        "period": "7-15天",
        "salary": "周结优先",
        "score": 78,
        "tags": "汽配厂, 抛光, 可加班, 短期工",
    },
    {
        "name": "陈晨",
        "location": "柳东",
        "available": "下周可到岗",
        "period": "长期稳定",
        "salary": "5500以上",
        "score": 84,
        "tags": "物流普工, 接受夜班, 无经验可培训, 需要住宿",
    },
    {
        "name": "赵敏",
        "location": "柳东花玲",
        "available": "暑假可做",
        "period": "暑假工",
        "salary": "17元/小时以上",
        "score": 81,
        "tags": "短期工, 包装, 坐班, 接受夜班",
    },
]


def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with connect() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS demands (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company TEXT NOT NULL,
                role TEXT NOT NULL,
                type TEXT NOT NULL,
                location TEXT NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT DEFAULT '',
                headcount INTEGER NOT NULL DEFAULT 0,
                signed INTEGER NOT NULL DEFAULT 0,
                salary TEXT DEFAULT '',
                age TEXT DEFAULT '',
                notes TEXT DEFAULT '',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS workers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT DEFAULT '',
                gender TEXT DEFAULT '',
                age TEXT DEFAULT '',
                location TEXT NOT NULL,
                available TEXT DEFAULT '',
                period TEXT DEFAULT '',
                expected_role TEXT DEFAULT '',
                salary TEXT DEFAULT '',
                score INTEGER NOT NULL DEFAULT 70,
                tags TEXT DEFAULT '',
                note TEXT DEFAULT '',
                source TEXT DEFAULT '',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS chat_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL,
                text TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS knowledge_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                title TEXT NOT NULL,
                summary TEXT NOT NULL,
                source TEXT DEFAULT '',
                entity_type TEXT DEFAULT '',
                entity_id INTEGER DEFAULT 0,
                tags TEXT DEFAULT '',
                confidence INTEGER NOT NULL DEFAULT 80,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
        ensure_worker_columns(conn)
        ensure_knowledge_columns(conn)
        demand_count = conn.execute("SELECT COUNT(*) FROM demands").fetchone()[0]
        if demand_count == 0:
            conn.executemany(
                """
                INSERT INTO demands
                (company, role, type, location, start_date, end_date, headcount, signed, salary, age, notes)
                VALUES (:company, :role, :type, :location, :start, :end, :headcount, :signed, :salary, :age, :notes)
                """,
                DEMANDS,
            )
        worker_count = conn.execute("SELECT COUNT(*) FROM workers").fetchone()[0]
        if worker_count == 0:
            conn.executemany(
                """
                INSERT INTO workers
                (name, location, available, period, salary, score, tags)
                VALUES (:name, :location, :available, :period, :salary, :score, :tags)
                """,
                WORKERS,
            )
        chat_count = conn.execute("SELECT COUNT(*) FROM chat_messages").fetchone()[0]
        if chat_count == 0:
            conn.execute(
                "INSERT INTO chat_messages (role, text) VALUES (?, ?)",
                (
                    "assistant",
                    "你好，我会根据本地企业需求、全年排期和求职者档案回答问题。可以问我：下个月有哪些缺口、某个求职者适合去哪、或者帮你生成招聘文案。",
                ),
            )
        sync_knowledge_entries(conn)


def ensure_worker_columns(conn):
    existing = {row["name"] for row in conn.execute("PRAGMA table_info(workers)")}
    columns = {
        "phone": "TEXT DEFAULT ''",
        "gender": "TEXT DEFAULT ''",
        "age": "TEXT DEFAULT ''",
        "expected_role": "TEXT DEFAULT ''",
        "note": "TEXT DEFAULT ''",
        "source": "TEXT DEFAULT ''",
    }
    for name, definition in columns.items():
        if name not in existing:
            conn.execute(f"ALTER TABLE workers ADD COLUMN {name} {definition}")


def ensure_knowledge_columns(conn):
    existing = {row["name"] for row in conn.execute("PRAGMA table_info(knowledge_entries)")}
    columns = {
        "source": "TEXT DEFAULT ''",
        "entity_type": "TEXT DEFAULT ''",
        "entity_id": "INTEGER DEFAULT 0",
        "tags": "TEXT DEFAULT ''",
        "confidence": "INTEGER NOT NULL DEFAULT 80",
        "updated_at": "TEXT DEFAULT CURRENT_TIMESTAMP",
    }
    for name, definition in columns.items():
        if name not in existing:
            conn.execute(f"ALTER TABLE knowledge_entries ADD COLUMN {name} {definition}")


def row_to_demand(row):
    return {
        "id": row["id"],
        "company": row["company"],
        "role": row["role"],
        "type": row["type"],
        "location": row["location"],
        "start": row["start_date"],
        "end": row["end_date"] or "",
        "headcount": row["headcount"],
        "signed": row["signed"],
        "salary": row["salary"],
        "age": row["age"],
        "notes": row["notes"],
    }


def row_to_worker(row):
    return {
        "id": row["id"],
        "name": row["name"],
        "phone": row["phone"],
        "gender": row["gender"],
        "age": row["age"],
        "location": row["location"],
        "available": row["available"],
        "period": row["period"],
        "expectedRole": row["expected_role"],
        "salary": row["salary"],
        "score": row["score"],
        "note": row["note"],
        "source": row["source"],
        "tags": [item.strip() for item in (row["tags"] or "").replace("，", ",").split(",") if item.strip()],
    }


def row_to_knowledge(row):
    return {
        "id": row["id"],
        "category": row["category"],
        "title": row["title"],
        "summary": row["summary"],
        "source": row["source"],
        "entityType": row["entity_type"],
        "entityId": row["entity_id"],
        "tags": [item.strip() for item in (row["tags"] or "").replace("，", ",").split(",") if item.strip()],
        "confidence": row["confidence"],
        "createdAt": row["created_at"],
        "updatedAt": row["updated_at"],
    }


def upsert_knowledge_entry(conn, category, title, summary, source, entity_type, entity_id, tags, confidence=80):
    tags_text = ", ".join(tags) if isinstance(tags, list) else str(tags or "")
    existing = conn.execute(
        "SELECT id FROM knowledge_entries WHERE entity_type = ? AND entity_id = ? AND category = ?",
        (entity_type, entity_id, category),
    ).fetchone()
    if existing:
        conn.execute(
            """
            UPDATE knowledge_entries
            SET title = ?, summary = ?, source = ?, tags = ?, confidence = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (title, summary, source, tags_text, confidence, existing["id"]),
        )
    else:
        conn.execute(
            """
            INSERT INTO knowledge_entries
            (category, title, summary, source, entity_type, entity_id, tags, confidence)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (category, title, summary, source, entity_type, entity_id, tags_text, confidence),
        )


def demand_knowledge(row):
    demand = row_to_demand(row)
    tags = [
        demand["type"],
        demand["location"],
        demand["role"],
        "周结" if "周结" in demand["notes"] else "",
        "不用体检" if "不用体检" in demand["notes"] else "",
        "夜班" if "夜班" in demand["notes"] or "两班倒" in demand["notes"] else "",
        "住宿" if "住宿" in demand["notes"] or "宿舍" in demand["notes"] else "",
    ]
    tags = [item for item in tags if item]
    summary = (
        f"{demand['company']}招聘{demand['role']}，{demand['type']}，地点{demand['location']}，"
        f"需求{demand['headcount']}人，已报名{demand['signed']}人，薪资{demand['salary']}，"
        f"年龄要求{demand['age'] or '未填写'}。关键规则：{demand['notes']}"
    )
    return {
        "category": "企业岗位规则",
        "title": f"{demand['company']}｜{demand['role']}",
        "summary": summary,
        "source": "企业需求维护",
        "entity_type": "demand",
        "entity_id": demand["id"],
        "tags": tags,
        "confidence": 90,
    }


def worker_knowledge(row):
    worker = row_to_worker(row)
    tags = worker["tags"] + [worker["location"], worker["period"], worker["expectedRole"], worker["source"]]
    tags = [item for item in tags if item]
    summary = (
        f"{worker['name']}，{worker.get('gender') or '性别未填'}，{worker.get('age') or '年龄未填'}岁，"
        f"电话{worker.get('phone') or '未填'}，当前地区{worker['location']}，{worker['available']}，"
        f"期望周期{worker['period']}，期望岗位{worker['expectedRole'] or '未填'}，期望薪资{worker['salary'] or '未填'}。"
        f"备注：{worker['note'] or '无'}"
    )
    return {
        "category": "求职者画像",
        "title": f"{worker['name']}｜{worker['location']}｜{worker['period']}",
        "summary": summary,
        "source": worker["source"] or "求职者维护",
        "entity_type": "worker",
        "entity_id": worker["id"],
        "tags": tags,
        "confidence": 82,
    }


def sync_knowledge_entries(conn):
    for row in conn.execute("SELECT * FROM demands"):
        item = demand_knowledge(row)
        upsert_knowledge_entry(conn, **item)
    for row in conn.execute("SELECT * FROM workers"):
        item = worker_knowledge(row)
        upsert_knowledge_entry(conn, **item)


def build_insights(demands, workers):
    total_gap = sum(max(int(item["headcount"]) - int(item.get("signed") or 0), 0) for item in demands)
    high_gap = sorted(demands, key=lambda item: max(int(item["headcount"]) - int(item.get("signed") or 0), 0), reverse=True)[:5]
    weekly = [item for item in demands if "周结" in item["notes"]]
    no_exam = [item for item in demands if "不用体检" in item["notes"] or "不体检" in item["notes"]]
    night = [worker for worker in workers if any("夜班" in tag for tag in worker["tags"])]
    self_registered = [worker for worker in workers if worker.get("source") == "求职者自助登记"]
    return {
        "totalGap": total_gap,
        "highGap": [
            {
                "title": f"{item['company']} {item['role']}",
                "value": max(int(item["headcount"]) - int(item.get("signed") or 0), 0),
                "note": item["salary"],
            }
            for item in high_gap
        ],
        "weeklyJobs": [{"title": f"{item['company']} {item['role']}", "note": item["salary"]} for item in weekly[:8]],
        "noExamJobs": [{"title": f"{item['company']} {item['role']}", "note": item["age"]} for item in no_exam[:8]],
        "nightWorkers": [{"title": worker["name"], "note": "、".join(worker["tags"])} for worker in night[:8]],
        "selfRegisteredCount": len(self_registered),
    }


def get_payload():
    with connect() as conn:
        sync_knowledge_entries(conn)
        demands = [row_to_demand(row) for row in conn.execute("SELECT * FROM demands ORDER BY start_date, id")]
        workers = [row_to_worker(row) for row in conn.execute("SELECT * FROM workers ORDER BY id DESC")]
        chat = [dict(row) for row in conn.execute("SELECT role, text FROM chat_messages ORDER BY id")]
        knowledge = [
            row_to_knowledge(row)
            for row in conn.execute("SELECT * FROM knowledge_entries ORDER BY updated_at DESC, id DESC")
        ]
    return {"demands": demands, "workers": workers, "chat": chat, "knowledge": knowledge, "insights": build_insights(demands, workers)}


def reset_seed_data():
    with connect() as conn:
        conn.execute("DELETE FROM chat_messages")
        conn.execute("DELETE FROM workers")
        conn.execute("DELETE FROM demands")
        conn.execute("DELETE FROM knowledge_entries")
        conn.executemany(
            """
            INSERT INTO demands
            (company, role, type, location, start_date, end_date, headcount, signed, salary, age, notes)
            VALUES (:company, :role, :type, :location, :start, :end, :headcount, :signed, :salary, :age, :notes)
            """,
            DEMANDS,
        )
        conn.executemany(
            """
            INSERT INTO workers
            (name, location, available, period, salary, score, tags)
            VALUES (:name, :location, :available, :period, :salary, :score, :tags)
            """,
            WORKERS,
        )
        conn.execute(
            "INSERT INTO chat_messages (role, text) VALUES (?, ?)",
            (
                "assistant",
                "已恢复乐颜提供的企业用工数据和演示求职者库，可以继续查询和推荐。",
            ),
        )
        sync_knowledge_entries(conn)


class Handler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/data":
            self.send_json(get_payload())
            return
        if parsed.path == "/":
            self.path = "/index.html"
        super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/demands":
            body = self.read_json()
            with connect() as conn:
                cursor = conn.execute(
                    """
                    INSERT INTO demands
                    (company, role, type, location, start_date, end_date, headcount, signed, salary, age, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        body.get("company", "").strip(),
                        body.get("role", "").strip(),
                        body.get("type", "长期工"),
                        body.get("location", "").strip(),
                        body.get("start", ""),
                        body.get("end", ""),
                        int(body.get("headcount") or 0),
                        int(body.get("signed") or 0),
                        body.get("salary", "").strip(),
                        body.get("age", "").strip(),
                        body.get("notes", "").strip(),
                    ),
                )
            self.send_json({"ok": True, "id": cursor.lastrowid, "data": get_payload()})
            return
        if parsed.path == "/api/workers":
            body = self.read_json()
            tags = body.get("tags", [])
            if isinstance(tags, list):
                tags = ", ".join(tags)
            with connect() as conn:
                cursor = conn.execute(
                    """
                    INSERT INTO workers
                    (name, phone, gender, age, location, available, period, expected_role, salary, score, tags, note, source)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        body.get("name", "").strip(),
                        body.get("phone", "").strip(),
                        body.get("gender", "").strip(),
                        str(body.get("age", "")).strip(),
                        body.get("location", "").strip(),
                        body.get("available", "").strip(),
                        body.get("period", ""),
                        body.get("expectedRole", body.get("expected_role", "")).strip(),
                        body.get("salary", "").strip(),
                        int(body.get("score") or 70),
                        str(tags),
                        body.get("note", "").strip(),
                        body.get("source", "业务员录入").strip(),
                    ),
                )
            self.send_json({"ok": True, "id": cursor.lastrowid, "data": get_payload()})
            return
        if parsed.path == "/api/chat":
            body = self.read_json()
            question = body.get("question", "").strip()
            if not question:
                self.send_json({"ok": False, "error": "问题不能为空"}, status=400)
                return
            payload = get_payload()
            answer = answer_question(question, payload)
            with connect() as conn:
                conn.execute("INSERT INTO chat_messages (role, text) VALUES (?, ?)", ("user", question))
                conn.execute("INSERT INTO chat_messages (role, text) VALUES (?, ?)", ("assistant", answer))
            self.send_json({"ok": True, "answer": answer, "data": get_payload()})
            return
        if parsed.path == "/api/reset":
            reset_seed_data()
            self.send_json({"ok": True, "data": get_payload()})
            return
        if parsed.path == "/api/knowledge/rebuild":
            with connect() as conn:
                conn.execute("DELETE FROM knowledge_entries")
                sync_knowledge_entries(conn)
            self.send_json({"ok": True, "data": get_payload()})
            return
        self.send_json({"ok": False, "error": "接口不存在"}, status=404)

    def read_json(self):
        length = int(self.headers.get("Content-Length", "0") or 0)
        raw = self.rfile.read(length).decode("utf-8") if length else "{}"
        return json.loads(raw or "{}")

    def send_json(self, payload, status=200):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def remaining(demand):
    return max(int(demand["headcount"]) - int(demand.get("signed") or 0), 0)


def rank_workers(demand, workers):
    ranked = []
    demand_text = f"{demand['company']} {demand['role']} {demand['type']} {demand['location']} {demand['notes']}".lower()
    for worker in workers:
        score = round(int(worker.get("score") or 70) * 0.45)
        reasons = []
        worker_text = f"{worker['location']} {worker['available']} {worker['period']} {' '.join(worker['tags'])}".lower()
        if worker["location"].lower() in demand_text or demand["location"][:2].lower() in worker_text:
            score += 14
            reasons.append("地区接近")
        if any(tag[:2].lower() in demand_text for tag in worker["tags"] if len(tag) >= 2):
            score += 16
            reasons.append("岗位经验匹配")
        if "短期" in demand["type"] and ("暑假" in worker["period"] or "7-15" in worker["period"] or "短期工" in worker["tags"]):
            score += 14
            reasons.append("可做短期")
        if "长期" in demand["type"] and "长期" in worker["period"]:
            score += 14
            reasons.append("适合长期稳定")
        if "夜班" in demand["notes"] and any("夜班" in tag for tag in worker["tags"]):
            score += 12
            reasons.append("接受夜班")
        if "住宿" in demand["notes"] and any("住宿" in tag for tag in worker["tags"]):
            score += 8
            reasons.append("住宿需求一致")
        for keyword in ["包装", "分拣", "质检", "注塑", "物流", "抛光", "坐班"]:
            if keyword in demand["role"] + demand["notes"] and any(keyword in tag for tag in worker["tags"]):
                score += 10
                reasons.append(f"{keyword}匹配")
                break
        ranked.append({"worker": worker, "score": min(score, 100), "reasons": reasons})
    return sorted(ranked, key=lambda item: item["score"], reverse=True)


def answer_question(question, payload):
    q = question.lower()
    demands = payload["demands"]
    workers = payload["workers"]
    knowledge = payload.get("knowledge", [])
    if "知识库" in q:
        categories = {}
        for item in knowledge:
            categories[item["category"]] = categories.get(item["category"], 0) + 1
        detail = "、".join(f"{name}{count}条" for name, count in categories.items())
        return f"当前私有知识库共有 {len(knowledge)} 条知识，包含：{detail or '暂无分类'}。知识来源包括企业需求维护、求职者自助登记和业务员录入。"
    if "周结" in q:
        items = [item for item in demands if "周结" in item["notes"]]
        return format_demand_answer("支持周结的岗位", items, workers)
    if "不用体检" in q or "不体检" in q:
        items = [item for item in demands if "不用体检" in item["notes"] or "不体检" in item["notes"]]
        return format_demand_answer("不用体检或暂不体检的岗位", items, workers)
    if "短期" in q or "下个月" in q:
        items = [item for item in demands if "短期" in item["type"]]
        return format_demand_answer("短期工相关需求", items, workers)
    if "暑假" in q or "季节" in q:
        items = [item for item in demands if item["type"] == "季节工" or "暑假" in item["notes"]]
        return format_demand_answer("适合暑假工或阶段性预招募的岗位", items, workers)
    if "夜班" in q:
        matched = [worker for worker in workers if any("夜班" in tag for tag in worker["tags"])]
        return "适合夜班岗位的人选：\n" + "\n".join(
            f"- {worker['name']}：{worker['location']}，{worker['available']}，标签：{'、'.join(worker['tags'])}" for worker in matched
        )
    if "文案" in q or "招聘" in q:
        target = sorted(demands, key=remaining, reverse=True)[0]
        return (
            f"招聘文案草稿：\n{target['company']}招聘{target['role']}，{target['type']}，需求{target['headcount']}人，"
            f"目前剩余{remaining(target)}个名额。工作地点{target['location']}，薪资{target['salary']}，时间{target['start']}至{target['end'] or '长期'}。"
            f"{target['notes']} 有意向的求职者请联系业务员报名，系统会优先安排匹配度高、可按时到岗的人选。"
        )
    for worker in workers:
        if worker["name"].lower() in q:
            best = sorted(
                [{"demand": demand, **next(item for item in rank_workers(demand, workers) if item["worker"]["id"] == worker["id"])} for demand in demands],
                key=lambda item: item["score"],
                reverse=True,
            )[0]
            demand = best["demand"]
            return (
                f"{worker['name']} 推荐岗位：{demand['company']} {demand['role']}，匹配度 {best['score']} 分。\n"
                f"推荐理由：{'、'.join(best['reasons']) or '基础条件较接近'}。\n"
                f"岗位信息：{demand['location']}，{demand['salary']}，当前缺口 {remaining(demand)} 人。"
            )
    for demand in demands:
        if demand["company"].lower() in q:
            return format_demand_answer(f"{demand['company']} 的用工知识", [item for item in demands if item["company"] == demand["company"]], workers)
    total_gap = sum(remaining(item) for item in demands)
    return f"本地知识库当前有 {len(demands)} 条企业需求、{len(workers)} 名求职者、总缺口 {total_gap} 人。你可以问某家企业有哪些岗位、某个求职者适合去哪、哪些岗位适合暑假工，或者让我生成招聘文案。"


def format_demand_answer(title, items, workers):
    if not items:
        return f"{title}：暂未找到匹配记录。"
    lines = [f"{title}："]
    for item in items:
        matches = "、".join(f"{match['worker']['name']}{match['score']}分" for match in rank_workers(item, workers)[:3])
        lines.append(
            f"- {item['company']} {item['role']}：{item['type']}，{item['start']}至{item['end'] or '长期'}，缺 {remaining(item)} 人，{item['salary']}。建议人选：{matches or '暂无'}"
        )
    return "\n".join(lines)


if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", "8000"))
    server = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    print(f"劳务中介系统已启动：http://127.0.0.1:{port}")
    server.serve_forever()
