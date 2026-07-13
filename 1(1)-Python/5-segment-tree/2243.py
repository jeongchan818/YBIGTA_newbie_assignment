from lib import SegmentTree
import sys


"""
TODO:
- 일단 SegmentTree부터 구현하기
- main 구현하기
"""


def main() -> None:
    '''
    data index - 사탕의 맛
    data value - 사탕의 개수
    binary search를 통해 k번째 사탕의 맛을 빠르게 찾는다.
    ''' 
    input = sys.stdin.readline
    Max_flavor = 1000000
    data = [0] * (Max_flavor + 1)

    tree = SegmentTree[int, int](
        data=data, merge=lambda a, b: a + b,
        default=0, apply_update=lambda old, y: old + y)
    
    n = int(input().strip())

    for i in range(n):
        q= list(map(int, input().split()))

        if q[0] == 2:
            flavor = q[1]
            count_diff = q[2]
            tree.update(flavor, count_diff)
        
        elif q[0] == 1:
            k = q[1]
            left =1
            right = Max_flavor
            target_flavor = 0

            # binary search
            while left <= right:
                mid = (left + right) //2
                count_1_to_mid = tree.query(1, mid)

                if count_1_to_mid >= k:
                    target_flavor = mid
                    right = mid - 1
                else:
                    left = mid + 1
            print(target_flavor)
            tree.update(target_flavor, -1)  # 꺼낸 사탕 빼주기


if __name__ == "__main__":
    main()