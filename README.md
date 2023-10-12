RePrIm (remotis project imperium (remote project control)) is comfortable software for manage files on your PC via telegram bot when you are away from your computer

Create a host file in the folder with the main file of your project, and make changes in main file

```python
#host file

import RePrIm
from myproject import main

if __name__ == '__main__':
    RePrIm.config(main_func=main)
    # use prestart=True if you want the project to start when the host starts
    RePrIm.start_host()
```


```python
#myproject file

from RePrIm import get_io_clients
import sys


def main():
    reprim_input, reprim_output = get_io_clients()
    sys.stdin = reprim_input
    sys.stdout = reprim_output
    sys.stderr = reprim_output
    ...
    # do something important job
```
