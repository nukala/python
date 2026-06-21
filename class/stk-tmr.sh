#/bin/bash 
# Source - https://stackoverflow.com/a/17366561
# Posted by Alex  Granovsky, modified by community. See post 'Timeline' for change history
# Retrieved 2026-06-16, License - CC BY-SA 4.0

#see stack.py for implementation
# 1k iterations, setup 10 times. Echo and opts - RN
opts="--number 1000 --setup 10"
echo -n "stack[0][0].f_code "
python -m timeit ${opts} -s 'import inspect, sys' 'inspect.stack()[0][0].f_code.co_name'

echo -n "stack[0][3] "
python -m timeit ${opts} -s 'import inspect, sys' 'inspect.stack()[0][3]'

echo -n "currentframe.f_code "
python -m timeit ${opts} -s 'import inspect, sys' 'inspect.currentframe().f_code.co_name'

echo -n "sys._getframe(3) "
python -m timeit ${opts} -s 'import inspect, sys' 'sys._getframe(3).f_code.co_name'

