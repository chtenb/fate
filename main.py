import sys
import text

with text.Text(sys.argv[1]) as t:
    while 1:
        print str(t)
        command = raw_input(":")
        try:
            exec(command)
        except Exception as e:
            print(e)
