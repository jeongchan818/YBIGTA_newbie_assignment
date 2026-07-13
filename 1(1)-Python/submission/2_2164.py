from __future__ import annotations
from collections import deque


"""
TODO:
- rotate_and_remove 구현하기 
"""


def create_circular_queue(n: int) -> deque[int]:
    """1부터 n까지의 숫자로 deque를 생성합니다.
    
    Args:
        n: 정수

    Returns:
        deque[int]: 1부터 n까지의 숫자로 구성된 deque
    """
    return deque(range(1, n + 1))

def rotate_and_remove(queue: deque[int], k: int) -> int:
    """
    큐에서 k번째 원소를 제거하고 반환합니다.
    k-1번째까지는 꺼내서 다시 큐의 뒤로 넣습니다.
    
    Args:
        queue: 원형 큐
        k: 제거할 원소의 위치

    Returns:
        int: 제거된 원소
    """
    for _ in range(k-1):
        queue.append(queue.popleft())  
    a= queue.popleft()
    return a
    




"""
TODO:
- simulate_card_game 구현하기
    # 카드 게임 시뮬레이션 구현
        # 1. 큐 생성
        # 2. 카드가 1장 남을 때까지 반복
        # 3. 마지막 남은 카드 반환
"""


def simulate_card_game(n: int) -> int:
    """
    카드2 문제의 시뮬레이션
    맨 위 카드를 버리고, 그 다음 카드를 맨 아래로 이동
    lib 모듈의 create_circular_queue 함수를 사용하여 큐를 생성

    Args:
        n: 카드의 개수  
    
    Returns:
        int: 마지막 남은 카드
    """
    queue = create_circular_queue(n)
    while len(queue) > 1:
        queue.popleft()  
        queue.append(queue.popleft())  
    return queue[0]  

def solve_card2() -> None:
    """입, 출력 format"""
    n: int = int(input())
    result: int = simulate_card_game(n)
    print(result)

if __name__ == "__main__":
    solve_card2()