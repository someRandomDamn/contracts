Docker container with dependencies for interactive use:
> docker build -f Dockerfile -t gastest .
> docker run -it --rm -v $(pwd):/usr/src/neo3 gastest /bin/bash

## Tests
> python3 -m unittest discover tests

