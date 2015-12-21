# QuickPin API

Python wrapper for the QuickPin API.

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

Set environment variables to avoid being prompted each time:

1. QUICKPIN_URL
1. QUICKPIN_TOKEN


Example:
```bash
$ export QUICKPIN_URL="https://example.com"
$ export QUICKPIN_TOKEN="1|2015-12-09T16:50:59.057635.Y5pm9qB_naw6FkOekcksiFRyMlY"
```
