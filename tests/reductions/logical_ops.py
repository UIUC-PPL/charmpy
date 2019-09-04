from charm4py import charm, Chare, Group, Future, Reducer
import numpy as np


ARRAY_SIZE = 100


class Test(Chare):

    def doallfalse(self, f1, f2, f3, array=False):
        if array:
            data = np.zeros(ARRAY_SIZE, dtype=np.bool)
        else:
            data = False
        self.reduce(f1, data, Reducer.logical_and)
        self.reduce(f2, data, Reducer.logical_or)
        self.reduce(f3, data, Reducer.logical_xor)

    def doalltrue(self, f1, f2, f3, array=False):
        if array:
            data = np.ones(ARRAY_SIZE, dtype=np.bool)
        else:
            data = True
        self.reduce(f1, data, Reducer.logical_and)
        self.reduce(f2, data, Reducer.logical_or)
        self.reduce(f3, data, Reducer.logical_xor)

    def test1(self, f1, f2, f3):
        data = self.thisIndex % 2 == 0
        self.reduce(f1, data, Reducer.logical_and)
        self.reduce(f2, data, Reducer.logical_or)
        self.reduce(f3, data, Reducer.logical_xor)


def main(args):
    g = Group(Test)

    f1, f2, f3 = Future(), Future(), Future()
    g.doallfalse(f1, f2, f3, array=False)
    assert f1.get() == False
    assert f2.get() == False
    assert f3.get() == False

    f1, f2, f3 = Future(), Future(), Future()
    g.doallfalse(f1, f2, f3, array=True)
    np.testing.assert_array_equal(f1.get(), np.zeros(ARRAY_SIZE, dtype=np.bool))
    np.testing.assert_array_equal(f2.get(), np.zeros(ARRAY_SIZE, dtype=np.bool))
    np.testing.assert_array_equal(f3.get(), np.zeros(ARRAY_SIZE, dtype=np.bool))

    f1, f2, f3 = Future(), Future(), Future()
    g.doalltrue(f1, f2, f3, array=False)
    assert f1.get() == True
    assert f2.get() == True
    assert f3.get() == False

    f1, f2, f3 = Future(), Future(), Future()
    g.doalltrue(f1, f2, f3, array=True)
    np.testing.assert_array_equal(f1.get(), np.ones(ARRAY_SIZE, dtype=np.bool))
    np.testing.assert_array_equal(f2.get(), np.ones(ARRAY_SIZE, dtype=np.bool))
    np.testing.assert_array_equal(f3.get(), np.zeros(ARRAY_SIZE, dtype=np.bool))

    f1, f2, f3 = Future(), Future(), Future()
    g.test1(f1, f2, f3)
    assert f1.get() == False
    assert f2.get() == True
    assert f3.get() == False

    exit()


charm.start(main)
