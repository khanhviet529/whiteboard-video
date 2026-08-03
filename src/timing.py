"""Bo dem nhip dung chung cho moi theme.

Builder xep phan tu tuan tu: moi phan tu bat dau sau phan tu truoc mot khoang
`wait`. Cuoi cung `finish()` chuan hoa HAI CHIEU cho khop nhip loi noi:
dai qua thi co lai, ngan qua thi gian ra. Neu chi co lai (khong gian) thi canh
co giong doc dai se ve xong tu som roi dung im rat lau.
"""


class B:
    # ve xong vao khoang 78% thoi luong canh, phan con lai giu hinh
    FILL = 0.78
    MAX_STRETCH = 3.2

    def __init__(self, dur, pre=0.30):
        self.dur = dur
        self.els = []
        self.cursor = pre

    def add(self, fn, dur=0.55, wait=0.30, at=None):
        t = self.cursor if at is None else at
        self.els.append([t, dur, fn])
        self.cursor = max(self.cursor, t + wait)
        return t

    def finish(self):
        if not self.els:
            return self.els
        end = max(t + d for t, d, _ in self.els)
        if end <= 0:
            return self.els
        room = self.dur - 0.45
        if end > room:
            k = room / end
        else:
            k = max(min(self.dur * self.FILL / end, self.MAX_STRETCH), 1.0)
        for e in self.els:
            e[0] *= k
            e[1] *= max(0.5, min(k, 1.6))
        return self.els
