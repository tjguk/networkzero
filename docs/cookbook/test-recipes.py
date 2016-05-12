from __future__ import print_function
import os, sys
import subprocess
import time

my_filepath = os.path.abspath(sys.argv[0])
my_dirpath = os.path.dirname(my_filepath)

def process_one_folder(dirpath, filenames):
    #
    # Run all the processes in one folder in parallel as
    # some of them will depend on others (eg a request/response)
    #
    processes = {}
    for filename in sorted(filenames):
        if not filename.endswith(".py"):
            continue        
        filepath = os.path.join(dirpath, filename)
        if filepath == my_filepath:
            continue
        print("About to run", filepath)
        
        processes[filename] = subprocess.Popen([sys.executable, filepath])
    
    t0 = time.time()
    while True:
        results = [(name, p.poll()) for (name, p) in processes.items()]
        if all(r is not None for (name, r) in results):
            break
        time.sleep(0.5)
        if time.time() - t0 > 15:
            print("Recipes taking longer than 30s; timing out...")
            for p in processes.values():
                if p.poll() is None:
                    p.kill()
            break
    print("Results:")
    for name, p in processes.items():
        print("  ", name, "=>", p.poll())

def main():
    #
    # Fire up a beacon and wait for it to start
    #
    beacon = subprocess.Popen([sys.executable, "-m", "networkzero.discovery"])
    time.sleep(2)
    try:
        for dirpath, dirnames, filenames in os.walk(my_dirpath):
            print(dirpath)
            process_one_folder(dirpath, filenames)
            print("\n\n")
    finally:
        beacon.kill()

if __name__ == '__main__':
    main(*sys.argv[1:])
