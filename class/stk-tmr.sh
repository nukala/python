#/bin/bash 
# Source - https://stackoverflow.com/a/17366561
# Posted by Alex  Granovsky, modified by community. See post 'Timeline' for change history
# Retrieved 2026-06-16, License - CC BY-SA 4.0

echo -n "stack[0][0] "
python -m timeit -s 'import inspect, sys' 'inspect.stack()[0][0].f_code.co_name'

echo -n "stack[0][3] "
python -m timeit -s 'import inspect, sys' 'inspect.stack()[0][3]'

echo -n "currentframe "
python -m timeit -s 'import inspect, sys' 'inspect.currentframe().f_code.co_name'

echo -n "sys "
python -m timeit -s 'import inspect, sys' 'sys._getframe().f_code.co_name'

