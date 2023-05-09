from(
    bucket: "OTT_Parsivel_2",
    host: "http://140.112.12.62:8086",
    org: "NTUCE",
    token: "fP-GBq8Z1wZE7iW8qFBuxVy-ArVP9TqVec0naJ77XLECiwSr82aRXqvo3ylXZqU_2ad2vxWGcMoMbl3PXqAZ7A==")
    |> range(start: -30d)
    |> filter(fn: (r) => r["_measurement"] == "machine status")
    |> filter(fn: (r) => r["_field"] == "Signal amplitude of laser strip")
    // Aggregate data into 1 hour windows.
    |> aggregateWindow(every: 1h, fn: mean, createEmpty: false)
    |> drop(columns: ["_start", "_stop", "_measurement", "_field"])
    //Iterate over all rows and convert _time column from nanoseconds to seconds.
    |> map(fn: (r) => ({r with _time: int(v: r._time)/1000000000}))