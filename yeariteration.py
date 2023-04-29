import subprocess
import sys

script_name = 'TripGen3.py'
n_iter = 7

output_file = 'output_tripgen_' + str(n_iter)
f = open(output_file, 'w')
for i in range(n_iter):
    a = str(subprocess.check_output(['python', script_name]))
    a = a.strip("b'")
    f.write(a)
f.close()
print("Done")



