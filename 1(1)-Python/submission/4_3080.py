from dataclasses import dataclass, field
from typing import TypeVar, Generic, Optional, Iterable


"""
TODO:
- Trie.push 구현하기
- (필요할 경우) Trie에 추가 method 구현하기
"""


T = TypeVar("T")


@dataclass
class TrieNode(Generic[T]):
    body: Optional[T] = None
    children: list[int] = field(default_factory=lambda: [])
    is_end: bool = False


class Trie(list[TrieNode[T]]):
    def __init__(self) -> None:
        super().__init__()
        self.append(TrieNode(body=None))

    def push(self, seq: Iterable[T]) -> None:
        """
        Trie에 단어를 삽입하는 메서드
        
        ARGS:
        seq - 단어를 구성하는 글자들의 시퀀스

        RETURNS:
        None
        """
        curr_idx = 0
        
        for val in seq:
            next_idx = -1
            # 현재 노드의 자식들 중 값이 일치하는 노드 탐색
            for child_idx in self[curr_idx].children:
                if self[child_idx].body == val:
                    next_idx = child_idx
                    break
            
            # 일치하는 자식이 없다면 새 노드 생성 및 연결
            if next_idx == -1:
                next_idx = len(self)
                self.append(TrieNode(body=val))
                self[curr_idx].children.append(next_idx)
            
            # 다음 노드로 이동
            curr_idx = next_idx
            
        # 시퀀스의 마지막 노드에 단어의 끝 표시
        self[curr_idx].is_end = True

    # 구현하세요!


import sys


"""
TODO:
- 일단 lib.py의 Trie Class부터 구현하기
- main 구현하기

힌트: 한 글자짜리 자료에도 그냥 str을 쓰기에는 메모리가 아깝다...
"""


def main() -> None:
    """
    input_data를 읽고 trie에 push한 뒤, 경우의 수를 계산하여 출력하는 함수
    메모리 절약을 위해 trie에 문자열을 아스키코드 열로 push
   
    ARGS:
    None

    RETURNS:
    None 
    상근이의 규칙을 지키면서 순서를 정하는 방법의 수를 1,000,000,007로 나눈 나머지를 출력
    """
    # 전체 데이터 읽기
    input_data = sys.stdin.read().split()
    if len(input_data) < 2:
        return
    
    n = int(input_data[0])
    words = input_data[1:]
    
    trie: Trie[int] = Trie()
    
    # Trie에 문자열 삽입
    # 메모리 절약을 위해 문자열을 byte로 변환하여 아스키코드(정수)로 push
    for word in words:
        trie.push(word.encode('ascii'))
        
    ans = 1 #answer 초기화
    MOD = 1000000007
    
    # Trie 클래스가 list[TrieNode]를 상속받았으므로 내부 배열을 직접 순회
    for node in trie:
        # branches 개수 산정: 자식 노드의 수 + (현재 노드가 끝이면 1 추가)
        branches = len(node.children)
        if node.is_end:
            branches += 1
            
        # branches가 2개 이상일 때는 순열 계산
        if branches > 1:
            for i in range(2, branches + 1):
                ans = (ans * i) % MOD
                
    print(ans)


if __name__ == "__main__":
    main()