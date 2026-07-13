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
- 일단 Trie부터 구현하기
- count 구현하기
- main 구현하기
"""


def count(trie: Trie, query_seq: str) -> int:
    """
    Args:
        trie - trie
        query_seq - 단어 

    returns: 
        query_seq의 단어를 입력하기 위해 버튼을 눌러야 하는 횟수
    """
    pointer = 0
    cnt = 0

    for element in query_seq:
        if len(trie[pointer].children) > 1 or trie[pointer].is_end:
            cnt += 1

        new_index = None
        for child_idx in trie[pointer].children:
            if trie[child_idx].body == element:
                new_index = child_idx
                break
                
        if new_index is not None:
            pointer = new_index    

    return cnt + int(len(trie[0].children) == 1)


def main() -> None:
    """
    표준 입력으로 주어지는 여러 개의 테스트 케이스를 순차적으로 처리하는 함수.
    
    각 테스트 케이스마다 단어들을 Trie에 저장
    모든 단어를 입력하기 위해 눌러야 하는 총 버튼 횟수를 구하고
    전체 단어 개수로 나눈 평균을 소수점 둘째 자리까지 반올림하여 출력"""
    input_data = sys.stdin.read().split()
    idx = 0
    
    while idx < len(input_data):
        n = int(input_data[idx])
        idx += 1
        
        words = input_data[idx:idx+n]
        idx += n
        
        trie: Trie[str] = Trie()
        for word in words:
            trie.push(word)
            
        total_keystrokes = 0
        for word in words:
            total_keystrokes += count(trie, word)
            
        print(f"{total_keystrokes / n:.2f}")


if __name__ == "__main__":
    main()