# http://stackoverflow.com/questions/60208/replacements-for-switch-statement-in-python/30012053#30012053
class Switch:
    Inst = None

    def __init__(self, value): self._val = value

    def __enter__(self): return self

    def __exit__(self, type, value, traceback): return False  # Allows traceback to occur

    def __call__(self, cond, *mconds): return self._val in (cond,) + mconds


class _SwitchInstance(Switch):
    def __call__(self, type_, *mtypes):
        return isinstance(self._val, (type_,) + mtypes)


Switch.Inst = _SwitchInstance

# # Example
# from datetime import datetime
# with Switch(datetime.today().weekday()) as case:
#     if case(0):
#         # Basic usage of switch
#         print("I hate mondays so much.")
#         # Note there is no break needed here
#     elif case(1,2):
#         # This switch also supports multiple conditions (in one line)
#         print("When is the weekend going to be here?")
#     elif case(3,4): print("The weekend is near.")
#     else:
#         # Default would occur here
#         print("Let's go have fun!") # Didn't use case for example purposes

import unittest


class SwitchTestCase(unittest.TestCase):
    def test_example(self):
        success = False
        with Switch(0) as case:
            if case(0):
                success = True
            elif case(1, 2):
                self.fail()
            elif case(3, 4):
                self.fail()
            else:
                self.fail()
        self.assertTrue(success)

    def test_type(self):
        class A:
            pass

        success = False
        with Switch.Inst(A()) as case:
            if case(list):
                self.fail()
            elif case(dict, list):
                self.fail()
            elif case(A):
                success = True
            else:
                self.fail()
        self.assertTrue(success)

    def test_types(self):
        class A:
            pass

        success = False
        with Switch.Inst(A()) as case:
            if case(dict, list):
                self.fail()
            elif case(dict, A):
                success = True
            else:
                self.fail()
        self.assertTrue(success)

    def test_subtype(self):
        class A:
            pass

        class B(A):
            pass

        success = False
        with Switch.Inst(B()) as case:
            if case(dict, list):
                self.fail()
            elif case(dict, A):
                success = True
            else:
                self.fail()
        self.assertTrue(success)

    def test_not_subtype(self):
        class A:
            pass

        class B(A):
            pass

        success = False
        with Switch.Inst(A()) as case:
            if case(type(123), list):
                self.fail()
            elif case(dict, B):
                self.fail()
            elif case(object):
                success = True
        self.assertTrue(success)
