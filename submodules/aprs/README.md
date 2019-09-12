## Methods To Test
### Send (Flight -> GS)
#### Inputs
* Normal-sized string that fits within bounds
* Long string
* Short string
* Empty string
* String of spaces
* String of newline/escape characters

#### Outputs
* Message should be displayed on the ground terminal
* RAW String should be base64 encoded

### Recieve(GS -> Flight)
#### Inputs
##### Non-Commands
* Normal-sized string that fits within bounds
* Long string
* Short string
* Empty string
* String of spaces
* String of newline/escape characters
##### Commands
* "$" + Actual Command
* "$" + Invalid Command Name
* "$" + Non-Command Strings

#### Outputs
##### Non-Commands
* Echos back to GS

##### Commands
* Should see evidence of executed function
* Echo "execution successful" to GS

**IMPORTANT** Unit testing should not include an intermediary. These tests should directly interface with the submodule file and only output can be viewed on an intermediary. (e.x. Test recieve() by sending from another file, not from the GS Terminal)
