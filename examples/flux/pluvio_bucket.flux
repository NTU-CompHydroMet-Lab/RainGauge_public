pluvioL = from(
    bucket: "Pluvio2_L_400",
    host: "http://140.112.12.62:8086",
    org: "NTUCE",
    token: "fP-GBq8Z1wZE7iW8qFBuxVy-ArVP9TqVec0naJ77XLECiwSr82aRXqvo3ylXZqU_2ad2vxWGcMoMbl3PXqAZ7A==")
  |> range(start: -7d)
  |> filter(fn: (r) => r["_measurement"] == "bucket")
  |> filter(fn: (r) => r["_field"] == "Bueket NRT")
  |> drop(columns: ["_start", "_stop", "_measurement"])

pluvioS = from(
    bucket: "Pluvio2_S",
    host: "http://140.112.12.62:8086",
    org: "NTUCE",
    token: "fP-GBq8Z1wZE7iW8qFBuxVy-ArVP9TqVec0naJ77XLECiwSr82aRXqvo3ylXZqU_2ad2vxWGcMoMbl3PXqAZ7A==")
  |> range(start: -7d)
  |> filter(fn: (r) => r["_measurement"] == "bucket")
  |> filter(fn: (r) => r["_field"] == "Bueket NRT")
  |> drop(columns: ["_start", "_stop", "_measurement"])

join(tables: {pluvioL: pluvioL, pluvioS: pluvioS}, on: ["_time", "_field"])
|> drop(columns: ["_field"])
|> map(fn: (r) => ({r with _time: int(v: r._time)/1000000000}))