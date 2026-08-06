"""Kiem tra Windows co noi duoc vao PostgreSQL va Redis trong WSL khong.

Chay:  py repro/_kiem_ket_noi.py

Chay duoc script nay nghia la CAI-DAT-WSL.md da lam xong. Moi script do khac
trong repo nay deu gia dinh dung ket noi ghi o day.

Khong bao gio in ra "khong sao" khi co van de: moi loi deu kem dung mot cau lam
gi tiep theo. Cai gia cua mot thong bao mo ho o day la ca buoi mo mo.
"""
import subprocess
import sys
import time

PG = dict(host="127.0.0.1", port=5432, dbname="bench",
          user="bench", password="bench")
REDIS = dict(host="127.0.0.1", port=6379)
VONG = 200        # so lan di ve de do do tre nen


def loi(gi, lam_gi):
    print(f"\n  HONG: {gi}")
    print(f"  LAM:  {lam_gi}")
    return False


def wsl_song():
    try:
        r = subprocess.run(["wsl.exe", "--", "true"], capture_output=True,
                           timeout=60)
        return r.returncode == 0
    except Exception:
        return False


def do_tre(goi, n=VONG):
    """Do do tre mot vong di ve. In ra de nguoi doc con TRU DI khi can.

    Bat buoc phai co: sqlite chay cung tien trinh nen do tre bang khong, con
    PostgreSQL trong WSL thi moi cau deu qua loopback. So do thoi gian tuyet doi
    ma khong bao do tre nen la so khong doc duoc.
    """
    t0 = time.perf_counter()
    for _ in range(n):
        goi()
    return (time.perf_counter() - t0) / n * 1000


def kiem_postgres():
    print("PostgreSQL")
    try:
        import psycopg
    except ImportError:
        return loi("chua co thu vien psycopg",
                   'py -m pip install "psycopg[binary]"')
    try:
        cx = psycopg.connect(**PG, connect_timeout=5)
    except Exception as e:
        m = str(e).lower()
        if "refused" in m or "timeout" in m:
            return loi(f"khong noi duoc toi {PG['host']}:{PG['port']}",
                       "wsl.exe -- systemctl status postgresql   "
                       "(WSL ngu thi chay `wsl.exe -- true` truoc)")
        if "password" in m:
            return loi("sai mat khau hoac pg_hba chua cho phep",
                       "wsl.exe -- systemctl reload postgresql, "
                       "roi xem lai Buoc 3 trong CAI-DAT-WSL.md")
        if "pg_hba" in m:
            return loi("dia chi nguon khong nam trong dai da khai o pg_hba.conf",
                       "them dong `host all all <dia-chi>/32 scram-sha-256` "
                       "vao pg_hba.conf")
        return loi(str(e).strip()[:160], "xem bang 'Khi hong' trong CAI-DAT-WSL.md")

    with cx:
        cur = cx.cursor()
        cur.execute("SELECT version()")
        print("  ", cur.fetchone()[0].split(" on ")[0])
        ms = do_tre(lambda: cur.execute("SELECT 1"))
        print(f"   do tre mot vong di ve: {ms:.3f} ms  ({VONG} lan)")

        cur.execute("SELECT extname FROM pg_extension ORDER BY extname")
        co = [r[0] for r in cur.fetchall()]
        print("   extension:", ", ".join(co))
        for can in ("pg_stat_statements", "pgstattuple"):
            if can not in co:
                print(f"   THIEU {can} -> wsl.exe -- su - postgres -c "
                      f"\"psql -d bench -c 'CREATE EXTENSION {can}'\"")

        # Quyen ghi: moi script do deu tu dung lai bang cua no o dau moi lan
        # chay, nen khong co quyen nay la hong ngay tu script dau tien.
        cur.execute("DROP TABLE IF EXISTS _kiem_ghi")
        cur.execute("CREATE TABLE _kiem_ghi (id int)")
        cur.execute("DROP TABLE _kiem_ghi")
        print("   tao va xoa bang: duoc")
    return True


def kiem_redis():
    print("\nRedis")
    try:
        import redis as rds
    except ImportError:
        return loi("chua co thu vien redis", "py -m pip install redis")
    try:
        r = rds.Redis(**REDIS, socket_connect_timeout=5)
        info = r.info("server")
    except Exception as e:
        m = str(e).lower()
        if "refused" in m or "timeout" in m:
            return loi(f"khong noi duoc toi {REDIS['host']}:{REDIS['port']}",
                       "wsl.exe -- systemctl status redis-server")
        if "denied" in m or "protected" in m:
            return loi("protected-mode con bat",
                       "lam lai phan Redis o Buoc 3 trong CAI-DAT-WSL.md")
        return loi(str(e).strip()[:160], "xem bang 'Khi hong' trong CAI-DAT-WSL.md")

    print(f"   Redis {info['redis_version']}")
    ms = do_tre(lambda: r.ping())
    print(f"   do tre mot vong di ve: {ms:.3f} ms  ({VONG} lan)")

    # Thi nghiem eviction se doi maxmemory luc chay roi tra ve nhu cu. Kiem o
    # day de chac la doi duoc, chu khong phai luc dang do dang.
    cu = r.config_get("maxmemory").get("maxmemory", "0")
    r.config_set("maxmemory", "16mb")
    r.config_set("maxmemory", cu)
    print(f"   doi duoc maxmemory luc chay: duoc  (dang la {cu})")
    return True


def main():
    print(f"WSL: {'dang chay' if wsl_song() else 'KHONG len duoc'}\n")
    ok = kiem_postgres()
    ok = kiem_redis() and ok
    print()
    if ok:
        print("Ca hai san sang. Xem KE-HOACH-90.md de biet so nao dung cai nao.")
    else:
        print("Con viec phai lam o tren. CAI-DAT-WSL.md co bang 'Khi hong'.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
