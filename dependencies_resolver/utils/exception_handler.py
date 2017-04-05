from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import traceback

import sys


def handle_exception(msg=''):
    """This function is the project's exception handler.
    There is currently no logic, but could be easily added in the future.

    :param msg: The message to print to the user. 
    :return: Nothing, actually exits the program.
    """
    print(msg)
    traceback.print_exc()
    sys.exit(1)
