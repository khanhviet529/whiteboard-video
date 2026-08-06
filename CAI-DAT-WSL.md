# Cài PostgreSQL và Redis trong WSL để đo

Mười lăm chủ đề mạnh nhất trong [KE-HOACH-90.md](KE-HOACH-90.md) không dựng lại
được bằng sqlite: MVCC, gap lock, autovacuum, planner đổi ý, eviction policy. Tài
liệu này cài hai thứ đó vào WSL2 và mở đường cho script Python **chạy trên
Windows** kết nối vào.

Máy này đã kiểm tại thời điểm viết:

| | |
|---|---|
| WSL | Ubuntu 26.04 LTS, WSL2, đang chạy |
| Người dùng mặc định | `root` |
| Init | systemd là pid 1, nên `systemctl` dùng được |
| Đĩa còn | 952 GB |
| RAM WSL thấy | 15 GB |
| Gói có trong repo | `postgresql` 18, `redis-server` 8.0.5 |

## Vì sao script chạy ở Windows mà database ở WSL

Mọi script trong [repro/](repro/) đang chạy bằng Python trên Windows, và giữ
nguyên như vậy thì `render.py`, `lint.py`, `repro/` dùng chung một trình thông
dịch. Đổi sang chạy trong WSL là phải cài lại toàn bộ phụ thuộc ở đó.

WSL2 có sẵn cầu localhost hai chiều, nên `localhost:5432` trên Windows đi thẳng
vào PostgreSQL trong WSL. Đổi lại mỗi câu truy vấn đi qua một chặng mạng loopback
thật, và điều đó **tốt hơn** cho việc đo: sqlite chạy cùng tiến trình nên độ trễ
đi về bằng không, đó chính là chỗ `n_cong_1_truy_van.py` phải khai độ trễ như một
tham số thay vì đo được.

---

## Bước 1 — Cài gói

Mở WSL rồi chạy. Lệnh này tải khoảng 60 MB.

```bash
wsl
```

```bash
apt-get update
apt-get install -y postgresql postgresql-contrib redis-server
```

`postgresql-contrib` là bắt buộc chứ không phải tuỳ chọn: `pgstattuple` (đo bảng
phình, số 20) và `pg_stat_statements` (đếm câu truy vấn, số 02 và 35) nằm trong
đó.

## Bước 2 — Bật và cho tự khởi động

```bash
systemctl enable --now postgresql
systemctl enable --now redis-server
systemctl is-active postgresql redis-server
```

Hai dòng `active` là được.

> WSL tự tắt sau một lúc không dùng, và cả hai service tắt theo. Mở lại bằng bất
> kỳ lệnh `wsl.exe` nào, ví dụ `wsl.exe -- true`, rồi systemd bật lại chúng.

## Bước 3 — Mở đường cho Windows kết nối

PostgreSQL mặc định chỉ nghe socket Unix và dùng xác thực `peer`, nên từ Windows
không vào được. Ba việc: cho nghe cổng TCP, cho phép đăng nhập bằng mật khẩu, và
tạo một vai trò riêng cho việc đo.

```bash
PGCONF=$(ls -d /etc/postgresql/*/main | head -1)

# nghe moi giao dien. WSL2 nam sau NAT cua Windows nen khong lo ra mang LAN.
sed -i "s/^#\?listen_addresses.*/listen_addresses = '*'/" "$PGCONF/postgresql.conf"

# cho phep dang nhap bang mat khau tu cau localhost cua WSL
grep -q 'BENCH' "$PGCONF/pg_hba.conf" || cat >> "$PGCONF/pg_hba.conf" <<'EOF'

# BENCH - cho script do tren Windows ket noi qua cau localhost cua WSL2
host    all   all   127.0.0.1/32     scram-sha-256
host    all   all   172.16.0.0/12    scram-sha-256
EOF
```

Tạo vai trò và cơ sở dữ liệu. Đặt `SUPERUSER` vì nhiều thí nghiệm cần `ALTER
SYSTEM`, `CHECKPOINT` và tạo extension; đây là máy đo cá nhân sau NAT nên chấp
nhận được.

```bash
su - postgres -c "psql -c \"CREATE ROLE bench LOGIN PASSWORD 'bench' SUPERUSER\""
su - postgres -c "psql -c \"CREATE DATABASE bench OWNER bench\""
```

Bật `pg_stat_statements`, cần khởi động lại vì nó nạp từ lúc server lên:

```bash
su - postgres -c "psql -c \"ALTER SYSTEM SET shared_preload_libraries = 'pg_stat_statements'\""
su - postgres -c "psql -c \"ALTER SYSTEM SET log_lock_waits = on\""
systemctl restart postgresql
su - postgres -c "psql -d bench -c 'CREATE EXTENSION IF NOT EXISTS pg_stat_statements; CREATE EXTENSION IF NOT EXISTS pgstattuple;'"
```

Redis mặc định chỉ nghe `127.0.0.1` và bật `protected-mode`. Cầu localhost của
WSL2 thường đi lọt, nhưng để chắc thì mở hẳn:

```bash
REDISCONF=/etc/redis/redis.conf
sed -i 's/^bind .*/bind 0.0.0.0 -::1/'        "$REDISCONF"
sed -i 's/^protected-mode .*/protected-mode no/' "$REDISCONF"
systemctl restart redis-server
```

Không đặt `maxmemory` ở đây. Thí nghiệm eviction sẽ tự `CONFIG SET` lúc chạy rồi
trả về như cũ, để trạng thái máy không trôi giữa các lần đo.

## Bước 4 — Cài driver ở phía Windows

Chạy trong PowerShell hoặc terminal bình thường, không phải trong WSL:

```powershell
py -m pip install "psycopg[binary]" redis
```

`psycopg[binary]` mang theo thư viện `libpq` biên dịch sẵn nên không cần cài gì
thêm trên Windows.

## Bước 5 — Kiểm tra

```powershell
py repro/_kiem_ket_noi.py
```

Script in ra phiên bản của cả hai, thời gian một vòng đi về, và danh sách
extension đã bật. Chạy được nghĩa là xong.

---

## Khi hỏng

| Triệu chứng | Nguyên nhân | Cách sửa |
|---|---|---|
| `connection refused` cổng 5432 | WSL đã ngủ | `wsl.exe -- true` rồi thử lại |
| `connection refused` mà WSL đang chạy | service chưa lên | `wsl.exe -- systemctl status postgresql` |
| `password authentication failed` | `pg_hba.conf` chưa nạp lại | `wsl.exe -- systemctl reload postgresql` |
| `no pg_hba.conf entry for host` | địa chỉ nguồn ngoài hai dải đã khai | xem địa chỉ thật trong log rồi thêm dòng |
| Redis nối được nhưng `DENIED` | `protected-mode` còn bật | làm lại bước 3 phần Redis |
| Cổng 5432 đã bị chiếm trên Windows | có PostgreSQL cài thẳng trên Windows | gỡ nó, hoặc đổi cổng WSL sang 5433 |

## Ảnh hưởng tới việc đo

Hai điều phải nhớ khi viết script trong `repro/`.

Mỗi câu truy vấn đi qua loopback nên có độ trễ thật, cỡ vài trăm micro giây. Với
những số đếm câu truy vấn thì điều này chỉ tốt lên. Với những số đo thời gian
tuyệt đối thì phải in cả độ trễ nền ra để người đọc trừ đi.

Trạng thái database sống qua nhiều lần chạy. Script phải tự dựng lại bảng của
mình ở đầu mỗi lần chạy (`DROP TABLE IF EXISTS`), không thì lần chạy thứ hai đo
trên dữ liệu của lần thứ nhất và ra số khác. Đây là khác biệt lớn nhất so với
sqlite `:memory:` mà mọi script hiện có đang dùng.
