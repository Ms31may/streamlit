use actix_web::{get, post, web, App, HttpResponse, HttpServer, Responder};
use serde::{Deserialize, Serialize};
use serde_json::*;
use serde_derive::*;
use firestore::*;
use futures::TryStreamExt;

#[derive(Serialize, Deserialize, Debug)]
struct GpsData {
    #[serde(default)]
    time: i64,
    #[serde(default)]
    lat: f64,
    #[serde(default)]
    lng: f64,
    #[serde(default)]
    alti: i32,
    #[serde(default)]
    speed: i32,
    #[serde(default)]
    ignstatus: i32,
    #[serde(default)]
    heading: i32,
}

#[derive(Serialize, Deserialize, Debug)]
struct CanData {
    #[serde(default)]
    time: i64,
    #[serde(default)]
    speed: i32,
    #[serde(default)]
    rpm: i32,
    #[serde(default)]
    ect: i32,
    parameter4: Option<String>,
    parameter5: Option<String>,
}

#[derive(Serialize, Deserialize, Debug)]
#[serde(tag = "type", content = "data")]
enum DataType {
    Gps { data: GpsData },
    Can { data: CanData },
}

#[derive(Deserialize)]
struct EchoRequest {
    #[serde(flatten)]
    other_fields: serde_json::Value,
}

#[get("/")]
async fn hello() -> impl Responder {
    HttpResponse::Ok().body("Hello world!")
}

#[post("/echo")]
async fn echo(req_body: web::Json<EchoRequest>) -> impl Responder {
    let mut data_list: Vec<DataType> = Vec::new();
    for item in req_body.other_fields["bulkData"].as_array().unwrap() {
        let vehicle_no = item["vehicleNo"].as_str().unwrap().to_string();
        let data_type_str = item["type"].as_str().unwrap();
        if data_type_str == "gps" {
            let gps_data: GpsData = serde_json::from_value(item["data"].clone()).unwrap();
            let output = serde_json::json!({
                "vehicleNo": vehicle_no,
                "time": gps_data.time,
                "lat": gps_data.lat,
                "lng": gps_data.lng,
                "alti": gps_data.alti,
                "speed": gps_data.speed,
                "ignstatus": gps_data.ignstatus,
                "heading": gps_data.heading
            });
            println!("{:?}", output);
            data_list.push(DataType::Gps { data: gps_data });
        } else {
            let can_data: CanData = serde_json::from_value(item["data"].clone()).unwrap();
            data_list.push(DataType::Can { data: can_data });
        }
    }
    let json = serde_json::to_string(&data_list).unwrap();
    HttpResponse::Ok().body(json)
}

async fn manual_hello() -> impl Responder {
    HttpResponse::Ok().body("Hey there!")
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    HttpServer::new(|| {
        App::new()
            .service(hello)
            .service(echo)
            .route("/hey", web::get().to(manual_hello))
    })
    .bind(("127.0.0.1", 8080))?
    .run()
    .await
}