from array import array
import math


class Vector2d:
    type_code = "d"

    def __init__(self, x, y):
        self.__x = float(x)
        self.__y = float(y)

    @property
    def x(self):
        return self.__x

    @property
    def y(self):
        return self.__y

    def __iter__(self):
        return (i for i in (self.x, self.y))

    def __repr__(self):
        class_name = type(self).__name__
        return "{}({!r},{!r})".format(class_name, *self)

    def __str__(self):
        return str(tuple(self))

    def __bytes__(self):
        return bytes([ord(self.type_code)]) + bytes(array(self.type_code, self))

    def __eq__(self, other):
        return tuple(self) == tuple(other)

    def __abs__(self):
        return math.hypot(self.x, self.y)

    def __bool__(self):
        return bool(abs(self))

    @classmethod
    def frombytes(cls, octets):
        type_code = chr(octets[0])
        memv = memoryview(octets[1:]).cast(type_code)
        return cls(*memv)

    def angle(self):
        # 角度
        return math.atan2(self.y, self.x)

    def __format__(self, format_spec=""):
        # 如果以p结尾，那么在极坐标中显示向量
        if format_spec.endswith("p"):
            format_spec = format_spec[:-1]
            coords = (abs(self), self.angle())
            outer_fmt = "<{}, {}>"
        else:
            coords = self
            outer_fmt = "({}, {})"
        components = (format(c, format_spec) for c in coords)
        return outer_fmt.format(*components)

    def __hash__(self):
        return hash(self.x) ^ hash(self.y)


v1 = Vector2d(3, 4)
print(v1)
print(repr(v1))
x, y = v1
print(x)
print(y)
v1_clone = eval(repr(v1))
print(v1 == v1_clone)
octets = bytes(v1)
print(octets)
print(abs(v1))
print(bool(v1))
print(bool(Vector2d(0, 0)))
print(format(v1))
print(format(v1, ".2f"))
print(format(v1, "p"))
print(format(v1, ".3ep"))
print(hash(v1))
print(set([v1]))
