import py
from pypy.conftest import gettestobjspace

class AppTestRandom:
    def setup_class(cls):
        cls.space = gettestobjspace(usemodules=['_random'])

    def test_dict(self):
        import _random
        _random.__dict__  # crashes if entries in __init__.py can't be resolved

    def test_random(self):
        import _random
        # XXX quite a bad test
        rnd = _random.Random(1)
        lst1 = [rnd.random() for i in range(100)]
        rnd.seed(1)
        lst2 = [rnd.random() for i in range(100)]
        assert lst1 == lst2
        smaller = 0
        for elt in lst1:
            assert 0 <= elt <= 1
            if elt < 0.5:
                smaller += 1
        # quite unlikely to fail, but well
        assert smaller > 10

    def test_getstate_setstate(self):
        import _random
        rnd1 = _random.Random()
        rnd1.random()
        rnd2 = _random.Random()
        assert rnd1.getstate() != rnd2.getstate()
        state = rnd2.getstate()
        rnd1.setstate(state)
        assert [rnd1.random() for i in range(100)] == [
                    rnd2.random() for i in range(100)]

    def test_seed(self):
        import _random
        rnd = _random.Random()
        rnd.seed()
        different_nums = []
        for obj in ["spam and eggs", 3.14, 1+2j, 'a', tuple('abc')]:
            nums = []
            for o in [obj, hash(obj), -hash(obj)]:
                rnd.seed(o)
                nums.append([rnd.random() for i in range(100)])
            n1 = nums[0]
            different_nums.append(n1)
            for n2 in nums[1:]:
                assert n1 == n2
        n1 = different_nums[0]
        for n2 in different_nums[1:]:
            assert n1 != n2

    def test_seedargs(self):
        import _random
        rnd = _random.Random()
        for arg in [None, 0, 0L, 1, 1L, -1, -1L, 10**20, -(10**20),
                    3.14, 1+2j, 'a', tuple('abc'), 0xffffffffffL]:
            rnd.seed(arg)
        for arg in [range(3), dict(one=1)]:
            raises(TypeError, rnd.seed, arg)
        raises(TypeError, rnd.seed, 1, 2)
        raises(TypeError, type(rnd), [])

    def test_randbits(self):
        import math
        import _random
        rnd = _random.Random()
        for n in range(10, 200, 10):
            n = rnd.getrandbits(n)
            assert int(math.log(n) / math.log(2)) <= n
