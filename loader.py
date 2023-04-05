import math, sys
import struct, zlib
from PIL import Image
import codecs
import os
from contextlib import redirect_stdout
import re

codepages = {
    "Sfhit-JIS": "shift_jis",
}


class ParseBuffer(object):
    def __init__(self, data):
        self.data = data
        self.i = 0
        self.key = None
        self.codepage = None

    @property
    def end(self):
        return self.i == len(self.data)

    def peek(self, size):
        return self.data[self.i : self.i + size]

    def read(self, size):
        self.i += size
        return self.data[self.i - size : self.i]

    def unpack(self, fmt):
        fmt = "<" + fmt
        ret = struct.unpack(fmt, self.read(struct.calcsize(fmt)))
        if len(ret) == 1:
            return ret[0]
        return ret

    @property
    def byte(self):
        return self.unpack("B")

    def bytes(self, size):
        return map(ord, self.read(size))

    @property
    def bool(self):
        return {0: False, 1: True}[
            self.byte
        ]  # Throws an exception if the byte is non 0/1

    @property
    def int16(self):
        return self.unpack("h")

    @property
    def uint16(self):
        return self.unpack("H")

    @property
    def int32(self):
        return self.unpack("i")

    @property
    def uint32(self):
        return self.unpack("I")

    @property
    def float(self):
        return self.unpack("f")

    @property
    def double(self):
        return self.unpack("d")

    def str(self, size: int = None):
        if size is None:
            return self.read(self.uint32).decode("utf-8")
        else:
            return self.read(size).decode("utf-8")

    @property
    def wstr(self):
        if self.key is not None:
            data = "".join(chr((ord(x) - self.key + 256) % 256) for x in self.str())
        else:
            data = self.str()
        if self.codepage is None or self.codepage not in codepages:
            return data

        return codecs.decode(data, codepages[self.codepage]).encode("utf-8")


def arr(*x):
    return "[%s]" % (", ".join(map(repr, x)))


def parse(data, file_name: str):
    file_name_without_ext: str = file_name.replace(".pdo", "")
    # create image output dir
    if not os.path.exists(file_name_without_ext):
        os.mkdir(file_name_without_ext)
    buf = ParseBuffer(data)
    assert buf.str(10) == "version 3\n"
    with open(f"{file_name_without_ext}/line.yaml", "w") as f:
        with redirect_stdout(f):
            locked = buf.uint32  # 4 == unlocked, 5 == locked
            print("locked:", locked)
            print("unk1:", buf.uint32)
            print("version:", buf.uint32)
            print

            if locked == 5:
                print("software:", re.sub(r"[\W]", " ", buf.wstr))  # Empty for en-us
                buf.key = buf.uint32
                print("key:", buf.key)
                print

            print(
                "locale:", buf.wstr
            )  # Should always be empty for en-us, according to the codepage bug
            buf.codepage = buf.wstr
            print("codepage:", buf.codepage)
            print("unk3:", buf.uint32)
            print("hexstring:", buf.wstr)
            print

            if locked == 5:
                print("unk4:", buf.bool)
                print("unk5:", buf.bool)
                print

            print("unk6:", arr(buf.double, buf.double, buf.double, buf.double))
            print("geometry:")
            for i in range(buf.uint32):
                print("  - name:", buf.wstr)
                print("    unk8:", buf.bool)
                print("    vertices:")
                for j in range(buf.uint32):
                    print("      -", arr(buf.double, buf.double, buf.double))
                print
                print("    shapes:")
                for j in range(buf.uint32):
                    print("      - unk11:", buf.int32)
                    print("        part:", buf.uint32)
                    print(
                        "        unk12:",
                        arr(buf.double, buf.double, buf.double, buf.double),
                    )
                    print("        points:")
                    for k in range(buf.uint32):
                        print("          - index:", buf.uint32)
                        print("            coord:", arr(buf.double, buf.double))
                        print("            unk13:", arr(buf.double, buf.double))
                        print("            unk14:", buf.bool)
                        print(
                            "            unk15:",
                            arr(buf.double, buf.double, buf.double),
                        )
                        print(
                            "            unk16:",
                            arr(
                                buf.uint32,
                                buf.uint32,
                                buf.uint32,
                                buf.float,
                                buf.float,
                                buf.float,
                            ),
                        )  # last three contain RGB values (x / 256)
                    print
                print
                print("    unk17:")
                for j in range(buf.uint32):
                    print(
                        "      -",
                        arr(
                            buf.uint32,
                            buf.uint32,
                            buf.uint32,
                            buf.uint32,
                            buf.bool,
                            buf.bool,
                            buf.uint32,
                        ),
                    )
                print
            print

            print("textures:")
            for i in range(buf.uint32):
                print("  - name:", buf.wstr)
                print("    unk20:", arr(buf.float, buf.float, buf.float, buf.float))
                print("    unk21:", arr(buf.float, buf.float, buf.float, buf.float))
                print("    unk22:", arr(buf.float, buf.float, buf.float, buf.float))
                print("    unk23:", arr(buf.float, buf.float, buf.float, buf.float))
                print("    unk24:", arr(buf.float, buf.float, buf.float, buf.float))
                has_image = buf.bool
                print("    has_image:", has_image)
                if has_image:
                    w, h = buf.uint32, buf.uint32
                    print("    width:", w)
                    print("    height:", h)
                    csize = buf.uint32
                    print("    csize:", csize)
                    cbuf = buf.read(csize)
                    cbuf = zlib.decompress(cbuf)
                    im = Image.frombuffer("RGB", (w, h), cbuf)
                    im.save(f"{file_name_without_ext}/texture-{i}.png")
                    print("    fn: texture-%i.png" % i)
                print
            print

            if buf.bool:
                print("unk26:", buf.double)
                print("unk27:", buf.bool)
                print("unk28:", arr(buf.double, buf.double, buf.double, buf.double))

                print("unk29:")
                for i in range(buf.uint32):
                    print(
                        "  - unk30:",
                        arr(buf.uint32, buf.double, buf.double, buf.double, buf.double),
                    )
                    if locked == 5:
                        print("    unk31:", buf.wstr)
                    print("    unk32:")
                    for j in range(buf.uint32):
                        print("      - unk33:", arr(buf.bool, buf.uint32))
                        if buf.bool:
                            print("        unk34:", arr(buf.uint32, buf.uint32))
                        if buf.bool:
                            print("        unk35:", arr(buf.uint32, buf.uint32))
                    print
                print

                print("text_display:")
                for i in range(buf.uint32):
                    print(
                        "  - unk37:",
                        arr(buf.double, buf.double, buf.double, buf.double, buf.double),
                    )
                    print("    unk38:", arr(buf.uint32, buf.uint32))
                    print("    font:", buf.wstr)
                    print("    lines:")
                    for j in range(buf.uint32):
                        print("      -", buf.wstr)
                    print

                print("unk39:")
                for i in range(buf.uint32):
                    print(
                        "  - unk40:",
                        arr(buf.double, buf.double, buf.double, buf.double),
                    )
                    print("    unk41:", arr(buf.uint32, buf.uint32))
                    cbuf = buf.read(buf.uint32)
                    dbuf = zlib.decompress(cbuf)
                    print("    decompressed_size:", len(dbuf))
                    print
                print

                print("unk42:")
                for i in range(buf.uint32):
                    print(
                        "  - unk43:",
                        arr(buf.double, buf.double, buf.double, buf.double),
                    )
                    print("    unk44:", arr(buf.uint32, buf.uint32))
                    cbuf = buf.read(buf.uint32)
                    dbuf = zlib.decompress(cbuf)
                    print("    decompressed_size:", len(dbuf))
                    print

            print("unk45:", arr(buf.bool, buf.bool, buf.bool, buf.bool, buf.bool))
            print(
                "unk46:",
                arr(
                    buf.uint32, buf.bool, buf.uint32, buf.uint32, buf.uint32, buf.uint32
                ),
            )

            unk = buf.uint32
            if unk == 0x0B:
                print("unk47:", arr(buf.double, buf.double))
            else:
                print("unk48:", unk)
            print

            print("unk49:", arr(buf.uint32, buf.uint32, buf.uint32))
            print(
                "unk50:",
                arr(
                    buf.double,
                    buf.double,
                    buf.double,
                    buf.double,
                    buf.double,
                    buf.double,
                ),
            )
            print(
                "unk51:",
                arr(
                    buf.double,
                    buf.double,
                    buf.double,
                    buf.double,
                    buf.double,
                    buf.double,
                ),
            )

            print("unk52:", arr(buf.bool, buf.double))
            if locked == 5:
                print("unk53:", '"' + buf.wstr + '"')
                print("unk54:", '"' + buf.wstr + '"')

    assert buf.uint32 == 0x270F
    assert buf.end
    f.close()


if __name__ == "__main__":
    data = open(sys.argv[1], "rb").read()
    parse(data, file_name=sys.argv[1])
