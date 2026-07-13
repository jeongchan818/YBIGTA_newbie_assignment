from __future__ import annotations

from dataclasses import dataclass, field
from typing import TypeVar, Generic, Optional, Callable


"""
TODO:
- SegmentTree 구현하기
"""


T = TypeVar("T")
U = TypeVar("U")


class SegmentTree(Generic[T, U]):
    def __init__(self, data, merge, default, apply_update):
        """
        Segment Tree 생성자
        Args:
            data (list): 초기 데이터
            merge (Callable[[T, T], T]): 구간 합치는 방법
            default (T): 범위 벗어났을 때 사용할 값
            apply_update (Callable[[T, U], T]): 업데이트 적용 방법
        """
        self.n = len(data)
        self.merge = merge # 구간 합치는 방법
        self.default = default # 범위 벗어낫을 때 사용할 값
        self.tree = [self.default] * (4 * self.n) # 트리 배열 크기

    def _build(self, data, start, end, node):
        """ 
        초기 데이터를 트리에 채워 넣기
        Args:
            data (list): 초기 데이터
            start (int): 현재 구간 시작 인덱스
            end (int): 현재 구간 끝 인덱스
            node (int): 현재 노드 인덱스
        """
        #리프노드에 도착한 경우
        if start == end:
            self.tree[node] = data[start]
            return
        #반으로 쪼개기
        mid = (start + end) // 2
        self._build(data, start, mid, 2 * node + 1)
        self._build(data, mid + 1, end, 2 * node)
        # 두 값 합치기
        self.tree[node] = self.merge(self.tree[node * 2], self.tree[node * 2 + 1])

    def _update(self, start, end, node, index, val):
        """
        특정 인덱스의 값을 업데이트
        Args:
            start (int): 현재 구간 시작 인덱스
            end (int): 현재 구간 끝 인덱스
            node (int): 현재 노드 인덱스
            index (int): 업데이트할 인덱스
            val (U): 업데이트할 값
        """
        #리프노드에 도착한 경우
        if start == end:
            self.tree[node] = val
            return
        #index가 어느 구간에 있는지 판단
        mid = (start + end) // 2
        if index <= mid:
            self._update(start, mid, 2 * node + 1, index, val)
        else:
            self._update(mid + 1, end, 2 * node + 2, index, val)
        # 리프노드에서 올라오면서 부모 노드 값 갱신
        self.tree[node] = self.merge(self.tree[2 * node + 1], self.tree[2 * node + 2])  
    
    def _query(self, start, end, node, left, right):
        """
        특정 구간의 값을 조회
        Args:
            start (int): 현재 구간 시작 인덱스
            end (int): 현재 구간 끝 인덱스
            node (int): 현재 노드 인덱스
            left (int): 조회할 구간 시작 인덱스
            right (int): 조회할 구간 끝 인덱스
        Returns:
            T: 조회한 구간의 값
        """
        # 범위를 벗어난 경우
        if left > end or right < start:
            return self.default
        # 범위 안에 있는 경우
        if left <= start and end <= right:
            return self.tree[node]
        # 범위가 걸쳐있는 경우
        mid = (start + end) // 2
        left_result = self._query(start, mid, 2 * node + 1, left, right)
        right_result = self._query(mid + 1, end, 2 * node + 2, left, right)
        return self.merge(left_result, right_result)
    
    def update(self, index: int, val: U) -> None:
        """외부에서 인덱스와 값만 넘겨주면, 알아서 루트 노드부터 업데이트를 시작하는 래퍼 함수"""
        # 트리 전체 범위(0부터 n-1까지)와 루트 노드(1번)를 시작점으로 지정하여 내부 함수 호출
        self._update(0, self.n - 1, 1, index, val)

    def query(self, left: int, right: int) -> T:
        """외부에서 탐색할 구간만 넘겨주면, 알아서 루트 노드부터 탐색을 시작하는 래퍼 함수"""
        return self._query(0, self.n - 1, 1, left, right)
    


import sys


"""
TODO:
- 일단 SegmentTree부터 구현하기
- main 구현하기
"""


def main() -> None:
    # 구현하세요!
    pass


if __name__ == "__main__":
    main()