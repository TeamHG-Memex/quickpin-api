# quickpin-api
Python wrapper for the QuickPin API

Includes a simple command line client.

## Example:
```
$ python qpi.py submit_names usernames.csv twitter --interval=5
``` 
This will parse the usernames contained (1 per line) in the usernames.csv file and submit them 1 by one at an interval of 5 seconds.

For more information:
```
$ python qpi.py --help
$ python qpi.py submit_names --help
$ python qpi.py submit_ids --help
```

Set the  environment variables to avoid being prompted each time:

1. QUICKPIN_USER
2. QUICKPIN_PASSWORD
3. QUICKPIN_URL


## Example:
```
$ export QUICKPIN_USER=guest
$ export QUICKPIN_PASSWORD=password
$ export QUICKPIN_URL=https://example.com
```
