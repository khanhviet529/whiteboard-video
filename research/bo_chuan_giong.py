"""Bo chuan cho GIONG, khong phai cho tung video.

    py research/bo_chuan_giong.py           # sinh file cau, in bang
    py src/thu_cau.py build/bo_chuan.txt --screenplay screenplays/pool-can.yaml \\
        --engine omnivoice                  # sinh audio, mat ~20 phut

Y tuong: nguoi dung khong the nghe 90 video, nhung nghe MOT bo chuan thi duoc.
Bo nay chay lai moi khi doi giong hoac doi cau hinh, nghe mot lan roi duyet.

Hai phan:

  A. Tung ung vien trong `phienam.TU_DIEN_THU`, sinh CA HAI cach doc de doi
     chieu. Nghe xong thay cach phien am ro hon thi chuyen muc do sang TU_DIEN,
     thay khong hon thi xoa han khoi TU_DIEN_THU. Dung de lung lung.

  B. Cac dang cau da tung sinh loi, giu lam moc. Neu mot ngay nao do doi giong
     hoac doi cau hinh lam chung hong tro lai thi biet ngay.
"""
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

import phienam  # noqa: E402

# Cau mang tu can thu. Dat tu o GIUA cau, khong dau khong cuoi: dau cau thi am
# tiet bi nen, cuoi cau thi cao tan sut - hai cho do lam nhieu phep so sanh.
KHUNG = {
    "database": "Mỗi lần gọi thì {} phải mở một kết nối mới cho bạn.",
    "cache": "Xoá {} xong rồi mà giá cũ vẫn còn nằm nguyên ở đó.",
    "request": "Mỗi {} chiếm một kết nối trong suốt thời gian chờ.",
    "timeout": "Không đặt {} thì một dịch vụ treo là cả hệ thống treo theo.",
    "transaction": "Đừng gọi mạng khi đang ở trong một {} chưa đóng.",
    "index": "Bọc hàm quanh cột là {} thành vô dụng ngay lập tức.",
    "query": "Một {} chậm không đáng sợ bằng một trăm câu nhanh.",
    "redis": "Bên {} trả về thành công nhưng dữ liệu thì chưa kịp ghi.",
    "nginx": "Tầng {} chuyển tiếp hết, nó không giữ lại request nào.",
    "worker": "Mỗi {} lấy một việc ra khỏi hàng đợi rồi làm cho xong.",
    "pool": "Cái {} chỉ có mười kết nối dùng chung cho tất cả.",
    "set": "Đổi kho sang {} rồi thì tìm bao nhiêu lần cũng như nhau.",
    "list": "Tìm trong {} thì phải so sánh lần lượt từng phần tử một.",
}

# Cac dang da tung sinh loi. Moi dong kem ly do, xem VIET-KICH-BAN.md.
MOC = [
    # viet tat giua cau, dang duoc phien am tu dong
    "Đặt TTL cho cache rồi thì dữ liệu cũ tự hết hạn sau sáu mươi giây.",
    "Câu API này trả về hai trăm nhưng mất tới bốn giây mới xong.",
    # so dung tran o cuoi menh de -> nhan trong am va keo dai
    "Hàng dâng lên bảy mươi trong khi chỉ có mười chỗ ngồi cho nó.",
    "Hàng dâng lên bảy mươi request trong khi chỉ có mười chỗ ngồi.",
    # cum tu lap ba lan
    "Mỗi đơn thêm một câu, mỗi dòng thêm một câu, mỗi ảnh thêm một câu.",
    # cau dai, nhieu menh de, co dau phay o ranh gioi
    "Khi bạn xoá cache trước rồi mới ghi database, có một khe hở rất hẹp mà "
    "người đọc vào đúng lúc đó sẽ nạp lại đúng giá trị cũ.",
    # con so nhieu chu so
    "Một trang hai mươi đơn hàng sinh ra một trăm bốn mươi chín câu truy vấn.",
    # cau ngan, dat o GIUA nen khong bi contour ha toc
    "Bộ đếm vẫn đứng ở không.",
]

RA = os.path.join(ROOT, "build", "bo_chuan.txt")


def main():
    d = []
    d.append("# Bo chuan giong - sinh boi research/bo_chuan_giong.py")
    d.append("# Phan A: tung ung vien trong phienam.TU_DIEN_THU, hai cach doc.")
    cap = []
    for tu, am in sorted(phienam.TU_DIEN_THU.items()):
        khung = KHUNG.get(tu)
        if not khung:
            continue
        goc, pa = khung.format(tu), khung.format(am)
        cap.append((tu, goc, pa))
        d.append(f"\n# --- {tu}  (goc / phien am)")
        d.append(goc)
        d.append(pa)
    d.append("\n# Phan B: cac dang da tung sinh loi, giu lam moc.")
    for c in MOC:
        d.append(c)
    io.open(RA, "w", encoding="utf-8").write("\n".join(d) + "\n")

    n = len(cap) * 2 + len(MOC)
    print(f"da ghi {RA}  ({n} cau, {len(cap)} cap doi chieu + {len(MOC)} moc)\n")
    print("Nghe theo TUNG CAP. So hieu file trong out/thu:")
    i = 1
    for tu, _, _ in cap:
        print(f"  {i:02d} vs {i + 1:02d}   {tu:12} goc / phien am '{phienam.TU_DIEN_THU[tu]}'")
        i += 2
    print(f"  {i:02d}-{i + len(MOC) - 1:02d}   cac moc dang da tung loi")
    print("\nSinh audio:")
    print("  py src/thu_cau.py build/bo_chuan.txt "
          "--screenplay screenplays/pool-can.yaml --engine omnivoice")
    print("\nNghe xong: cach phien am ro hon thi chuyen muc do tu TU_DIEN_THU")
    print("sang TU_DIEN trong src/phienam.py; khong hon thi xoa khoi TU_DIEN_THU.")


if __name__ == "__main__":
    main()
