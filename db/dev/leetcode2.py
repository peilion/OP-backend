from typing import List


class Solution:
    def addBinary(self, a: str, b: str) -> str:
        lb = len(b)
        la = len(a)

        a = a[::-1]
        b = b[::-1]
        sm = b if lb <= la else a
        lg = a if lb <= la else b
        res = ''
        next_increase = 0
        for i in range(len(sm)):
            sm_i = int(sm[i])
            lg_i = int(lg[i])
            res += str((sm_i + lg_i + next_increase) % 2)
            next_increase = int((sm_i + lg_i + next_increase) / 2)
        if len(lg) > len(sm):
            for i in range(len(sm), len(lg)):
                res += str((int(lg[i]) + next_increase) % 2)
                next_increase = int((int((lg[i])) + next_increase) / 2)
            res += str(next_increase) if next_increase != 0 else ''

        if len(lg) == len(sm):
            res += str(next_increase) if next_increase != 0 else ''
        return res[::-1]


class Solution:
    def threeSumClosest(self, nums: List[int], target: int) -> int:
        import collections
        nums.sort()
        num_dic = collections.Counter(nums)
        min_ = [nums[0], nums[1], nums[2]]
        min_sum = abs(sum(min_) - target)

        def find(min_, min_sum, nums, target):
            for i in range(len(nums)):
                if nums[i] in min_:
                    dic = collections.Counter(min_)
                    if dic[nums[i]] + 1 > num_dic[nums[i]]:
                        continue
                r1 = [nums[i], min_[1], min_[2]]
                r2 = [min_[0], nums[i], min_[2]]
                r3 = [min_[0], min_[1], nums[i]]
                x = [abs(sum(r1) - target), abs(sum(r2) - target), abs(sum(r3) - target)]
                if min(x) < min_sum:
                    min_sum = min(x)
                    if x.index(min(x)) == 0:
                        return min_sum, r1, True
                    elif x.index(min(x)) == 1:
                        return min_sum, r2, True
                    elif x.index(min(x)) == 2:
                        return min_sum, r3, True
            return min_sum, min_, False

        cont = True
        while cont:
            min_sum, min_, cont = find(min_, min_sum, nums, target)

        return sum(min_)


class Solution:
    def wordBreak(self, s: str, wordDict: List[str]) -> bool:
        import collections
        import functools
        s_counter = collections.Counter(s)
        w_s = ''
        for item in wordDict:
            w_s += item
        w_counter = collections.Counter(w_s)
        for key in s_counter.keys():
            if key not in w_counter.keys():
                return False
        max_ = max([len(item) for item in wordDict])
        wordDict = collections.Counter(wordDict)

        @functools.lru_cache(None)
        def find(word):
            if len(word) == 0: return True
            for i in range(min(len(word),max_)):
                if word[:i + 1] in wordDict.keys():
                    found = find(word[i + 1:])
                    if found:
                        return True
            return False

        res = find(s)
        return res

class Solution:
    def restoreIpAddresses(self, s: str) -> List[str]:
        length = len(s)
        res = []
        for i in range(1,4):
            for j in range(1,4):
                for k in range(1,4):
                    if i+j+k< length:
                        one = s[:i]
                        two = s[i:i+j]
                        three = s[i+j:i+j+k]
                        four = s[i+j+k:]
                        if all([ int(item) <= 255 and len(str(int(item))) == len(item) for item in [one,two,three,four]]):
                            res.append('{0}.{1}.{2}.{3}'.format(one,two,three,four))
        return res


class Singleton(object):
    def __new__(cls, *args, **kw):
        if not hasattr(cls, '_instance'):
            orig = super(Singleton, cls)
            cls._instance = orig.__new__(cls, *args, **kw)
        return cls._instance



class Node:
    def __init__(self, val=0, neighbors=[]):
        self.val = val
        self.neighbors = neighbors


class Solution:
    def cloneGraph(self, node: 'Node') -> 'Node':

        copy_list = [Node(node.val, None)]
        node_list = [node]

        def helper(neighbors):
            if neighbors[0] not in node_list:
                node_list.append(neighbors[0])
                copy_list.append(Node(neighbors[0].val, None))
                helper(neighbors[0].neighbors)
            if neighbors[1] not in node_list:
                node_list.append(neighbors[1])
                copy_list.append(Node(neighbors[1].val, None))
                helper(neighbors[1].neighbors)

        helper(node.neighbors)
        return copy_list


class TreeNode:
    def __init__(self, x,):
        self.val = x
        self.left = None
        self.right = None


class Solution:
    def buildTree(self, inorder: List[int], postorder: List[int]) -> TreeNode:
        if len(inorder) == 0:
            return None
        def helper(inord, pord):
            root_val = pord[-1]

            left_in = inord[:inord.index(root_val)]
            right_in = inord[inord.index(root_val) + 1:]

            if len(left_in) == 0:
                left_node = None
            else:
                left_post = pord[:len(pord) - len(right_in)-1]
                left_node = helper(left_in, left_post)

            if len(right_in) == 0:
                right_node = None
            else:
                right_post = pord[len(pord) - len(right_in)-1:len(pord)-1]
                right_node = helper(right_in, right_post)

            node = TreeNode(root_val)
            node.left = left_node
            node.right = right_node
            return node

        node = helper(inorder, postorder)
        return node

class Solution:
    def maximalSquare(self, matrix: List[List[str]]) -> int:
        rows = len(matrix)
        cols = len(matrix[0])
        max_ = float('-inf')
        dp = [[0]* cols for i in range(rows)]
        for i in range(rows):
            for j in range(cols):
                if j == 0 or i ==0:
                    dp[i][j] = int(matrix[i][j])
                    max_ = max(max_,dp[i][j])
                else:
                    if (dp[i-1][j-1] * dp[i][j-1] * dp[i-1][j] * int(matrix[i][j]) ) > 0:
                        dp[i][j] = min(dp[i-1][j-1] , dp[i][j-1] , dp[i-1][j]) + 1
                    else :
                        dp[i][j] =int(matrix[i][j])
                    max_ = max(max_,dp[i][j])
        return dp

if __name__ == "__main__":
    from db.dev.leetcode2 import Solution
    import itertools


    res = Solution().maximalSquare([
        ["0","0","0","1"],
        ["1","1","0","1"],
        ["1","1","1","1"],
        ["0","1","1","1"],
        ["0","1","1","1"]])
    print(res)
