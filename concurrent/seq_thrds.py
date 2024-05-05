import threading 
import thrd_utils

#
# Sequential threads (non-mt) 
#
# https://topdeveloperacademy.com/articles/python-multithreading-vs-java-multithreading-important-considerations-for-high-performance-programming
# 
#
# how do we prove these are not-MT?

if __name__ == '__main__':
    thrd_utils.write_log(f"Main thread started")  
    thread_one = threading.Thread(target=thrd_utils.thread_work, args=(1,)) 
    thread_two = threading.Thread(target=thrd_utils.thread_work, args=(2,))  
    #thread_three = threading.Thread(target=thrd_utils.thread_work, args=(3,))  

    #thread_three.start()
    thread_two.start()
    thread_one.start()

    thread_one.join()
    thread_two.join()
    #thread_three.join()

    thrd_utils.write_log(f"Exiting")
