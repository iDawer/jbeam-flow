# http://stackoverflow.com/questions/60208/replacements-for-switch-statement-in-python/30012053#30012053
class Switch:
    def __init__(self, value): self._val = value

    def __enter__(self): return self

    def __exit__(self, type, value, traceback): return False  # Allows traceback to occur

    def __call__(self, cond, *mconds): return self._val in (cond,) + mconds

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
