import sqlite3


def list_all(conn: sqlite3.Connection) -> list[dict]:
    return [dict(r) for r in conn.execute("SELECT * FROM readings ORDER BY id").fetchall()]


def for_account(conn: sqlite3.Connection, account_id: int) -> list[dict]:
    q = "SELECT * FROM readings WHERE account_id=? ORDER BY id"
    return [dict(r) for r in conn.execute(q, (account_id,)).fetchall()]


def insert(
    conn: sqlite3.Connection,
    account_id: int,
    kwh: float,
    peak: int = 0,
    period: str | None = None,
    source: str = "manual",
    share_run_id: int | None = None,
    pct: int | None = None,
    commit: bool = True,
) -> int:
    cur = conn.execute(
        "INSERT INTO readings(account_id, kwh, peak, period, source, share_run_id, pct)"
        " VALUES (?,?,?,?,?,?,?)",
        (account_id, kwh, peak, period, source, share_run_id, pct),
    )
    if commit:
        conn.commit()
    return int(cur.lastrowid)


def insert_share(
    conn: sqlite3.Connection,
    rows: list[dict],
    period: str,
    share_run_id: int,
) -> None:
    # 抄表逐户如实记录方案比例（成员比例之和在方案校验时已保证为 100），
    # 不得在此改写；电量之和由分摊引擎保证等于主表电量。
    for row in rows:
        insert(
            conn,
            account_id=row["account_id"],
            kwh=row["kwh"],
            peak=0,
            period=period,
            source="share",
            share_run_id=share_run_id,
            pct=int(row["pct"]),
            commit=False,
        )
