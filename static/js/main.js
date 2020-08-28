//WebSocket接続
var connection = new WebSocket("ws://localhost:8888/pipe");

// サーバからメッセージを受け取った時の処理
connection.onmessage = function(event) {
    // TODO: 実行可能アクションをサーバから受け取って，実行不可なアクションボタンが押された時，ユーザに通知する仕組みを作る．
    // 加えて，サーバ側でもチェックさせる．
    console.log(event.data);
}

function send_message() {
    // msg の値を取得　(使うときは .value プロパティを使用すること．)
    var msg = document.getElementById("msg");

    //エラーが発生した場合
    connection.onerror = function(error) {
        console.log("エラー");
    };
    connection.send(msg.value);
}

function hit() {
    // hit ボタンが押されたとき，サーバー側に 「hit」 とプリントする．
    // TODO: hit という文字列をサーバに渡すのか，hit に相当する データ(0とか1とか)を送るのか．
    // とりあえず hit という文字列を送ってみる．
    connection.send("hit");
    // もし，ヒットできないばあい，js でユーザにできないと通知する．サーバからの連絡が必要．
}
function stand() {
    connection.send("stand");
}

