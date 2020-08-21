//WebSocket接続
var connection = new WebSocket("ws://localhost:8888/pipe");

function send_message() {
    var msg = document.getElementById("msg");
    // html のボタンが押された時実行される．
    connection.onopen = function(e) {
        console.log("通信が接続されました．");
    };
    //エラーが発生した場合
    connection.onerror = function(error) {
        console.log("エラー");
    };
    connection.send("from browser.");
    connection.send(msg.value);
}