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