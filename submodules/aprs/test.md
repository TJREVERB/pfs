# Tests

## Send (Flight -> GS)
### Inputs
- Normal-sized string that fits within bounds
- Long string
- Short string
- Empty string
- String of spaces
- String of newline/escape characters

### Output
- Should get message displayed on groundstation terminal
- RAW String should be base64 encoded


## Receive (GS -> Flight)
### Inputs
#### Non-Commands
- Normal-sized string that fits within bounds
- Long string
- Short string
- Empty string
- String of spaces
- String of newline/escape 

#### Commands
- "$" + Actual Command Name
- "$" + Invalid Command Name
- "$" + Non-Command Strings
- "$"

### Outputs
#### Non-Commands
- Echo input back down to GS

#### Commands
- 
