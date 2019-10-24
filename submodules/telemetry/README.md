# Telemetry Module
A module that handles data input and output.


Data Structures
------------------------
- `general_queue` (type: [Queue](https://docs.python.org/3/library/queue.html))
- `log_stack` (type: [Stack](https://docs.python.org/3/tutorial/datastructures.html#using-lists-as-stacks))
- `err_stack` (type: [Stack](https://docs.python.org/3/tutorial/datastructures.html#using-lists-as-stacks))

Methods (excluding helpers)
---------------
 - `enqueue(message: str)`
   - PUSH message onto general_queue
 - `dump()`
   - Convert log_stack and err_stack into strings
   - Encode generated string with base64
   - Add prefixes and postfixes
   - Send final string through radio_output.send()

Threads
-------------
- `decide()`
   - WHILE True:
   - if len(general_queue) > 0
     - POP message from general_queue
     - if message == CMD
       - command_ingest.enqueue(message)
     - if message == LOG
       - PUSH message onto log_stack
     - if message == ERR
       - PUSH message onto err_stack   - POP message from general_queue
     - if message == CMD
       - command_ingest.enqueue(message)
     - if message == LOG
       - PUSH message onto log_stack
     - if message == ERR
       - PUSH message onto err_stack