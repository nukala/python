import multiprocessing
import time
import thrd_utils


#
# multiprocessing processes
#
# https://topdeveloperacademy.com/articles/python-multithreading-vs-java-multithreading-important-considerations-for-high-performance-programming
# 
# how do we prove these are MT?



if __name__ == '__main__':
    thrd_utils.write_log(f"Main thread started")  
    process_one = multiprocessing.Process(target=thrd_utils.thread_work, args=(5,))
    process_two = multiprocessing.Process(target=thrd_utils.thread_work, args=(3,))

    process_one.start()
    process_two.start()

    process_one.join()
    process_two.join()
    
    thrd_utils.write_log(f"Exiting")
