from lib import Trie
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