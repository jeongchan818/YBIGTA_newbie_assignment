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
    