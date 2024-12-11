from(
    bucket: "Ultrasonic3D",
    host: "http://140.112.12.62:8086",
    org: "NTUCE",
    token: "fP-GBq8Z1wZE7iW8qFBuxVy-ArVP9TqVec0naJ77XLECiwSr82aRXqvo3ylXZqU_2ad2vxWGcMoMbl3PXqAZ7A==")
    |> range(start: {start}, stop: {end})
    |> filter(fn: (r) => r["_measurement"] == "wind_vector")
    |> filter(fn: (r) => r._field == "Wind velocity X" or r._field == "Wind velocity Y" or r._field == "Wind velocity Z")
    |> aggregateWindow(every: {window}, fn: mean, createEmpty: false)
    |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
    |> drop(columns: ["_start", "_stop", "_measurement", "_field"])
    |> map(fn: (r) => ({{r with _time: int(v: r._time)/1000000000}}))