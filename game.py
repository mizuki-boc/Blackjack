# coding: utf-8
import numpy as np
import random

import readchar

class Player:
    def __init__(self, name):
        self.name = name
        self.bankroll = 1000# 適当、最終的にアカウントと紐づけると面白いかも todo
        self.original_bet = 0
        # self.bet_amount = 0
        self.bet_amount = []
        self.income = 0
        self.hand = []
        self.is_blackjack = False
        self.bet_insurance = False
        self.bet_surrender = False
    def bet(self):
        self.original_bet = 100# 適当、最終的に各プレイヤーが自由に入力できるようにする。
        # self.bet_amount += self.original_bet
        self.bet_amount.append(self.original_bet)
        print("bet amount =", self.bet_amount)
    def key_input(self, hand_num, h_flag=True, d_flag=True, u_flag=True):
        # キーボード入力を受け付ける関数．CLI デバッグ用．
        # キー入力に対してアクションを決定する
        print("=== ", self.name, "s turn ! ===")
        print(self.hand[hand_num])
        print("Hit = h key")
        print("Stand = s key")
        if d_flag:
            print("Double down = d key")
        if u_flag:
            print("Surrender = u key")
        key = ord(readchar.readchar())
        if key == 115:
            # stand / stay
            pass
        elif key == 104 and h_flag:
            # hit
            self.hand[hand_num].append(deck.draw())
            # burst 確認
            if 0 < calc_hand(self.hand[hand_num]) < 21:
                # 一度ヒットした場合．次はヒットかスタンドのみ
                d = {"h_flag": True, "d_flag": False, "u_flag": False}
                self.key_input(hand_num, **d)
            elif calc_hand(self.hand[hand_num]) == 21:
                return
            elif calc_hand(self.hand[hand_num]) == 0:
                print(p.name, "burst !")
            else:
                print("unexpected error! calc_hand is over [0, 21]")
            
        elif key == 100 and d_flag:
            # double
            print("double down !")
            # self.bet_amount = self.bet_amount * 2
            self.bet_amount[hand_num] = self.bet_amount[hand_num] * 2
            print("bet amount =", self.bet_amount)
            # ダブルダウンした場合．次はヒットかスタンドのみ，それで終了．
            print("Hit = h key")
            print("Stand = s key")
            key = ord(readchar.readchar())
            if key == 104:
                self.hand[hand_num].append(deck.draw())
        elif key == 117 and u_flag:
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

if __name__ == "__main__":
    # リスト初期化
    players = []# プレイヤーインスタンスのリスト
    # - 各インスタンス生成
    mizuki = Player("mizuki")# ゲームの参加人数に応じて生成。todo
    players.append(mizuki)
    yokosawa = Player("yokosawa")
    players.append(yokosawa)
    dealer = Dealer()
    deck = Deck(3)
    # - プレイヤーのベット金額を決定する ***
    for p in players:
        p.bet()
    # - プレイヤーにカードを配る ***
    for p in players:
        p.hand.append([deck.draw()])
    for p in players:
        p.hand[0].append(deck.draw())
    # ブラックジャックかチェック
    for p in players:
        if calc_hand(p.hand[0]) == 21:
            print(p.name, "s blackjack!")
            p.is_blackjack = True
        else:
            p.is_blackjack = False
    # - ディーラーにカードを配る
    dealer.hand.append(deck.draw())
    dealer.hand.append(deck.draw())
    #     - 内一枚は伏せる
    #     - A の場合、インシュランス選択 ***
    if dealer.hand[0] % 100 == 1:
        for p in players:
            p.insurance()
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
                # スプリットできるかどうか決定する
                if p.hand[0][0] % 100 == p.hand[0][1] % 100:
                    # ord("y") = 121, ord("n") = 110
                    print("split? - y/n")
                    split_key = ord(readchar.readchar())
                    if split_key == 121:
                        # yes
                        p.hand.append([p.hand[0].pop(0)])
                        p.bet_amount.append(p.original_bet)
            # どのハンド(スプリット時)に対するアクションか決めるのが hand_num
            for hand_num in range(len(p.hand)):
                p.key_input(hand_num)
        # - ディーラーのアクション
        dealer.action()
    print(dealer.hand)
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
                # スコア勝負
                for hand_num in range(len(p.hand)):
                    if calc_hand(dealer.hand) < calc_hand(p.hand[hand_num]):
                        # ここスプリット時の print出力 をどうするか考える　todo
                        print(p.name, "s win!")
                        p.income += p.bet_amount[hand_num]
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
        p.income = 0