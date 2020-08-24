import sys
if __name__ == "__main__":
    # 读取第一行的n
    first_line = sys.stdin.readline().strip().split(' ')
    n,k = int(first_line[0]),int(first_line[1])
    node_value_list = sys.stdin.readline().strip().split(' ')
    class ListNode:
        def __init__(self,val):
            self.val = val
            self.next = None
    node = ListNode(node_value_list[0])
    head = node
    ans = str(node_value_list[0]) + ' '
    for index,val in enumerate(node_value_list[1:]):
        if index == k - 2 :
            pass
        else:
            temp = ListNode(val)
            node.next = temp
            node = temp
            ans += str(temp.val) + ' '
    print(ans)


import sys
if __name__ == "__main__":
    # 读取第一行的n
    s = sys.stdin.readline().strip()
    k = int(sys.stdin.readline().strip())
    cum = 0
    ans = None
    res = []
    for i in range(len(s)):
        for j in range(i+1,len(s)):
            cum +=1
            if cum == k:
                ans = s[i:j]
                break
        if ans is not None:
            break
    print(ans)