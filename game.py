# coding: utf-8
import numpy as np
import random

import readchar

class Player:
    def __init__(self):
        self.bankroll = 1000# 適当、最終的にアカウントと紐づけると面白いかも todo
        self.hand = []
    def key_input(self, hand_num, h_flag=True, d_flag=True, u_flag=True):
        # キーボード入力を受け付ける関数．CLI デバッグ用．
        # キー入力に対してアクションを決定する
        key = ord(readchar.readchar())
        if key == 115:
            # stand / stay
            pass
        elif key == 104 and h_flag:
            # hit
            self.hand[hand_num].append(deck.draw())
            # 一度ヒットした場合．次はヒットかスタンドのみ
            d = {"h_flag": True, "d_flag": False, "u_flag": False}
            self.key_input(hand_num, **d)
        elif key == 100 and d_flag:
            # double
            print("double")
            # ダブルダウンした場合．次はヒットかスタンドのみ
            d = {"h_flag": True, "d_flag": False, "u_flag": False}
            self.key_input(hand_num, **d)
        elif key == 117 and u_flag:
            # surrender
            pass
    def bet(self):
        bet_amount = 100# 適当、最終的に各プレイヤーが自由に入力できるようにする。
        self.bankroll -= bet_amount
        return bet_amount
        

class Dealer:
    def __init__(self):
        self.hand = []
    def action(self):
        pass
        

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
    return score

if __name__ == "__main__":
    # リスト初期化
    players = []# プレイヤーインスタンスのリスト
    players_bet_amount = []# プレイヤーインスタンスに紐づく bet 額のリスト
    # - 各インスタンス生成
    mizuki = Player()# ゲームの参加人数に応じて生成。todo
    # yokosawa = Player()
    players.append(mizuki)
    # players.append(yokosawa)
    dealer = Dealer()
    deck = Deck(3)
    # - プレイヤーにカードを配る ***
    for p in players:
        p.hand.append([deck.draw()])
    for p in players:
        p.hand[0].append(deck.draw())
    # - ディーラーにカードを配る
    dealer.hand.append(deck.draw())
    dealer.hand.append(deck.draw())
    #     - 内一枚は伏せる
    #     - A の場合、インシュランス選択 ***
    if dealer.hand[0] % 100 == 1:
        print("insurance ??")# todo
    #     - ブラックジャックだった場合のみオープンする
    if calc_hand(dealer.hand) == 21:
        print("dealers blackjack!")
    # - プレイヤーのベット金額を決定する ***
    for i in range(len(players)):
        players_bet_amount.append(players[i].bet())
    # - プレイヤーのアクション ***
    for p in players:
        # スプリットできるかどうか決定する
        if p.hand[0][0] % 100 == p.hand[0][1] % 100:
            # ord("y") = 121, ord("n") = 110
            print("split? - y/n")
            split_key = ord(readchar.readchar())
            if split_key == 121:
                p.hand.append([p.hand[0].pop(0)])
        # どのハンド(スプリット時)に対するアクションか決めるのが hand_num
        for hand_num in range(len(p.hand)):
            p.key_input(hand_num)
    # - ディーラーのアクション
    # - 清算
