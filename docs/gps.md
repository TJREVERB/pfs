# GPS DOCS
### Modes of Operation
1. Threaded mode
    * Continously reads, parses, and caches gps data
    * ONLY USED FOR TELEMETRY PURPOSES!
    * GPS reciever is always on
    * Should not be accessed by any other module!
2. Get Single GPS
    * Returns a dictionary of data from a single gps reading
    * call `gps.getsinglegps()` returns [dictionary of gps readings](#reading-dictionary-values)
    * Assumes gps receiver is off, waits for gps to turn on and get signal lock
        * Will not always be instantaneous
 4. [Caching Points](#gps-caching-feature)
    * For every 'n' seconds gps.py calls `gps.get_points(duration)` and stores the result in a deque called cache
    * cache is a deque of size 2(only stores latest 2 readings)
        * Each reading may up to 300 actual packets of location data 
    * accessed by `gps.get_cache()`
### Callable Methods
1. `gps.getsinglegps()` 
    * Turns on gps, waits for signal, starts gps logs, reads/parses data, returns dictionary of values
    * Same use as `get_data()` except `getsinglegps()` will be more recent and accurate
2. `gps.get_data()`
    * Returns the last cached [data object](#reading-dictionary-values)
    * Same use as `getsinglegps()` except data returned by `getData()` may be outdated since it is the last cached packet
3. `gps.get_cache()`
    * Returns the last two readings
    * Deque object
    * two(optimally) lists of dictionaries of points from the latest two readings    

### GPS Caching Feature
* Every 300 seconds gps.py will call `get_points(duration)` and update the cache with up to 300 packets
* The cache is a `deque` object with a size of 2
    * The cache will contain the latest 2 readings of up to 300 packets each   
    #### Usage
    * Refer to the [documentation on deques](https://docs.python.org/2/library/collections.html#collections.deque)
    * Assume `data = gps.get_cache()`
    * MAKE SURE TO CHECK `len(data)` IT MAY NOT ALWAYS BE 2
    * `data[-1]` will return the latest reading
    * `data[0]` will return second-to-latest reading
    * `data[-1]` or `data[0]` will return a list of dictionaries
        * [Reading Dictionaries](#reading-dictionary-values)


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
        * Refer to lines 141-143 in gps.py for more information
    #### Usage with `get_cache()`    
    * Assume `data = gps.get_cache()`
    * `get_cache()` will return a list of size 10 with 10 dictionaries inside. Each dictionary contains values from separate readingx
    * Assume `len(data) = 2` and 'n' is either 0 or -1
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
        * Refer to lines 141-143 in gps.py for more information

### Other Things
* gps.py controls turning off and on the gps receiver
* Try not to access variables directly
* Failsafe
    * Each point is checked for accuracy before being appended to the cache
    * Cache readings may not always have 300 packets due to gps variability
* `get_data()` - last cached data(can be outdated)
* `getsinglegps()` - gets and returns a gps packet from the receiver
* `get_cache()` - deque of last two readings