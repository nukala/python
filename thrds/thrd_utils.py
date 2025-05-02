import datetime
import threading 
import time  

#
# Bunch of utilities inspired by code from 
# https://topdeveloperacademy.com/articles/python-multithreading-vs-java-multithreading-important-considerations-for-high-performance-programming
#

def write_log(message):
    print(f"{datetime.datetime.now()} ({threading.current_thread().name}) - {message}")
    
def thread_work(delay):     
    #time.sleep(delay)     
    cpu_intensive_work(delay)
    #write_log(f"Hello after {delay} seconds!")  

def cpu_intensive_work(delay):
    start = datetime.datetime.now()
    log_in_between = False
    i = 0
    mult = 6
    if ( not log_in_between ):
        mult = 20
        #mult *= int(delay)
    write_log(f"entered cpu_intensive_work")
    while True:
        i = i + 1
        if ( log_in_between and (i % 2999999 == 0) ):
            write_log(f"i={i}")
            #time.sleep(1)
        if (i > mult*1000*1000):
            break
    elapsed = datetime.datetime.now() - start
    write_log(f"At the end i={i}, multiple={mult}, elapsed={elapsed.total_seconds()} sec ")
