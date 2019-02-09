# GPS DOCS
### Modes of Operation
1. Threaded mode
    * Continously reads, parses, and caches gps data
    * GPS reciever is always on
    * Data accessed through `gps.get_data()`
2. Get Single GPS
    * Returns a dictionary of data from a single gps reading
    * call `gps.getsinglegps()` returns [dictionary of gps readings](#reading-dictionary-values)
    * Assumes gps receiver is off, waits for gps to turn on and get signal lock
        * Will not always be instantaneous
 3. Get Points
    * Returns a list of [dictionaries](#reading-dictionary-values)
    * Records points for a certain amount of time in seconds(passed as parameter) and returns all packets in dictionary form inside a list
    * call `gps.get_points(duration)` returns list of dictionaries of readings
    * duration is an integer
    * Assumes gps receiver is off, waits for gps to turn on and get signal lock
        * Will not always be instantaneous 
 4. [Caching Points](#gps-caching-feature)
    * For every 'n' seconds gps.py calls `gps.get_points(duration)` and stores the result in a list called cache
    * cache is a list of list of dictionaries 
    * accessed by `gps.get_cache()`
### Callable Methods
1. `gps.getsinglegps()` 
    * Turns on gps, waits for signal, starts gps logs, reads/parses data, returns dictionary of values
    * Same use as `get_data()` except `getsinglegps()` will be more recent and accurate
2. `gps.get_points(period)`
    * Turns on gps, waits for signal, start gps logs, records values for duration `period`, returns list of dictionary of all packets recorded
3. `gps.get_data()`
    * Returns the last cached [data object](#reading-dictionary-values)
    * Same use as `getsinglegps()` except data returned by `getData()` may be outdated since it is the last cached packet
### Reading Dictionary Values
* All data recorded from the gps are stored in dictionaries
    #### Usage
    * Assume `data = gps.get_data()` or `data = gps.getsinglegps()`
    * `data['lat']` returns latitude
    * `data['lon']` returns longitude
    * `data['alt']` returns altitude
    * `data['alt_units'` returns altitude unites
    * `data['lon_dir']` returns longitude direction
    * `data['lat_dir']` returns latitude direction
    * `data['time']` returns time in datetime.time(x,x,x) format
    * `data['x_pos']` returns x position
    * `data['y_pos']` returns y position
    * `data['z_pos']` returns z position
    * `data['x_vel']` returns x velocity
    * `data['y_vel']` returns y velocity
    * `data['z_vel']` returns z velocity
    * **IMPORTANT the velocity and position readings may not always be accurate**
        * if `data['position_status']` is -1 position readings are not accurate
        * if `data['velocity_status']` is -1 velocity readings are not accurate
        * Refer to lines 143-148 in gps.py for more information
    #### Usage with `get_points()`    
    * Assume `data = gps.get_points(10)`
    * `get_points(10)` will return a list of size 10 with 10 dictionaries inside. Each dictionary contains values from separate readingx
    * Assume `n` is an integer between 0-9 inclusive 
    * `data[n]['lat']` returns latitude of nth reading
    * `data[n]['lon']` returns longitude of nth reading
    * `data[n]['alt']` returns altitude of nth reading
    * `data[n]['alt_units'` returns altitude unites of nth reading
    * `data[n]['lon_dir']` returns longitude direction of nth reading
    * `data[n]['lat_dir']` returns latitude direction of nth reading
    * `data[n]['time']` returns time in datetime.time(x,x,x) format of nth reading
    * `data[n]['x_pos']` returns x position of nth reading
    * `data[n]['y_pos']` returns y position of nth reading
    * `data[n]['z_pos']` returns z position of nth reading
    * `data[n]['x_vel']` returns x velocity of nth reading
    * `data[n]['y_vel']` returns y velocity of nth reading
    * `data[n]['z_vel']` returns z velocity of nth reading
    * **IMPORTANT the velocity and position readings may not always be accurate**
        * if `data[n]['position_status']` is -1 position readings are not accurate
        * if `data[n]['velocity_status']` is -1 velocity readings are not accurate
        * Refer to lines 143-148 in gps.py for more information

### GPS Caching Feature
* Every 'n' seconds(not determined) gps.py will call `get_points(duration)` with a predetermined duration(not determined) and update the internal cache
* cache is a list of list of dictionaries containing all previous readings from `get_points()` 
    #### Usage
    * Assume `data = gps.get_cache()`
    * Assume `x` is between 0 to `len(data)` and y is between 0 and `len(data[x])`
    * Same as `getsinglegps()`, `get_data()`, or `get_points(duration)` except:
    * `data[x][y]['lat']` returns latitude of the yth reading of the xth cached data


### Other Things
* gps.py controls turning off and on the gps receiver
* Try not to access variables directly
* `get_data()` - last cached data(can be outdated)
* `getsinglegps()` - gets and returns a gps packet from the receiver
* `get_points(duration)` - returns a list of length duration of recently read gps packets
* `get_cache()` - have fun