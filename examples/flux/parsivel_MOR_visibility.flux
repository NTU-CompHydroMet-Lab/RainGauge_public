from(
    bucket: "OTT_Parsivel_2",
    host: "http://140.112.12.62:8086",
    org: "NTUCE",
    token: "fP-GBq8Z1wZE7iW8qFBuxVy-ArVP9TqVec0naJ77XLECiwSr82aRXqvo3ylXZqU_2ad2vxWGcMoMbl3PXqAZ7A==")
    |> range(start: -7d)
    |> filter(fn: (r) => r._measurement == "weather_parameters" and r._field == "MOR visibility in precipitation")
    //MOR visibiliyt is 20000 meters when there's no precipitation. Ignore those data for less network traffic.
    |> filter(fn: (r) => r._value != 20000)
    |> drop(columns: ["_start", "_stop", "_measurement", "_field"])
    //Iterate over all rows and convert _time column from nanoseconds to seconds.
    |> map(fn: (r) => ({r with _time: int(v: r._time)/1000000000}))
