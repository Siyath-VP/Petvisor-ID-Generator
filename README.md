# Petvisor-ID-Generator

This solution implements a simple algorithm to generate a user ID which is "globally unique", "time-sortable" which is more relatable for twitter snowflakes and suitable for distributed systems.

##Features
- Globally Unique: IDs consist of a timestamp, node ID(Server No) and a sequence number ensuring uniqueness across machines.
- ID Inlcuded main part which are
- Format : `[TimeStamp 41]` `[Node 10]` `[Sequence 12]`

- 
  ``[TimeStamp (UNIX format)]`` ``[Node ID(Unique for each representing server)]`` ``[Sequence (this represent if in the same timstamp try to genrate another ID with this it can assigned uniqe value withhin the same TimeStamp ID allocated 12bit)]``
- Efficient: Uses simple bitwise operations for low-latency ID generation

The ID consits of the following components
[1-bit unused][41-bit timestamp][10-bit node ID][12-bit sequence number]


In the recent edits, 2 approaches were taken to solve the thread safety issue.

## Lock Based Approach
The 1st approach is the updated approach of the original method with thread lock added to synchronize access to shared state for thread safety. (ThreadingAlgo.py)

## Thread aware approach
In the second approach a new bit allocation was introduced to uniquely identify threads and generate Thread ID (DirectGenerate.py)
-Format : `[TimeStamp 41]` `[Node 7]` `[Thread 6]` `[Sequence 10]`
- 
  ``[TimeStamp (UNIX format)]`` ``[Node ID(Unique for each representing server)]`` ``[Thread ID(Unique for each thread feeding concurrently to the server)]`` ``[Sequence (this represent if in the same timstamp try to genrate another ID with this it can assigned uniqe value withhin the same TimeStamp ID allocated 12bit)]``
