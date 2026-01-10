from rootpy.io import root_open
from rootpy.tree import Tree, TreeModel, FloatCol, IntCol


class TreeModel0(TreeModel):
    x = FloatCol()

# make a tree with one float column, put some crap in it, save the
# tree to a file
with root_open("foo.root", "recreate") as f0:

    t0 = Tree("t0", model=TreeModel0)

    for i in range(10):
        t0.x = 2. * i
        t0.fill()

    t0.write()


# The tree is now written and the file is closed at the end of the with block


# Get it back
# get the old tree back
f0Again = root_open("foo.root", "update")
t0Again = f0Again.t0
t0Again.create_buffer()

# Make a new tree in a new file with the new branch
with root_open("foo_new.root", "recreate") as f1:
    t1 = Tree("t1")

    # Set new tree to use same buffer. This creates the necessary branches and
    # sets their memory addresses to the locations of the old branches for
    # fast copying
    t1.set_buffer(t0Again._buffer, create_branches=True)

    # New int branch called y
    t1.create_branches({'y' : 'I'})

    # fill the copied branches with old stuff, fill new branches with new stuff
    for i, row in enumerate(t0Again):
        t1.y = i
        t1.fill()

    # write new tree (file closed at end of with block)
    t1.write()

# close old file
f0Again.close()
