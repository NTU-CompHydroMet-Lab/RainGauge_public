from(
    bucket: "WS100",
    host: "http://140.112.12.62:8086",
    org: "NTUCE",
    token: "fP-GBq8Z1wZE7iW8qFBuxVy-ArVP9TqVec0naJ77XLECiwSr82aRXqvo3ylXZqU_2ad2vxWGcMoMbl3PXqAZ7A==")
|> range(start: -1d)
|> filter(fn: (r) => r["_measurement"] == "DSD")
|> drop(columns: ["_start", "_stop", "_measurement"])
|> pivot(
    rowKey:["_time"],
    columnKey: ["_field"],
    valueColumn: "_value"
  )
// If there's no particle. Don't send it. This line can significantly reduce the data size.
|> filter(fn: (r) => r["Total Particles"] > 0)
|> map(fn: (r) => ({r with _time: int(v: r._time)/1000000000}))