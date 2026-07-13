from __future__ import annotations
import copy
from collections import deque
from collections import defaultdict
from typing import DefaultDict, List


"""
TODO:
- __init__ 구현하기
- add_edge 구현하기
- dfs 구현하기 (재귀 또는 스택 방식 선택)
- bfs 구현하기
"""


class Graph:
    def __init__(self, n: int) -> None:
        """
        그래프 초기화

        Args:
        n: 정점의 개수 (1번부터 n번까지)

        Returns:
        None

        인접 리스트를 사용하여 그래프를 표현(DefaultDict를 통해 정점이 없는 경우에는 빈 배열 반환)
        """
        self.n = n
        self.graph: DefaultDict[int, List[int]] = defaultdict(list)

    
    def add_edge(self, u: int, v: int) -> None:
        """
        양방향 간선 추가

        ARGS:
        u: 정점 u
        v: 정점 v

        Returns:
        None
        """
        self.graph[u].append(v)
        self.graph[v].append(u)
    
    def dfs(self, start: int) -> list[int]:
        """
        깊이 우선 탐색 (DFS)
        스택 방식: 명시적 스택을 사용하여 반복문으로 구현
        번호가 작은 노드부터 방문하기 위해, 인접 노드를 내림차순으로 정렬하여 스택에 추가

        Args:
        start: 시작 정점 번호

        Returns:
        checklist: 방문한 노드 순서 리스트
        """
        checklist =[]
        checklist_set = set()
        #set를 통해 방문여부를 list보다 빠르게 파악
        stack = [start]

        while stack:
            node= stack.pop()
            if node not in checklist_set:
                checklist.append(node)
                checklist_set.add(node)
                for neighbor in sorted(self.graph[node], reverse=True):
                    if neighbor not in checklist_set:
                        stack.append(neighbor)

        return checklist

    def bfs(self, start: int) -> list[int]:
        """
        너비 우선 탐색 (BFS)
        큐를 사용하여 구현
        번호가 작은 노드부터 방문하기 위해 오름차순으로 정렬해 큐에 추가

        Args:
        start: 시작 정점 번호

        Returns:
        checklist: 방문한 노드 순서 리스트
        """
        cheklist = []
        checklist_set = set()
        queue = deque([start])

        while queue:
            node = queue.popleft()
            if node not in checklist_set:
                cheklist.append(node)
                checklist_set.add(node)
                for neighbor in sorted(self.graph[node]):
                    if neighbor not in checklist_set:
                        queue.append(neighbor)

        return cheklist

    def search_and_print(self, start: int) -> None:
        """
        DFS와 BFS 결과를 출력
        """
        dfs_result = self.dfs(start)
        bfs_result = self.bfs(start)
        
        print(' '.join(map(str, dfs_result)))
        print(' '.join(map(str, bfs_result)))
