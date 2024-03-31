# This file is used to set a breakpoint every n frames.
# To use it, import it in the file you want to debug, and call set_breakpoint_every_n_frames()
# The default value is 1, so it will break on every frame.
# To change the value, call update_n_frames(new_value) with the desired value.
# Calling update_n_frames(n) is available from the ipdb prompt!!
# Calling update_n_frames(0) will disable the breakpoint.

import ipdb; 
n_frames = 1  # Setting n_frames as a global variable

# a helper function which increments a counter every time it is called.
# when the counter reaches a certain value, it will return True, otherwise False
def every_n_frames():
    global n_frames
    counter = 0
    def helper():
        nonlocal counter
        counter += 1
        if counter == n_frames:
            counter = 0
            return True
        return False
    return helper

debug_launch = every_n_frames()

def set_breakpoint_every_n_frames():
    if debug_launch():
        # Update using update_n_frames(new_value)
        ipdb.set_trace()

def update_n_frames(new_value):
    """Updates the global n_frames value."""
    global n_frames
    n_frames = new_value
