= Lamdbdas =

Each folder is small function designed to run as an AWS Lambda.

== Packaging for AWS Lambda ==

This example uses the realtime data fetching lambda, but could be adapted to any of the others.

Lambda requires all the dependencies to be include the uploaded zip file. Run this in the local directory of each lambda:

```
$ cd realtime-fetch
$ pip install -r requirements.txt -t .
```

When packaging as a zip file, the script and dependencies should be at the top level, not inside a folder.
Run this (still in the `realtime-fetch` directory):

```
$ zip -r realtimefetchlamdba.zip *
```


== Configuration ==

Configure the lambda to run `realtime_fetch.main` and set up Cloudwatch to run it once per minute (or whatever the polling frequency should be).
