// Cac SU THAT CUA NGON NGU trong JavaScript. Khong phai bo do.
//
//     node bench-js/su-that.mjs
//
// ## Vi sao file nay khac han `repro/bench_*.py`
//
// Nhung file kia DO: ket qua phu thuoc du lieu, cau hinh va tai may, nen chung
// phai lay trung vi nhieu lan va phai co hieu chuan chong do luc may ban. Da
// mat mot bo so vi bo qua chuyen do.
//
// Con o day la nhung thu DAC TA quy dinh. `[10,9,1].sort()` tra ve `[1,10,9]`
// tren moi may, moi phien ban, khong dao dong. Dung bo do co hieu chuan va
// trung vi cho chung la thua.
//
// Nhung VAN chay mot lan, vi hai ly do that:
//   1. Trong mot buoi da BA LAN nho sai code lam gi: `sorted(key=)` nhanh hon
//      chu khong cham hon, `sum([0.1]*10)` ra dung 1.0, noi chuoi chi cham 2
//      lan chu khong binh phuong.
//   2. Dong `nguon:` trong video chi co nghia khi file do ton tai va chay duoc.

const ra = [];
const in_ = (ten, ...dong) => ra.push([ten, dong]);

// ---------------------------------------------------------------- so 71
{
  const xs = [10, 9, 1, 200, 30];
  // Gia tien lam hien truong: day so tron chi cho thay THU TU sai, con gia tien
  // cho thay HAU QUA - "re nhat" tren trang khong phai mon re nhat.
  const gia = [1200000, 990000, 85000, 1000000];
  const reNhat = [...gia].sort()[0];
  in_("71 · sort mặc định so sánh theo CHUỖI",
    `[10, 9, 1, 200, 30].sort()        -> [${[...xs].sort()}]`,
    `.sort((a,b) => a - b)             -> [${[...xs].sort((a, b) => a - b)}]`,
    `"200" < "30"                      -> ${"200" < "30"}`,
    `giá [1200000, 990000, 85000, 1000000].sort()`,
    `  -> [${[...gia].sort()}]`,
    `  "rẻ nhất" hoá ra là ${reNhat.toLocaleString("vi")}đ, rẻ thật là ${Math.min(...gia).toLocaleString("vi")}đ`);
}

// ---------------------------------------------------------------- so 72
{
  const M = Number.MAX_SAFE_INTEGER;
  const id = "9007199254740993";              // id that tu backend, kieu chuoi
  const doi = Number(id);
  in_("72 · số nguyên lớn mất chính xác",
    `Number.MAX_SAFE_INTEGER           -> ${M}`,
    `Number("${id}")   -> ${doi}`,
    `giá trị trả về có đúng id không?  -> ${String(doi) === id}`,
    `9007199254740993 === 9007199254740992 -> ${9007199254740993 === 9007199254740992}`,
    `BigInt("${id}")   -> ${BigInt(id)}`);
}


// ---------------------------------------------------------------- so 73
{
  // Cap gia tri chon de lo DU CAC LOAI ep kieu, khong phai de gay soc: so voi
  // chuoi, so voi rong, so voi boolean, so voi mang, null voi undefined.
  const cap = [[0, "0"], [0, ""], [0, false], [0, []], ["", []],
               [null, undefined], [null, 0], [NaN, NaN], ["1", 1]];
  const ten = (v) => typeof v === "string" ? JSON.stringify(v)
                   : Array.isArray(v) ? "[]" : String(v);
  in_("73 · dấu bằng đôi ép kiểu trước khi so",
    ...cap.map(([x, y]) =>
      `${ten(x).padEnd(10)} ==  ${ten(y).padEnd(10)} -> ${String(x == y).padEnd(5)}`
      + ` | === -> ${x === y}`),
    // Hai truong hop dac biet khong nam trong bang tren.
    `[] == ![]                        -> ${[] == ![]}`,
    `null >= 0                        -> ${null >= 0}   (nhưng null == 0 -> ${null == 0})`,
    // Day moi la cho dat: `==` KHONG co tinh bac cau, nen khong the suy luan
    // bang no. Ba dong duoi day la mot phan chung.
    `phá vỡ tính bắc cầu:`,
    `  0 == ""    -> ${0 == ""}`,
    `  "" == "0"  -> ${"" == "0"}`,
    `  0 == "0"   -> ${0 == "0"}   (nếu bắc cầu thì dòng giữa phải đúng)`);
}


for (const [ten, dong] of ra) {
  console.log(`\n=== ${ten} ===`);
  for (const d of dong) console.log(`  ${d}`);
}
console.log(`\nnode ${process.version}`);
