//WebSocket接続
var connection = new WebSocket("ws://localhost:8888/pipe");

// サーバからメッセージを受け取った時の処理
connection.onmessage = function (event) {
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
    pop_message_html = document.getElementById("pop_message");
    pop_message_html.textContent = '';
    if (json_data.pop_message) {
        // pop_message に メッセージが代入されているとき
        pop_message_html.innerHTML = json_data.pop_message;
    }

    // ボタンのインアクティベート
    document.getElementById("hit").disabled = !json_data.active_button.hit
    document.getElementById("stand").disabled = !json_data.active_button.stand
    document.getElementById("double").disabled = !json_data.active_button.double
    document.getElementById("surrender").disabled = !json_data.active_button.surrender
    document.getElementById("yes").disabled = !json_data.active_button.yes
    document.getElementById("no").disabled = !json_data.active_button.no
    document.getElementById("to_next_game").disabled = !json_data.active_button.to_next_game

    // バンクロールの更新
    if (json_data.player_bankroll != null) {
        document.getElementById("bankroll").innerHTML = json_data.player_bankroll
    }
}

function exitGame() {
    // TODO: 押すとサーバー側でエラー出るのでその対処
    ret = confirm("ゲームを終了します．よろしいですか？");
    if (ret == true){
        connection.close();
        location.href = "/";
    }
}

function action(ele) {
    // 押したボタンの id を送信する関数
    id_value = ele.id;
    dic = {
        "action": id_value,
        "bet_amount": false
    }
    console.log(dic.action)
    if (id_value == "to_next_game") {
        // game_main_container を非表示にする
        document.getElementById("game_main_container").style.display = "none";
        // bet_form を表示する
        document.getElementById("bet_form_container").style.display = "block";
    }
    message = JSON.stringify(dic);
    connection.send(message);
}

function cardnumToSuit(hand) {
    // 仮想カード番号のリスト から マークのリストに変換する関数
    suit_list = ["♥", "♦", "♣", "♠"];
    str_hand = [];
    for (let i = 0; i < hand.length; i++) {
        if (hand[i] == 0) {
            str_hand.push("？？")
        } else {
            num = hand[i] % 100;
            suit = suit_list[(hand[i] - num) / 100 - 1];
            str_hand.push(suit + String(num));
        }
    }
    return str_hand;
}

function test() {
    // これで消えるので，逆(もともと消えてて，ベット完了すると表示される)を実装する
    // また，１ゲーム終了してまたベットするフェーズになると，game_main_container を非表示に初期化する
    // そんで，bet 額をバックに送信する．(ここで送信データの json フォーマット化が必要．)
    document.getElementById("game_main_container").style.display = "none";
}

function select_bet_amount() {
    // セレクトフォームから option の value を取得する
    const bet_name = document.bet_form.bet_name;
    const num = bet_name.selectedIndex;
    const str_bet_amount = bet_name.options[num].value;
    if (str_bet_amount == "none") {
        return
    }
    console.log(str_bet_amount)
    // json送信
    dic = {
        "action": false,
        "bet_amount": str_bet_amount
    }
    connection.send(JSON.stringify(dic))
    // game_main_container を表示する
    document.getElementById("game_main_container").style.display = "block";
    // bet_form を非表示にする
    document.getElementById("bet_form_container").style.display = "none"
}