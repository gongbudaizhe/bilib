import signal
def sigint_handler(signum, frame):
    print 'type "stop" to terminate'

signal.signal(signal.SIGINT, sigint_handler)

if __name__=="__main__":
    while True:
        print 'type "stop" to terminate:'
        if raw_input().lower() == "stop":
            print "TERMINATED"
            break