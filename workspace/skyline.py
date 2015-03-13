# [SortedDict](http://www.grantjenks.com/docs/sortedcontainers/sorteddict.html)
from sortedcontainers import SortedDict # pip3 install sortedcontainers
from collections import deque
import heapq

def skyline(buildings_by_L): # a deque.
    buildings_by_H = SortedDict() # a self-balancing binary tree.
    buildings_by_R = [] # a priority queue.
    skyline = []
    def add_point(x):
        h = buildings_by_H.iloc[-1] if buildings_by_H else 0
        if not skyline:
            skyline.append((x, h))
        else:
            x0, h0 = skyline[-1]
            if h != h0:
                if x == x0:
                    skyline[-1] = (x, max(h, h0))
                else:
                    skyline.append((x, h))
    def insert(b, sets=[set()]):
        heapq.heappush(buildings_by_R, (b[2], b))
        s = buildings_by_H.setdefault(b[1], sets[0])
        s.add(b)
        if s == sets[0]:
            sets[0] = set()
        add_point(b[0])
    def delete(b):
        buildings_by_H[b[1]].remove(b)
        if not buildings_by_H[b[1]]:
            del buildings_by_H[b[1]]
        add_point(b[2])
    while buildings_by_L or buildings_by_R: # another sweep line algorithm
        if (not buildings_by_R
            or buildings_by_L
               and buildings_by_L[0][0] <= buildings_by_R[0][0]):
            insert(buildings_by_L.popleft())
        else:
            delete(heapq.heappop(buildings_by_R)[1])
    return skyline

# # test case
# buildings = (
#     (1,9,3), (1,11,5), (2,6,7), (3,13,9), (12,7,16),
#     (14,3,25), (19,18,22), (23,13,29), (24,4,28))
# assert ([(1, 11), (3, 13), (9, 0), (12, 7), (16, 3), (19, 18), (22, 3), (23, 13), (29, 0)]
#     == skyline(deque(buildings)))
