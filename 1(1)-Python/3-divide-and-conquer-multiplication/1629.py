# lib.py의 Matrix 클래스를 참조하지 않음
import sys


"""
TODO:
- fast_power 구현하기 
"""


def fast_power(base: int, exp: int, mod: int) -> int:
    """
    빠른 거듭제곱 알고리즘 구현
    분할 정복을 이용, 시간복잡도 고민!

    Args:
        base: 밑
        exp: 지수
        mod: 나눌 수

    Returns:
        int: (base^exp) % mod
    """
    # 지수가 1이면 base를 mod로 나눈 나머지를 반환
    if exp == 1:
        return base % mod
    
    # 지수를 반으로 나누어 재귀적으로 계산
    half = fast_power(base, exp // 2, mod)
    
    # 짝수 제곱일 때: A^(2n) = A^n * A^n
    if exp % 2 == 0:
        return (half * half) % mod
    # 홀수 제곱일 때: A^(2n+1) = A^n * A^n * A
    else:
        return (half * half * base) % mod

def main() -> None:
    A: int
    B: int
    C: int
    A, B, C = map(int, input().split()) # 입력 고정
    
    result: int = fast_power(A, B, C) # 출력 형식
    print(result) 

if __name__ == "__main__":
    main()
