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
  in_("71 · sort mặc định so sánh theo CHUỖI",
    `[10, 9, 1, 200, 30].sort()        -> [${[...xs].sort()}]`,
    `.sort((a,b) => a - b)             -> [${[...xs].sort((a, b) => a - b)}]`,
    `"200" < "30"                      -> ${"200" < "30"}`);
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
  const cap = [["[] == ![]", [] == ![]], ["'' == 0", "" == 0],
               ["'0' == 0", "0" == 0], ["'' == '0'", "" == "0"],
               ["null == 0", null == 0], ["null >= 0", null >= 0],
               ["NaN == NaN", NaN == NaN]];
  in_("73 · bảng ép kiểu của ==",
    ...cap.map(([b, v]) => `${b.padEnd(34)} -> ${v}`),
    `--- cùng những phép đó với === ---`,
    ...cap.map(([b]) => {
      const c = b.replace("==", "===").replace(">==", ">=");
      // eslint-disable-next-line no-eval
      return `${c.padEnd(34)} -> ${eval(c)}`;
    }));
}

for (const [ten, dong] of ra) {
  console.log(`\n=== ${ten} ===`);
  for (const d of dong) console.log(`  ${d}`);
}
console.log(`\nnode ${process.version}`);
