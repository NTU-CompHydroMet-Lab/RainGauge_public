from(
    bucket: "OTT_Parsivel_2",
    host: "http://140.112.12.62:8086",
    org: "NTUCE",
    token: "fP-GBq8Z1wZE7iW8qFBuxVy-ArVP9TqVec0naJ77XLECiwSr82aRXqvo3ylXZqU_2ad2vxWGcMoMbl3PXqAZ7A==")
    |> range(start: -30d)
    |> filter(fn: (r) => r["_measurement"] == "raw_particle")
    |> drop(columns: ["_start", "_stop", "_field", "_measurement"])
    |> sum()
