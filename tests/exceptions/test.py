from charm4py import charm, Chare, Group, Array, threaded


class Test(Chare):

    def __init__(self):
        if isinstance(self.thisIndex, tuple):
            self.idx = self.thisIndex[0]
        else:
            self.idx = self.thisIndex

    def bad(self):
        if self.idx % 2 != 0:
            # this will raise NameError exception
            test[3] = 3
        else:
            return 'good'

    def allbad(self):
        # this will raise NameError exception
        test[3] = 3

    def good(self):
        return self.idx

    @threaded
    def bad_th(self):
        return self.bad()

    @threaded
    def allbad_th(self):
        return self.allbad()

    @threaded
    def good_th(self):
        return self.good()


def main(args):
    assert charm.numPes() % 2 == 0

    NUM_ITER = 20
    npes = charm.numPes()
    g = Group(Test)
    a = Array(Test, npes * 8)

    for proxy, num_chares in ((g, npes), (a, npes * 8)):
        for i in range(2):
            if i == 0:
                methods = {'allbad': 'allbad', 'good': 'good', 'bad': 'bad'}
            else:
                methods = {'allbad': 'allbad_th', 'good': 'good_th', 'bad': 'bad_th'}

            # p2p
            if proxy == g:
                bad_idx = 1
            else:
                bad_idx = (num_chares // 2) + 1
            for _ in range(NUM_ITER):
                try:
                    getattr(proxy[bad_idx], methods['bad'])(ret=1).get()
                    assert False
                except NameError:
                    retval = getattr(proxy[bad_idx], methods['good'])(ret=1).get()
                    assert retval == bad_idx

            # bcast ret=1
            for _ in range(NUM_ITER):
                try:
                    getattr(proxy, methods['allbad'])(ret=1).get()
                    assert False
                except:
                    try:
                        getattr(proxy, methods['bad'])(ret=1).get()
                        assert False
                    except:
                        retval = getattr(proxy, methods['good'])(ret=1).get()
                        assert retval is None

            # bcast ret=2 (returns list of results)
            for _ in range(NUM_ITER):
                retvals = getattr(proxy, methods['bad'])(ret=2).get()
                num_errors = 0
                for retval in retvals:
                    if isinstance(retval, Exception):
                        num_errors += 1
                    else:
                        assert retval == 'good'
                assert num_errors == (num_chares // 2)
    exit()


charm.start(main)
