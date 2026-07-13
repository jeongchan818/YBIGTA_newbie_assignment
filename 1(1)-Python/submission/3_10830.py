from __future__ import annotations
import copy


"""
TODO:
- __setitem__ 구현하기
- __pow__ 구현하기 (__matmul__을 활용해봅시다)
- __repr__ 구현하기
"""


class Matrix:
    MOD = 1000

    def __init__(self, matrix: list[list[int]]) -> None:
        self.matrix = matrix

    @staticmethod
    def full(n: int, shape: tuple[int, int]) -> Matrix:
        return Matrix([[n] * shape[1] for _ in range(shape[0])])

    @staticmethod
    def zeros(shape: tuple[int, int]) -> Matrix:
        return Matrix.full(0, shape)

    @staticmethod
    def ones(shape: tuple[int, int]) -> Matrix:
        return Matrix.full(1, shape)

    @staticmethod
    def eye(n: int) -> Matrix:
        matrix = Matrix.zeros((n, n))
        for i in range(n):
            matrix[i, i] = 1
        return matrix

    @property
    def shape(self) -> tuple[int, int]:
        return (len(self.matrix), len(self.matrix[0]))

    def clone(self) -> Matrix:
        return Matrix(copy.deepcopy(self.matrix))

    def __getitem__(self, key: tuple[int, int]) -> int:
        return self.matrix[key[0]][key[1]]

    def __setitem__(self, key: tuple[int, int], value: int) -> None:
        """
        행렬의 특정 위치에 값을 정해줍니다.

        Args:
            key: (행, 열) 위치를 나타내는 튜플
            value: 설정할 값

        Returns:
            None
        """
        self.matrix[key[0]][key[1]] = value

    def __matmul__(self, matrix: Matrix) -> Matrix:
        x, m = self.shape
        m1, y = matrix.shape
        assert m == m1

        result = self.zeros((x, y))

        for i in range(x):
            for j in range(y):
                for k in range(m):
                    result[i, j] += self[i, k] * matrix[k, j]

        return result

    def __pow__(self, n: int) -> Matrix:
        """
        행렬의 거듭제곱을 계산합니다.
        지수를 반으로 쪼개는 '분할 정복'을 사용해 O(log n)으로 속도를 최적화

        Args:
            n: 거듭제곱할 정수  

        Returns:
            Matrix: self의 n제곱
        """
        if n == 1:
            result = self.clone()
            for i in range(result.shape[0]):
                for j in range(result.shape[1]):
                    result[i, j] %= self.MOD
            return result
        
        # 지수를 반으로 쪼개서 계산
        half = self ** (n // 2)
        
        if n % 2 == 0:
            result = half @ half
        else:
            result = half @ half @ self
            
        # 결과에 MOD 연산 적용
        for i in range(result.shape[0]):
            for j in range(result.shape[1]):
                result[i, j] %= self.MOD
                
        return result
    def __repr__(self) -> str:
        """
        행렬을 출력(print)할 때 보여줄 문자열 형태를 정의
        각 행의 원소들은 공백으로 띄우고, 행 단위로는 줄바꿈(\n)이 되도록 문자열을 생성
        
        Returns:
            str: 행렬을 문자열로 표현한 결과
        """
        rows = []
        for row in self.matrix:
            # 각 행의 숫자들을 띄어쓰기로 연결
            rows.append(" ".join(map(str, row)))
        # 행들을 줄바꿈으로 연결하여 출력 문자열 생성
        return "\n".join(rows)


from typing import Callable
import sys


"""
-아무것도 수정하지 마세요!
"""


def main() -> None:
    intify: Callable[[str], list[int]] = lambda l: [*map(int, l.split())]

    lines: list[str] = sys.stdin.readlines()

    N, B = intify(lines[0])
    matrix: list[list[int]] = [*map(intify, lines[1:])]

    Matrix.MOD = 1000
    modmat = Matrix(matrix)

    print(modmat ** B)


if __name__ == "__main__":
    main()