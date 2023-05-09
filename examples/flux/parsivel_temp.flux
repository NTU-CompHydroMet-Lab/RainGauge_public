from(
    bucket: "OTT_Parsivel_2",
    host: "http://140.112.12.62:8086",
    org: "NTUCE",
    token: "fP-GBq8Z1wZE7iW8qFBuxVy-ArVP9TqVec0naJ77XLECiwSr82aRXqvo3ylXZqU_2ad2vxWGcMoMbl3PXqAZ7A==")
    |> range(start: -30d)
    |> filter(fn: (r) => r["_measurement"] == "machine status")
    |> filter(fn: (r) => r["_field"] == "Left sensor head temperature" or r["_field"] == "Right sensor head temperature" or r["_field"] == "Temperature PCB" or r["_field"] == "Temperature in the sensor housing")
    // Temperature change is not that significant, so we use mean() to get the average temperature in 1 hour.
    |> aggregateWindow(every: 1h, fn: mean, createEmpty: false)
    // We don't need those data sent in 4 different table, so we merge them into one table.
    |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")
    |> drop(columns: ["_start", "_stop", "_measurement"])
    //Iterate over all rows and convert _time column from nanoseconds to seconds.
    |> map(fn: (r) => ({r with _time: int(v: r._time)/1000000000}))