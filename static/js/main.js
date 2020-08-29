//WebSocket接続
var connection = new WebSocket("ws://localhost:8888/pipe");

// サーバからメッセージを受け取った時の処理
connection.onmessage = function (event) {
    // TODO: 実行可能アクションをサーバから受け取って，実行不可なアクションボタンが押された時，ユーザに通知する仕組みを作る．
    // 加えて，サーバ側でもチェックさせる．
    console.log(event.data);
    // json にする
    json_data = JSON.parse(event.data);
    player_hand = document.getElementById("player_hand");
    // TODO: 暫定で cardnumToSuit で文字のマークにしてるが、画像とかにする場合はここを変更する
    player_hand.innerHTML = cardnumToSuit(json_data.player_hand);
}

function gameExit() {
    // TODO: 終了ボタン押したときの警告表示(終了しますか？等)
    // TODO: 押すとサーバー側でエラー出るのでその対処
    connection.close();
}

function action(ele) {
    // TODO: 選択できないアクションがある場合，ユーザにできないと通知する．サーバからの連絡が必要．
    id_value = ele.id;
    connection.send(id_value);
}

function cardnumToSuit(player_hand) {
    // 仮想カード番号のリスト から マークのリストに変換する関数
    suit_list = ["♥", "♦", "♣", "♠"];
    str_player_hand = [];
    for (let i = 0; i < player_hand.length; i++) {
        num = player_hand[i] % 100;
        suit = suit_list[(player_hand[i] - num) / 100 - 1];
        str_player_hand.push(suit + String(num));
    }
    return str_player_hand;
}