# coding: utf-8
'''
Pythonブラックジャック
'''
import random
import math
import time
import os
import numpy as np
#import pygame
#from pygame.locals import *
import sys
import readchar
'''
# TODO:
hand_aryを[[~,~],[~,~,~],[~,~,~,~]]みたいな構造にして，
呼び出す時(calc_handとか)はhand_ary[0]を入力する
'''

def main():
    bankroll = 10000#バンクロール
    shuffle_threshold = 10#X回目でシャッフル
    count = 1#シャッフルしてからのゲーム回数保存用
    deck = Deck(3)

    game_running = True
    while game_running:
        #インスタンスの生成 -> デッキの引継ぎ,手札の初期化
        player = BlackJackPlayer(deck, bankroll)
        dealer = BlackJackDealer(deck)
        #print(deck.deck)
        #ベット
        print('Bankroll: ', player.bankroll)
        player.bet_con()
        #カードを２枚配る
        player.hand += [deck.draw(), deck.draw()]
        deck = player.deck
        print('p_hand:', player.hand)
        if calc_hand(player.hand) == 21:
            message = 'BlackJack!'
        else:
            #ディーラーに２枚配る
            dealer.hand += [deck.draw(), deck.draw()]
            deck = dealer.deck
            dealers_open_hand = ['*', dealer.hand[1]]
            print('d_hand:', dealers_open_hand)
            #インシュランス
            if dealer.hand[1] == 1:
                print('Insurance?')
                player.insurance()
            #プレイヤーアクションの選択・実行
            player_score = player.action()
            #print('p_score:',player_score)
            print('d_hand:', dealer.hand)
            if 0 < player_score <= 21:
                #ディーラーアクションの実行
                dealer_score = dealer.action()
                if dealer_score > 21:
                    message = 'You win!'
                else:
                    print('d_score:',dealer_score)
                    #結果
                    if player_score > dealer_score:
                        message = 'You win!'
                    elif player_score < dealer_score:
                        message = 'You lose!'
                    else:
                        message = 'Push!'
            elif player_score > 21:
                message = 'Burst!'
            elif player_score == 0:#スコア0はサレンダー
                message = 'Surrender'
        #清算
        print(message)
        bankroll = player.bankroll + check(message,player.bets)
        #一定回数でシャッフル
        if count == shuffle_threshold:
            print('Shuffle')
            deck.shuffle()
            count = 1
            game_running = False#テスト用
        count += 1
    print('GameOver!_RESULT:',bankroll)
    print('Card_counting:',deck.card_count)

class BlackJackDealer:
    def __init__(self, deck):
        #初期化
        self.hand = []
        #引継ぎ
        self.deck = deck
    def action(self):
        while calc_hand(self.hand) < 17:
            self.hand.append(self.deck.draw())
            print('d_hand:',self.hand)
        return calc_hand(self.hand)

class BlackJackPlayer:
    def __init__(self, deck, bankroll):
        #初期化
        self.hand = []#.append(X)で追加
        self.hand_ary = []
        self.ans = 0#リターンするアンサー
        #引継ぎ
        self.deck = deck
        self.bankroll = bankroll
    def bet_vari(self):
        print('how much you bet?')
        print('1 -> 100 , 2 -> 200')
        key = ord(readchar.readchar())
    def bet_con(self,n = 1):#n倍の掛け金をbet
        #固定で100betする
        self.bets = 100 * n#掛け金
        print('bet_amount = ',self.bets)
    def action(self):
        if calc_hand(self.hand) > 21:
            return calc_hand(self.hand)
        print('[Stand -> S , Hit -> H]')
        key = ord(readchar.readchar())
        #print('key:',key)
        if key == 115:
            self.stand()#Stand
        elif key == 104:
            self.hit()#Hit
        elif key == 100 and len(self.hand) == 2:
            self.double()#Double
        elif key == 112 and len(self.hand) == 2:
            self.split()#sPlit
        elif key == 114 and len(self.hand) == 2:
            return self.surrender()#suRRender
        return calc_hand(self.hand)
    def stand(self):
        return
    def hit(self,one_time = False):
        self.hand.append(self.deck.draw())
        print('p_hand:',self.hand)
        if one_time:
            pass
        else:
            self.action()
    def double(self):
        self.bet_con(2)
        self.hit(True)
    def surrender(self):#r->114
        return 0
    def split(self):#p->112
        self.hand_ary.append(self.hand[1])
        self.hand.remove(self.hand[1])
        self.hand_ary.append(self.hand)
        # TODO: hand_ary[0],hand_ary[1]分の処理記述
    def insurance(self):
        print('yes -> y , no -> n')#y=121,n=110
        key = ord(readchar.readchar())
        if key == 121:#yes
            pass
        elif key == 110:#no
            pass

class Deck:
    def __init__(self,deck_num):
        self.deck_num = deck_num#何デックか
        self.num = [1,2,3,4,5,6,7,8,9,10,11,12,13]
        self.suit = [100,200,300,400] * deck_num
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
        else:
            pass
    for i in range(ace_count):
        if score + 11 > 21:
            score += 1
        else:
            score += 11
    return score

def check(message,bets):
    if message == 'BlackJack!':
        ans =  bets * 6 / 5
    elif message == 'You win!':
        ans =  bets
    elif message == 'You lose!' or message == 'Burst!':
        ans = - bets
    elif message == 'Push!':
        ans =  0
    elif message == 'Surrender':
        ans = - bets / 2
    else:
        print('func_\'check\'_unexpected_error!')
        ans =  0
    return ans


if __name__ == '__main__':
    main()
