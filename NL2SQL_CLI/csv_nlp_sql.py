import sys
import csv
import sqlite3
import re
from tabulate import tabulate

# --- CSV to SQLite in-memory DB ---
def read_csv_make_db(csv_file, table_name="data"):
    conn = sqlite3.connect(":memory:")
    cur = conn.cursor()

    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        headers = next(reader)
        headers_cleaned = [re.sub(r'[^a-zA-Z0-9_]', '', h.strip().replace(" ", "_")) for h in headers]

        sample_rows = []
        for _ in range(10):
            try:
                sample_rows.append(next(reader))
            except StopIteration:
                break

        types = []
        for i, h in enumerate(headers_cleaned):
            col = [row[i].replace('.', '', 1) for row in sample_rows if len(row) > i]
            if col and all(c.replace('-','').replace('.','',1).isdigit() for c in col if c):
                types.append("INTEGER")
            else:
                types.append("TEXT")

        columns_create = ', '.join(f"{h} {t}" for h, t in zip(headers_cleaned, types))
        cur.execute(f"CREATE TABLE {table_name} ({columns_create});")

        to_insert = sample_rows + list(reader)
        for row in to_insert:
            values = [r.strip() for r in row]
            cur.execute(
                f'INSERT INTO {table_name} VALUES ({",".join("?"*len(headers_cleaned))})',
                values
            )
        conn.commit()
    return conn, headers_cleaned, types

# --- Parse ordinals ---
def parse_ordinal(nlq):
    d = {"first":1,"second":2,"third":3,"fourth":4,"fifth":5,"sixth":6,"seventh":7,"eighth":8,"ninth":9,"tenth":10}
    for k, v in d.items():
        if k in nlq:
            return v
    return None

# --- Natural language to SQL ---
def nl_to_sql(nlq, headers, types, table_name="data"):
    q = nlq.lower()
    selected = [h for h in headers if h.lower() in q]
    sql = ""

    # COUNT
    if "count" in q or "how many" in q:
        h = selected[0] if selected else "*"
        sql = f"SELECT COUNT({h}) FROM {table_name}"

    # SUM / TOTAL
    elif "sum" in q or "total" in q:
        for h, t in zip(headers, types):
            if h.lower() in q and t == "INTEGER":
                sql = f"SELECT SUM({h}) FROM {table_name}"
                break

    # AVG
    elif "average" in q or "avg" in q:
        for h, t in zip(headers, types):
            if h.lower() in q and t == "INTEGER":
                sql = f"SELECT AVG({h}) FROM {table_name}"
                break

    # MAX / MIN
    elif any(x in q for x in ["max","maximum","highest"]):
        for h, t in zip(headers, types):
            if h.lower() in q and t == "INTEGER":
                sql = f"SELECT MAX({h}) FROM {table_name}"
                break
    elif any(x in q for x in ["min","minimum","lowest"]):
        for h, t in zip(headers, types):
            if h.lower() in q and t == "INTEGER":
                sql = f"SELECT MIN({h}) FROM {table_name}"
                break

    # SELECT *
    elif "all" in q or "*" in q:
        sql = f"SELECT * FROM {table_name}"
    elif selected:
        sql = f"SELECT {', '.join(selected)} FROM {table_name}"
    else:
        sql = f"SELECT * FROM {table_name}"

    # Ordinals
    ordinal = parse_ordinal(q)
    if ordinal and any(x in q for x in ["max","highest"]):
        for h, t in zip(headers, types):
            if h.lower() in q and t=="INTEGER":
                sql = f"SELECT {h} FROM {table_name} ORDER BY {h} DESC LIMIT 1 OFFSET {ordinal-1}"
                break

    # WHERE clause for filters
    for h, t in zip(headers, types):
        # numeric comparison
        patt_num = re.search(rf"{h.lower()} *(=|>|<|>=|<=) *([\d.]+)", q)
        if patt_num:
            op, val = patt_num.group(1), patt_num.group(2)
            sql += f" WHERE {h} {op} {val}"
            break
        # text equality
        patt_txt = re.search(rf"{h.lower()} *(is|=|=?) *'?(.*?)'?", q)
        if patt_txt:
            val = patt_txt.group(2).strip()
            if val:
                sql += f" WHERE {h}='{val}'"
                break
        # simple 'from cityname' pattern
        patt_from = re.search(rf"from (\w+)", q)
        if patt_from and h.lower() in ["city","grade","name"]:
            sql += f" WHERE {h}='{patt_from.group(1)}'"
            break

    # ORDER BY clause
    if "order by" in q:
        ob = q.split("order by")[1].split()[0]
        for h in headers:
            if h.lower() in ob:
                desc = "DESC" if "desc" in q or "highest" in q else "ASC"
                sql += f" ORDER BY {h} {desc}"
                break

    return sql.strip()

# --- Main CLI ---
def main():
    if len(sys.argv)<3:
        print("Usage: python csv_nlp_sql.py <csv_file> <natural language query>")
        sys.exit(1)
    csvfile = sys.argv[1]
    q = sys.argv[2]

    try:
        conn, headers, types = read_csv_make_db(csvfile)
        sql = nl_to_sql(q, headers, types)
        # print(f"Generated SQL:\n{sql}") # optional debug
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        headers_disp = [desc[0] for desc in cur.description] if cur.description else []
        if rows and len(rows)==1 and len(rows[0])==1:
            print(rows[0][0])
        else:
            print(tabulate(rows, headers=headers_disp, tablefmt="grid"))
    except Exception as e:
        print("Error:", e)
    finally:
        if 'conn' in locals():
            conn.close()

if __name__=="__main__":
    main()
