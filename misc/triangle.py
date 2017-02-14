class Triangle(tuple):
    """
    |   3-tuple that allows to shift elements and preserve hash, shifted copies are equal to each other.
    |   It's like rotating triangle around normal, but not flipping normal.
    |   Memory overhead: tuple✕3.
    |   E.g.:
    |       Triangle((1, 2, 3)) == Triangle((2, 3, 1)) == Triangle((3, 1, 2))
    |       hash(Triangle((1, 2, 3))) == hash(Triangle((2, 3, 1)))
    |   BUT:
    |       Triangle((1, 2, 3)) != Triangle((1, 3, 2))
    |       hash(Triangle((1, 2, 3))) != hash(Triangle((1, 3, 2)))
    |       hash(instance_of_Triangle) != hash(any_tuple)
    """

    def __init__(self, seq=()):
        super().__init__()
        if len(seq) != 3:
            raise ValueError('Expected 3-tuple')
        t1 = tuple(seq)
        # explicit shifted alternatives for hashing and comparing
        t2 = tuple((t1[2], t1[0], t1[1]))
        t3 = tuple((t1[1], t1[2], t1[0]))
        rotated_alts = [t1, t2, t3]
        # sort to preserve hash
        rotated_alts.sort()
        self._rotated_alts = tuple(rotated_alts)

    def __hash__(self):
        return hash(self._rotated_alts)

    def __eq__(self, other):
        """
        Comparing with shifted alternatives returns true.
        Also it is possible to compare with tuples.
        :param other: Triangle or tuple
        :return:
        """
        if isinstance(other, Triangle):
            return self._rotated_alts == other._rotated_alts
        elif isinstance(other, tuple):
            return other in self._rotated_alts
        else:
            raise ValueError('IDK how to compare ' + str(type(other)))
