import sys 
import time
if __name__ == "__main__":
    # show the progress
    for progress in range(100):
		i = progress / 5
		# the general syntax for a format place holder is
		#              %[flags][width][.precision]type
		# reference: http://www.python-course.eu/python3_formatted_output.php
		#
		# for example, %-20s
		# flag "-" means that the output is left adjusted
		# width "20" means that the output width is 20
		# precision is optional and we don't have it
		# type "s" means that the input is string
		sys.stdout.write("Processing progress: [%-20s] %d%%  \r" %('='*i+'>',progress))
		sys.stdout.flush()
		time.sleep(1)
