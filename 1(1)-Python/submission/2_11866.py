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
- josephus_problem 구현하기
    # 요세푸스 문제 구현
        # 1. 큐 생성
        # 2. 큐가 빌 때까지 반복
        # 3. 제거 순서 리스트 반환
"""


def josephus_problem(n: int, k: int) -> list[int]:
    """
    요세푸스 문제 해결
    n명 중 k번째마다 제거하는 순서를 반환
    rotate_and_remove 함수를 사용하여 k번째 사람을 제거하고, 제거된 사람의 번호를 result 리스트에 추가

    Args:
        n: 사람 수
        k: 제거할 사람의 위치
    
    Returns:
        list[int]: 제거된 사람들의 순서 리스트
    """
    queue = create_circular_queue(n)
    result = []
    while len(queue) > 0:
        a= rotate_and_remove(queue, k)
        result.append(a)
    return result

def solve_josephus() -> None:
    """입, 출력 format"""
    n: int
    k: int
    n, k = map(int, input().split())
    result: list[int] = josephus_problem(n, k)
    
    # 출력 형식: <3, 6, 2, 7, 5, 1, 4>
    print("<" + ", ".join(map(str, result)) + ">")

if __name__ == "__main__":
    solve_josephus()