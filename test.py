import numpy as np

hand1 = [1, 2, 3, 4]
hand2 = [2, 3, 4, 5]

hand = []
hand.append(hand1)
hand.append(hand2)
print(hand)
print(hand[0])

hand[0].remove(1)
print(hand)