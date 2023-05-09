from(
    bucket: "WS100",
    host: "http://140.112.12.62:8086",
    org: "NTUCE",
    token: "fP-GBq8Z1wZE7iW8qFBuxVy-ArVP9TqVec0naJ77XLECiwSr82aRXqvo3ylXZqU_2ad2vxWGcMoMbl3PXqAZ7A==")
    |> range(start: -7d)
    |> filter(fn: (r) => r["_measurement"] == "precipitation" and r._field == "Precipitation Intensity")
    //Ignore the intensity with value is equal to 0
    |> filter(fn: (r) => r._value != 0)
    |> drop(columns: ["_start", "_stop", "_measurement", "_field"])
    //Iterate over all rows and convert _time column from nanoseconds to seconds.
    |> map(fn: (r) => ({r with _time: int(v: r._time)/1000000000}))
