# Requirements

- Find a function that matches the input command string
- **;** is the delimiter 
- Check if command is coming from a valid source

## Command Structure

;*command_name*;*arg1*,*arg2*;*checksum*;

## Functions

### Public

- `enqueue(cmd: str)`: Adds a command to the queue

### Private

- `dispatch(cmd: str)`: Actually run the associated function 
- `validate(cmd: str)`: Check if command is coming from a valid source