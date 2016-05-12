import os, sys
import traceback

my_filepath = os.path.abspath(sys.argv[0])
my_dirpath = os.path.dirname(my_filepath)

for dirpath, dirnames, filenames in os.walk("."):
    for filename in filenames:
        if not filename.endswith(".py"):
            continue
        filepath = os.path.abspath(os.path.join(dirpath, filename))
        if filepath == my_filepath:
            continue
        if not filepath.startswith(my_dirpath):
            raise RuntimeError("%s is unexpectedly outside directory %s" % (filepath, my_dirpath))
        relative_filepath = filepath[1 + len(my_dirpath):]
        print("Running:", relative_filepath)

        with open(filepath) as f:
            try:
                #
                # TODO: for now, just make sure the files have no syntax
                # errors; later we'll try to run them inside a suitable
                # virtual environment
                #
                compile(f.read(), filepath, "exec")
            except Exception as exc:
                #~ print("ERROR!!")
                traceback.print_exc()
