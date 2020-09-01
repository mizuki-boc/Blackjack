//WebSocket接続
var connection = new WebSocket("ws://localhost:8888/pipe");

// サーバからメッセージを受け取った時の処理
connection.onmessage = function (event) {
    // TODO: 実行可能アクションをサーバから受け取って，実行不可なアクションボタンが押された時，ユーザに通知する仕組みを作る．
    // 加えて，サーバ側でもチェックさせる．
    console.log(event.data);
    json_data = JSON.parse(event.data);

    // プレイヤーの ハンドHTML書き換え
    player_hand_html = document.getElementById("player_hand");
    // player_hand が False の場合、 False の箇所は更新しない
    if (json_data.player_hand != false) {
        // 空に初期化する
        player_hand_html.textContent = '';
        // スプリットハンドのときと通常時とで表示方法を切り替える
        if (json_data.is_split_hand) {
            for (let i = 0; i < json_data.player_hand.length; i++) {
                hand = cardnumToSuit(json_data.player_hand[i]);
                player_hand_html.insertAdjacentHTML("afterbegin", "<div>" + hand + "</div>")
                // player_hand_html.innerHTML = "<div>" + hand + "</div>";
            }
        } else {
            player_hand_html.innerHTML = cardnumToSuit(json_data.player_hand);
        }
    }
    
    // ディーラーの ハンドHTML書き換え
    dealer_hand_html = document.getElementById("dealer_hand");
    // dealer_hand が False の場合、 False の箇所は更新しない
    if (json_data.dealer_hand != false) {
        dealer_hand_html.innerHTML = cardnumToSuit(json_data.dealer_hand);
    }

    // ポップメッセージの更新
    // 初期化
    pop_message_html = document.getElementById("pop_message");
    pop_message_html.textContent = '';
    if (json_data.pop_message) {
        // pop_message に メッセージが代入されているとき
        pop_message_html.innerHTML = json_data.pop_message;
    }

    // 結果の HTML 書き換え TODO: switch
    result = document.getElementById("result");
    if (json_data.is_player_win == 0) {
        // 未
        result.innerHTML = "";
    } else if (json_data.is_player_win == 1) {
        // 勝ち
        result.innerHTML = "you win!!";
    } else if (json_data.is_player_win == 2) {
        // プッシュ
        result.innerHTML = "push";
    } else if (json_data.is_player_win == 3) {
        // 負け
        result.innerHTML = "you lose!";
    } else if (json_data.is_player_win == 4) {
        // サレンダー
        result.innerHTML = "you surrendered!";
    }
}

function exitGame() {
    // TODO: 終了ボタン押したときの警告表示(終了しますか？等)
    // TODO: 押すとサーバー側でエラー出るのでその対処
    connection.close();
}

function nextGame() {
    // TODO: 終了ボタンと同じく警告表示(次のゲームに移行しますか？など)
    connection.send("to_next_game")
}

function action(ele) {
    // TODO: 選択できないアクションがある場合，ユーザにできないと通知する．サーバからの連絡が必要．
    // 押したボタンの id を送信する関数
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