# coding: utf-8

import json
import datetime
import time

from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler

from flask import Flask, request, render_template

app = Flask(__name__)
# *+*+*+*+*+*+*+*+**+* ここから game.py の内容 *+*+*+*+*+*+*+*+**+*
import numpy as np
import random

import readchar
import json

def calc_hand(hand_array):
    score = 0
    ace_count = 0
    for card in hand_array:
        num = card % 100
        if num in [2,3,4,5,6,7,8,9]:
            score += num
        elif num in [10,11,12,13]:
            score += 10
        elif num in [1]:
            ace_count += 1
    # A の補正計算
    for _ in range(ace_count):
        if score + 11 > 21:
            score += 1
        else:
            score += 11
    if score > 21:
        score = 0
    return score
# *+*+*+*+*+*+*+*+**+* ここまで game.py の内容 *+*+*+*+*+*+*+*+**+*
@app.route("/")
def index():
    return render_template("index.html")

@app.route('/pipe')
def pipe():
    if request.environ.get('wsgi.websocket'):
        ws = request.environ['wsgi.websocket']
        while True:
            # ここに game.py の内容を書く．コマンド入力が欲しいときは message = ws.receive() で入力待ち状態に移行する．
            # print("message 受信前")
            # message = ws.receive()
            # print("message 受信後")
            # print(message)
            # ws.send("test message")
            main(ws)
        ws.close()
    return 200

def main(ws):
    class Player:
        def __init__(self, name):
            self.name = name
            self.bankroll = 1000# 適当、最終的にアカウントと紐づけると面白いかも todo
            self.original_bet = 0
            self.bet_amount = []
            self.income = 0
            self.hand = []
            self.is_blackjack = False
            self.bet_insurance = False
            self.bet_surrender = False

        def bet(self):
            self.original_bet = 100# 適当、最終的に各プレイヤーが自由に入力できるようにする。
            self.bet_amount.append(self.original_bet)
            print("bet amount =", self.bet_amount)

        def key_input(self, hand_num, can_hit_flag=True, can_double_flag=True, can_surrender_flag=True):
            # キーボード入力を受け付ける関数．CLI デバッグ用．
            # キー入力に対してアクションを決定する
            print("=== ", self.name, "s turn ! ===")
            print(self.hand[hand_num])
            print("Hit = h key")
            print("Stand = s key")
            if can_double_flag:
                print("Double down = d key")
            if can_surrender_flag:
                print("Surrender = u key")
            # key = ord(readchar.readchar())
            key = ws.receive()
            if key == "stand":
                # stand / stay
                pass
            elif key == "hit" and can_hit_flag:
                # hit
                self.hand[hand_num].append(deck.draw())
                # burst 確認
                if 0 < calc_hand(self.hand[hand_num]) < 21:
                    # 一度ヒットした場合．次はヒットかスタンドのみ
                    d = {"can_hit_flag": True, "can_double_flag": False, "can_surrender_flag": False}
                    self.key_input(hand_num, **d)
                elif calc_hand(self.hand[hand_num]) == 21:
                    return
                elif calc_hand(self.hand[hand_num]) == 0:
                    print(p.name, "burst !")
            elif key == 100 and can_double_flag:
                # double
                print("double down !")
                self.bet_amount[hand_num] = self.bet_amount[hand_num] * 2
                print("bet amount =", self.bet_amount)
                # ダブルダウンした場合．次はヒットかスタンドのみ，それで終了．
                print("Hit = h key")
                print("Stand = s key")
                key = ord(readchar.readchar())
                if key == 104:
                    self.hand[hand_num].append(deck.draw())
            elif key == 117 and can_surrender_flag:
                # surrender
                self.bet_surrender = True
        def insurance(self):
            # 呼ばれた時に insurance するかしないか選択する．
            # した場合， self.bet_insurance = True
            print("Insurance ? - y/n")
            key = ord(readchar.readchar())
            if key == 121:
                # y
                print("insurance accepted!")
                self.bet_insurance = True
            else:
                # n
                print("insurance rejected!")
                self.bet_insurance = False

    class Dealer:
        def __init__(self):
            self.hand = []
            self.is_blackjack = False
        def action(self):
            while 0 < calc_hand(self.hand) < 17:
                # hit 
                self.hand.append(deck.draw())
            
    class Deck:
        def __init__(self,deck_num):
            self.deck_num = deck_num#何デックか
            self.num = [1,2,3,4,5,6,7,8,9,10,11,12,13]
            # self.num = ["A", "2" ,"3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K"]
            self.suit = [100,200,300,400] * deck_num
            # self.suit = ["H", "D", "C", "S"]
            self.deck = np.zeros(len(self.num) * len(self.suit), dtype = int)
            self.draw_count = 0#ドローカウント
            self.left_card_count = np.full(13,4) * self.deck_num
            self.card_count = 0#カードカウンティング用変数
            #print(self.left_card_count)
            c = 0#カウント用
            for s in range(len(self.suit)):
                for n in range(len(self.num)):
                    self.deck[c] = self.num[n] + self.suit[s]
                    c = c + 1
            self.shuffle()
            #print(self.deck)
        def shuffle(self):
            self.draw_count = 0#ドローカウントの初期化
            random.shuffle(self.deck)
            #print(self.deck)
        def draw(self):
            drawn_card = self.deck[self.draw_count]
            drawn_card_num = drawn_card % 100
            self.left_card_count[drawn_card_num - 1] -= 1
            self.draw_count += 1
            self.card_count += self.card_counting(drawn_card)
            return drawn_card
        def calc_prob(self,obj_num):
            return self.left_card_count[obj_num - 1] / np.sum(self.left_card_count) * 100
        def card_counting(self, card):
            num = card % 100
            if num in [10,11,12,13,1]:
                return -1
            elif num in [7,8,9]:
                return 0
            elif num in [2,3,4,5,6]:
                return +1

    def calc_hand(hand_array):
        score = 0
        ace_count = 0
        for card in hand_array:
            num = card % 100
            if num in [2,3,4,5,6,7,8,9]:
                score += num
            elif num in [10,11,12,13]:
                score += 10
            elif num in [1]:
                ace_count += 1
        # A の補正計算
        for i in range(ace_count):
            if score + 11 > 21:
                score += 1
            else:
                score += 11
        if score > 21:
            score = 0
        return score
    
    def add_card_to_hand(ws, player_hand, dealer_hand, player_add_card=False, dealer_add_card=False):
        '''
        ハンドにカードを追加し、追加したタイミングでフロントに json を投げる関数
        カードを追加せずに json を投げる場合は add_card には False を代入する
        '''
        # TODO: カード二枚追加する場合に対応できない？
        # カード追加処理。追加しないときはスルーされる
        if player_add_card:
            player_hand.append(player_add_card)
        if dealer_add_card:
            dealer_hand.append(dealer_add_card)
        # player hand を int にキャスト
        int_player_hand = []
        for c in player_hand:
            int_player_hand.append(int(c))
        # dealer hand を int にキャスト
        int_dealer_hand = []
        for c in dealer_hand:
            int_dealer_hand.append(int(c))
        # json 投げる
        ws.send(json.dumps(
            {
                "player_hand": int_player_hand,
                "dealer_hand": int_dealer_hand,
            }
            ))

    print("------------------------ GAME START ------------------------")
    # リスト初期化
    players = []# プレイヤーインスタンスのリスト
    # - 各インスタンス生成
    mizuki = Player("mizuki")# ゲームの参加人数に応じて生成。todo
    players.append(mizuki)
    # yokosawa = Player("yokosawa")
    # players.append(yokosawa)
    dealer = Dealer()
    deck = Deck(3)
    # - プレイヤーのベット金額を決定する ***
    for p in players:
        p.bet()
    # - プレイヤーにカードを配る ***
    for p in players:
        p.hand.append([deck.draw()])
    for p in players:
        # 二回目にカードを追加するタイミングで json 投げる
        add_card_to_hand(ws=ws, player_hand=p.hand[0], dealer_hand=[], player_add_card=deck.draw())
    # ブラックジャックかチェック
    for p in players:
        if calc_hand(p.hand[0]) == 21:
            p.is_blackjack = True
        else:
            p.is_blackjack = False
    # - ディーラーにカードを配る
    dealer.hand.append(deck.draw())
    dealer.hand.append(deck.draw())
    # add_card_to_hand(ws, dealer.hand, deck.draw())
    #     - 内一枚は伏せる
    #     - A の場合、インシュランス選択 ***
    if dealer.hand[0] % 100 == 1:
        for p in players:
            p.insurance()
    # 勝敗決定処理
    if calc_hand(dealer.hand) == 21:
        # ディーラーがブラックジャックだった場合．
        dealer.is_blackjack = True
    else:
        # - ディーラーがブラックジャックでなかった場合．
        dealer.is_blackjack = False
        # - プレイヤーのアクション ***
        for p in players:
            # プレイヤーが natural 21 でないときのみアクション
            if not p.is_blackjack:
                # スプリットできるとき
                if p.hand[0][0] % 100 == p.hand[0][1] % 100:
                    # ord("y") = 121, ord("n") = 110
                    print("split? - y/n")
                    split_key = ord(readchar.readchar())
                    if split_key == 121:
                        # yes 時の処理
                        p.hand.append([p.hand[0].pop(0)])
                        p.bet_amount.append(p.original_bet)
                # どのハンド(スプリット時)に対するアクションか決めるのが hand_num
                if len(p.hand) > 1:
                    # スプリットしてる場合、action は一回まで。
                    # 二枚目は強制的(?)にヒット
                    for hand_num in range(len(p.hand)):
                        p.hand[hand_num].append(deck.draw())
                    print(p.hand)
                    # 三枚目は hit or stand のみ選択可能
                    for hand_num in range(len(p.hand)):
                        key = ws.receive()
                        if key == "hit":
                            p.hand[hand_num].append(deck.draw())
                        elif key == "stand":
                            pass
                        print(p.hand[hand_num])
                else:
                    for hand_num in range(len(p.hand)):
                        d = {"can_hit_flag": True, "can_double_flag": True, "can_surrender_flag": True}
                        p.key_input(hand_num)
        # - ディーラーのアクション
        dealer.action()
    # アクション終了後の手札表示処理
    print("dealer hand", dealer.hand)
    for p in players:
        print(p.name, p.hand)
    # - 勝敗，インシュランス，サレンダー，ブラックジャック の判断
    if dealer.is_blackjack:
        # ディーラーが　BJ だった場合．
        # この場合，split に入らないので，必ず bet_amount[0]
        for p in players:
            if p.is_blackjack:
                # Push
                print("Push!")
            else:
                # プレイヤーの負け
                print("dealers blackjack!")
                p.income -= p.bet_amount[0]
            # insurance 処理
            if p.bet_insurance:
                # insurance が適応される場合
                p.income += p.original_bet
    else:
        # ディーラーが　BJ でない場合．
        for p in players:
            if p.is_blackjack:
                # プレイヤーのBJ！
                # split には入らない．
                print(p.name, "s blackjack!")
                p.income += p.original_bet * 1.5
            else:
                # バーストしてないか確認
                # どっちかがバーストしてるとき
                for hand_num in range(len(p.hand)):
                    if calc_hand(dealer.hand) == 0 or calc_hand(p.hand[hand_num]) == 0:
                        if calc_hand(dealer.hand) != 0 and calc_hand(p.hand[hand_num]) == 0:
                            # プレイヤーのみバースト
                            print(p.name, "lose!")
                            p.income -= p.bet_amount[hand_num]
                        elif calc_hand(dealer.hand) == 0 and calc_hand(p.hand[hand_num]) != 0:
                            # ディーラーのみバースト
                            print(p.name, "s win!")
                            p.income += p.bet_amount[hand_num]
                        elif calc_hand(dealer.hand) == 0 and calc_hand(p.hand[hand_num]) == 0:
                            # 両方バースト
                            print(p.name, "lose!")
                            p.income -= p.bet_amount[hand_num]
                    else:
                        # スコア勝負
                        for hand_num in range(len(p.hand)):
                            if calc_hand(dealer.hand) < calc_hand(p.hand[hand_num]):
                                # ここスプリット時の print出力 をどうするか考える　todo
                                print(p.name, "s win!")
                                p.income += p.bet_amount[hand_num]
                            elif calc_hand(dealer.hand) == calc_hand(p.hand[hand_num]):
                                # 引き分け時
                                print("push")
                                p.income += 0
                            else:
                                print(p.name, "lose!")
                                p.income -= p.bet_amount[hand_num]
            if p.bet_insurance:
                # insurance 失敗
                p.income -= p.original_bet
    # - 清算
    for p in players:
        print(p.name, "s income", p.income)
        p.bankroll += p.income
        print(p.name, "s bankroll", p.bankroll)
        # 初期化
        p.income = 0

if __name__ == "__main__":
    app.debug = True
    host = 'localhost'
    port = 8888

    host_port = (host, port)
    server = WSGIServer(
        host_port,
        app,
        handler_class=WebSocketHandler
    )
    server.serve_forever()