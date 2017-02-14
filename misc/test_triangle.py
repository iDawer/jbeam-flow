import unittest
import triangle as tr
import collections

t1 = tr.Triangle((1, 2, 3))
t2 = tr.Triangle((3, 1, 2))
t3 = tr.Triangle((2, 3, 1))


class TestTriangle(unittest.TestCase):
    def test_hashable(self):
        t = tr.Triangle((0, 0, 0))
        self.assertIsInstance(t, collections.Hashable)

    def test_tuple(self):
        self.assertEqual((1, 2, 3), t1)
        t2 = t1 + (3, 4, 5)
        self.assertEqual((1, 2, 3, 3, 4, 5), t2)

    def test_rotate(self):
        self.assertEqual(t1, t2)
        self.assertTrue(t1 == t2)
        self.assertEqual(t2, t3)

    def test_hash(self):
        self.assertEqual(hash(t1), hash(t2))
        self.assertEqual(hash(t2), hash(t3))
        self.assertEqual(hash(t1), hash(t3))

    def test_normal_flip(self):
        f_tri = tr.Triangle((1, 3, 2))
        self.assertNotEqual(t1, f_tri)
        self.assertTrue(t1 != f_tri)

    def test_misc(self):
        t000 = tr.Triangle((0, 0, 0))
        self.assertTrue(t000 == t000)
        self.assertTrue(t000 == (0, 0, 0))
        self.assertNotEqual(hash((0, 0, 0)), hash(t000))
        self.assertEqual(t000 + ('abc',), (0, 0, 0, 'abc'))
        t111 = tr.Triangle((1, 1, 1))
        self.assertTrue(t000 != t111)
        self.assertNotEqual(hash(t000), hash(t111))

    def test_dic_key(self):
        d = {t1: 'tri 1 2 3'}
        self.assertEqual('tri 1 2 3', d[t1])
        self.assertEqual('tri 1 2 3', d[t2])
        self.assertEqual('tri 1 2 3', d[t3])
        d[t3] = 'tri rotated'
        self.assertEqual('tri rotated', d[t1])
        f_tri = tr.Triangle((1, 3, 2))
        d[f_tri] = 'flipped'
        self.assertNotEqual(d[t1], d[f_tri])
        d[(1, 2, 3)] = 'not tri'
        self.assertEqual('not tri', d[(1, 2, 3)])
        self.assertNotEqual(d[t1], d[(1, 2, 3)])

        self.assertIn(t1, d.keys())
        self.assertIn(t2, d)
        self.assertIn(f_tri, d.keys())
        self.assertNotIn(tr.Triangle((12, 34, 56)), d.keys())


class TestFrozenset(unittest.TestCase):
    def test_frozenset(self):
        f1 = frozenset((1, 2, 3))
        f2 = frozenset((3, 1, 2))
        self.assertTrue(f1 == f2)
        self.assertEqual(f1, f2)
        flipped = frozenset((1, 3, 2))
        self.assertTrue(f1 == flipped)

        # def test_sort(self):
        #     t1 = tr.Triangle(('1', '2', '3'))
        #     t2 = tr.Triangle(('3', '1', '2'))
        #     t3 = tr.Triangle(('2', '3', '1'))
        #     res = [t1, t2, t3]
        #     res.sort()
        #     print(res)
        #     res = [t1, t3, t2]
        #     res.sort()
        #     print(res)
        #     res = [t3, t2, t1]
        #     res.sort()
        #     print(res)


if __name__ == '__main__':
    unittest.main()
