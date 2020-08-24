from typing import List


class Solution:
    def isPalindrome(self, x: int) -> bool:
        s = str(x)
        if s[0] == "-":
            return False
        if len(s) % 2 != 0:
            for i in range(int((len(s) - 1) / 2)):
                if s[i] != s[-i - 1]:
                    return False
        else:
            for i in range(int(len(s) / 2)):
                if s[i] != s[-i - 1]:
                    return False
        return True


class Solution1:
    def searchInsert(self, nums: List[int], target: int) -> int:
        if target in nums:
            return nums.index(target)
        else:
            if target < nums[0]:
                return 0
            if target > nums[-1]:
                return len(nums)
            for i in range(len(nums)):
                if (nums[i] - target < 0) and (nums[i + 1] - target > 0):
                    return i + 1


class Solution2:
    def exist(self, board: List[List[str]], word: str) -> bool:

        size_r = len(board) - 1
        size_c = len(board[0]) - 1

        def search(r, c, word_index, path):
            if word_index > len(word) - 1:
                return True
            for around in [[1, 0], [0, 1], [-1, 0], [0, -1]]:
                position_r = r + around[0]
                position_c = c + around[1]
                if (
                        (position_r > size_r)
                        or (position_r < 0)
                        or (position_c > size_c)
                        or (position_c < 0)
                        or ((position_r, position_c) in path)
                ):
                    continue
                if board[position_r][position_c] == word[word_index]:
                    path.add((position_r, position_c))
                    found = search(position_r, position_c, word_index + 1, path)
                    if not found:
                        path.remove((position_r, position_c))
                    else:
                        return True
            return False

        for r in range(size_r + 1):
            for c in range(size_c + 1):
                if (word[0] == board[r][c]) and search(r, c, 1, {(r, c)}):
                    return True
        return False


'''
给你一个包含 n 个整数的数组 nums，判断 nums 中是否存在三个元素 a，b，c ，使得 a + b + c = 0 ？请你找出所有满足条件且不重复的三元组。

注意：答案中不可以包含重复的三元组。

给定数组 nums = [-1, 0, 1, 2, -1, -4]，

满足要求的三元组集合为：
[
  [-1, 0, 1],
  [-1, -1, 2]
]
'''


class Solution5:
    def threeSum(self, nums: List[int]) -> List[List[int]]:
        num_dict = {}
        res = set()
        for num in nums:
            num_dict.setdefault(num, 0)
            num_dict[num] += 1
        num_key = list(num_dict.keys())
        num_key.sort()
        for i in range(len(num_key)):
            for j in range(i, i + len(num_key[i:])):
                if num_key[i] > 0:
                    return [list(item) for item in res]
                a = num_key[i]
                b = num_key[j]
                num_dict[a] = num_dict[a] - 1
                num_dict[b] = num_dict[b] - 1

                if (-a - b in num_dict):
                    if ((num_dict[-a - b]) > 0) & ((num_dict[a]) >= 0) & ((num_dict[b]) >= 0):
                        result = [a, b, -a - b]
                        result.sort(reverse=True)
                        res.add(tuple(result))
                num_dict[a] = num_dict[a] + 1
                num_dict[b] = num_dict[b] + 1

        return [list(item) for item in res]


class Solution6:
    def climbStairs(self, n: int) -> int:
        if n == 1:
            return 1
        res = 0
        mod = n % 2
        for i in range(int(n / 2) if mod == 0 else int(n / 2) + 1, n + 1):
            num2 = n % i
            num1 = n - 2 * num2
            if (num2 == 0) or (num1 == 0):
                res += 1
                print('{0}步，{1}个2，{2}个1，方案数{3}'.format(i, num2, num1, 1))

                continue

            if (num2 == 1):
                res += num1 + 1
                print('{0}步，{1}个2，{2}个1，方案数{3}'.format(i, num2, num1, num1 + 1))

                continue
            if (num1 == 1):
                res += num2 + 1
                print('{0}步，{1}个2，{2}个1，方案数{3}'.format(i, num2, num1, num2 + 1))

                continue
            mother = 1
            for j in range(1, i + 1):
                mother = mother * j
            child1 = 1
            for k in range(1, num2 + 1):
                child1 = child1 * k
            child2 = 1
            for k in range(1, i - num2 + 1):
                child2 = child2 * k
            res += (mother / (child1 * child2))
            print('{0}步，{1}个2，{2}个1，分子{3}，分母{4}，方案数{5}'.format(i, num2, num1, mother, child1 * child2,
                                                               mother / (child1 * child2)))
        return int(res)


class Solution8:
    def sum(self, arr):
        sum = 0
        for i in arr:
            sum += i
        return sum

    def replace_sum(self, arr, num):
        length = len(arr)
        for i in range(length):
            if arr[length - i - 1] >= num:
                arr[length - i - 1] = num
            else:
                break
        sum = self.sum(arr)
        return sum

    def findArrayMin(self, arr):
        min = arr[0]
        min_index = 0
        min_res = [min]
        min_index_res = [0]
        for index, item in enumerate(arr[1:]):
            if item < min:
                min_res = [item]
                min_index_res = [index + 1]
            elif item == min:
                min_res.append(item)
                min_index_res.append(index + 1)
        return min_index_res

    def findBestValue(self, arr: List[int], target: int) -> int:
        if (len(arr) > target):
            return 0
        arr.sort()
        # 第一轮
        distance_list = []

        for i in range(len(arr)):
            arr_copy = [item for item in arr]
            replace_value = arr[i]
            sum = self.replace_sum(arr_copy, replace_value)
            local_distance = abs(sum - target)
            if i == 0:
                distance_list.append(local_distance)
            else:
                if local_distance <= distance_list[i - 1]:
                    distance_list.append(local_distance)
                else:
                    distance_list.append(local_distance)

                    break

        min_index = self.findArrayMin(distance_list)
        search_range = []

        if len(min_index) == 1:
            if (min_index[0] == 0):
                search_range = [0, arr[1]]
            elif min_index[0] == (len(arr) - 1):
                search_range = [0, arr[-1]]
            else:
                search_range = [arr[min_index[0] - 1], arr[min_index[0] + 1]]
        else:
            if arr[min_index[1]] == arr[min_index[0]]:
                if (min_index[0] == 0):
                    search_range = [0, arr[1]]
                else:
                    search_range = [arr[min_index[1]], arr[min_index[1] + 1]]
            else:
                search_range = [arr[min_index[0]], arr[min_index[1]]]

            # 第二轮
        replace_value = search_range[1]

        distance = abs(self.sum(arr) - target)
        for i in range(search_range[1], search_range[0] - 1, -1):
            arr_copy = [item for item in arr]

            sum = self.replace_sum(arr_copy, i)
            new_distance = abs(sum - target)
            print('新距离{0}，旧距离{1}，新数组{2}，替换值{3}'.format(new_distance, distance, arr_copy, i))
            if new_distance <= distance:
                distance = new_distance
                replace_value = i
            elif new_distance > distance:
                break

        return replace_value


class Solution9:
    def find_min(self, strs):
        min_index = [0]
        min = len(strs[0])
        for index, item in enumerate(strs[1:]):
            if len(item) < min:
                min_index = [index + 1]
                min = len(item)
            elif len(item) == min:
                min_index.append(index + 1)

        return min_index

    def longestCommonPrefix(self, strs: List[str]) -> str:
        if len(strs) == 0:
            return ''
        res = ''
        min_index = self.find_min(strs)[0]
        min_str = strs[min_index]
        for char_index, char in enumerate(min_str):
            for item in strs:
                if item[char_index] != char:
                    return res
            res = res + char
        return res


class Solution10:
    def maxScoreSightseeingPair(self, A: List[int]) -> int:
        left = A[0]
        res = 0
        for lindex, litem in enumerate(A[1:]):
            lindex += 1
            res = max(res, left + A[lindex] - lindex)
            left = max(left, A[lindex] + lindex)
        return res


class Solution11:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        dic = {}
        for item in nums:
            dic.setdefault(item, 0)
            dic[item] += 1
        for num in dic.keys():
            require_num = target - num
            dic[num] = dic[num] - 1
            if require_num in dic.keys():
                if dic[require_num] > 0:
                    break
            dic[num] = dic[num] + 1
        first = nums.index(num)
        del nums[first]
        second = nums.index(require_num) + 1
        return [first, second]


class Solution12:
    def calPoints(self, ops: List[str]) -> int:
        values = []
        res = 0
        for round in ops:
            if round == 'C':
                res -= values[-1]
                values.pop()
            elif round == 'D':
                res += 2 * values[-1]
                values.append(2 * values[-1])
            elif round == '+':
                res = res + values[-1] + values[-2]
                values.append(values[-1] + values[-2])
            else:
                res += int(round)
                values.append(int(round))
        return res


class Solution13:
    def compressString(self, S: str) -> str:
        res = ''
        for i in range(len(S)):
            if i == 0:
                res = ''
                counter = 0
            elif S[i] != S[i - 1]:
                counter += 1
                res = res + S[i - 1] + str(counter)
                counter = 0
            else:
                counter += 1

            if i == len(S) - 1:
                counter += 1
                res = res + S[i] + str(counter)
        return res if len(res) < len(S) else S


import base64


class Codec:
    def __init__(self):
        self.encode_book = {}

    def encode(self, longUrl: str) -> str:
        s = base64.b64encode(longUrl.encode('utf8')).decode('utf8')
        key = ''
        for i in range(10):
            if s[i:i + 5] not in self.encode_book.keys():
                key = s[i:i + 5]
                self.encode_book[s[i:i + 5]] = longUrl
                break
        return 'http://tinyurl.com/' + key

    def decode(self, shortUrl: str) -> str:
        """Decodes a shortened URL to its original URL.
        """
        s = shortUrl.split('.com/')[1]
        url = self.encode_book[s]
        return url


# Definition for a binary tree node.
class TreeNode:
    def __init__(self, x, d):
        self.val = x
        self.left = None
        self.right = None
        self.depth = d


class Solution14:

    def recoverFromPreorder(self, S: str) -> TreeNode:
        def add_node(pnode, cnode):
            if pnode.left is None:
                pnode.left = cnode
            elif (pnode.left is not None) and (pnode.right is None):
                pnode.right = cnode
            else:
                raise ('Node occupied!')

        if '-' not in S:
            return TreeNode(int(S), 0)
        res_list = []
        item = ''
        depth = 0
        max_depth = 0
        for i in range(len(S)):
            if i == 0:
                item = item + S[i]
            elif i == len(S) - 1:
                res_list.append((item + S[i], depth))
                max_depth = max(max_depth, depth)

            else:
                if (S[i] == '-') and (S[i - 1] != '-'):
                    res_list.append((item, depth))
                    max_depth = max(max_depth, depth)
                    item = ''
                    depth = 1
                elif (S[i] != '-') and (S[i - 1] != '-'):
                    item += S[i]
                elif (S[i] == '-') and (S[i - 1] == '-'):
                    depth += 1
                elif (S[i] != '-') and (S[i - 1] == '-'):
                    item += S[i]

        root_node = TreeNode(res_list[0][0], 0)
        res_list[0] = (res_list[0][0], res_list[0][1], root_node)
        pre_node = None
        parent_node = None
        for i in range(1, len(res_list)):
            node = res_list[i]
            cur_node = TreeNode(node[0], node[1])
            if (i == 1):
                add_node(root_node, cur_node)
                pre_node = cur_node
                parent_node = root_node

            elif node[1] == pre_node.depth:
                add_node(parent_node, cur_node)
                pre_node = cur_node

            elif node[1] > pre_node.depth:
                parent_node = pre_node
                add_node(pre_node, cur_node)
                pre_node = cur_node

            elif node[1] < pre_node.depth:
                for j in range(len(res_list[:i]) - 1, -1, -1):
                    if res_list[j][1] == node[1] - 1:
                        parent_node = res_list[j][2]
                        break
                add_node(parent_node, cur_node)
                pre_node = cur_node

            res_list[i] = (res_list[i][0], res_list[i][1], cur_node)

        def assign_null_node(node):
            if node.depth < max_depth:
                if node.left is None:
                    node.left = TreeNode(None, node.depth + 1)
                else:
                    assign_null_node(node.left)
                if node.right is None:
                    node.right = TreeNode(None, node.depth + 1)
                else:
                    assign_null_node(node.right)

        # assign_null_node(root_node)
        return root_node, res_list


class Solution15:
    def countCharacters(self, words: List[str], chars: str) -> int:
        import collections
        char_dic = collections.Counter(chars)
        res = 0
        for word in words:
            learnable = True
            word_dic = collections.Counter(word)
            for key in word_dic.keys():
                if key in char_dic:
                    if char_dic[key] >= word_dic[key]:
                        continue
                    else:
                        learnable = False
                        break
                else:
                    learnable = False
                    break
            if learnable:
                res += len(word)
        return res


class Solution16:
    def convertToBase7(self, num: int) -> str:
        if num == 0:
            return 0
        unfinished = True
        count = abs(num)
        res = ''
        while unfinished:
            rest = count % 7
            res += str(rest)
            count = int(count / 7)
            if count < 7:
                if count != 0:
                    res += str(count)
                unfinished = False
        res = "".join(list(res)[::-1])
        if num < 0:
            res = '-' + res
        return res


class Solution16:
    def maximalRectangle(self, matrix: List[List[str]]) -> int:
        maxmal = 0
        for rindex in range(len(matrix)):
            row = matrix[rindex]
            link_group = []
            start_cindex = None
            length = 0
            for cindex, item in enumerate(row):
                if (item == '1') and (start_cindex is None):
                    start_cindex = cindex
                    length += 1
                elif (item == '1') and (start_cindex is not None):
                    length += 1
                elif (item == '0') and (start_cindex is not None):
                    link_group.append((start_cindex, length))
                    start_cindex = None
                    length = 0
            if start_cindex is not None:
                link_group.append((start_cindex, length))
            for link in link_group:
                for item in range(0, link[1]):
                    start_cindex = link[0] + item
                    length = link[1] - item
                    width = 1
                    for row in matrix[rindex + 1:]:
                        if row[start_cindex:start_cindex + length] == ['1' for i in range(length)]:
                            width += 1
                        else:
                            break
                    for row in range(rindex - 1, 0 - 1, -1):
                        row = matrix[row]
                        if row[start_cindex:start_cindex + length] == ['1' for i in range(length)]:
                            width += 1
                        else:
                            break
                    maxmal = max(maxmal, length * width)
        return maxmal


class Solution17:
    def isMatch(self, s: str, p: str) -> bool:
        pl = p.split('*')
        x = []
        for item in pl:
            if item == '.':
                x.append('.')
            elif '.' in item:
                ls = ''
                for i in item:
                    if i != '.':
                        ls += i
                    else:
                        x.append(ls)
                        x.append('.')
                        ls = ''

            else:
                x.append(item)
        pll = []
        for index, item in enumerate(x):
            if index == len(pl) - 1:
                pll.append(item)
            elif len(item) == 1:
                pll.append(item + '*')
            else:
                pll.append(item[:-1])
                pll.append(item[-1] + '*')

        if p.endswith('*'):
            pll.pop()

        count = 0
        for item in pll:
            if '*' not in item:
                count += len(item)
        if count > len(s):
            return False

        def match_item(s: str, sp: str):
            if sp == '.*':
                return True, len(s)
            elif sp == '.':
                return True, 1
            elif '*' in sp:
                if not s.startswith(sp[0]):
                    return True, 0
                n = 1
                while True:
                    if s.startswith(n * sp[0]):
                        n += 1
                    else:
                        return True, n - 1
            elif '.' in sp:
                for i in range(len(sp)):
                    if (s[i] != sp[i]) and (sp[i] != '.'):
                        return False, 0
                return True, len(sp)
            else:
                if s[:len(sp)] == sp:
                    return True, len(sp)
                else:
                    return False, 0

        def match(s, pll):
            increase = 0
            pll_index = 0
            first_matched = False
            while increase != len(s):
                if (pll_index > len(pll) - 1) and not first_matched:
                    return False
                elif (pll_index > len(pll) - 1) and first_matched:
                    return True
                prefix = pll[pll_index]
                matched, inc = match_item(s[increase:], prefix)
                increase = increase + inc
                if not matched:
                    return False
                if (increase == len(s)) and (pll_index < len(pll) - 1):
                    if (pll_index + 1 == len(pll) - 1) and ('*' in pll[pll_index + 1]):
                        return True
                    first_matched = True
                    sc_matched = False
                    for i in range(inc, 0, -1):
                        eincrease = increase - i
                        res = match(s[eincrease:], pll[pll_index + 1:])
                        if res:
                            sc_matched = True
                    if not sc_matched:
                        return False
                pll_index += 1
            return True

        return match(s, pll)


class Solution20:
    def patternMatching(self, pattern: str, value: str) -> bool:
        if pattern == '':
            return True
        pattern = list(pattern)
        len_s = len(value)
        import collections
        pdic = collections.Counter(pattern)
        a_num, b_num = pdic['a'], pdic['b']

        # a,b 为空字符串情形
        if a_num!=0:
            if len_s % a_num == 0:
                len_word = int(len_s / a_num)
                base = value[:len_word]
                matched = True
                for i in range(a_num):
                    if value[i * len_word:(i + 1) * len_word] != base:
                        matched = False
                        break
                if matched:
                    return True
        elif a_num == 0 :
            if len_s % b_num != 0:
                return False
            else:
                s=''
                for i in range(b_num):
                   s += value[:int(len_s / b_num)]
                if value != s:
                    return False
                else: return True

        if b_num != 0 :
            if len_s % b_num == 0:
                len_word = int(len_s / b_num)
                base = value[:len_word]
                matched = True
                for i in range(b_num):
                    if value[i * len_word:(i + 1) * len_word] != base:
                        matched = False
                        break
                if matched:
                    return True
        elif b_num == 0 :
            if len_s % a_num != 0:
                return False
            else:
                s=''
                for i in range(a_num):
                   s += value[:int(len_s / a_num)]
                if value != s:
                    return False
                else: return True
        # 一般情形
        max_a_len = int((len_s - b_num * 1) / a_num)
        for a_len in range(max_a_len, 0, -1):
            if (len_s - (a_len * a_num)) % b_num != 0:
                continue
            b_len = int((len_s - (a_len * a_num)) / b_num)
            a_word = ''
            b_word = ''
            cursor = 0
            matched = True
            for p in pattern:
                if p == 'a':
                    a_word = value[cursor:cursor+a_len] if a_word == '' else a_word
                    if value[cursor:cursor+a_len] != a_word:
                        matched = False
                        break
                    cursor += a_len
                elif p == 'b':
                    b_word = value[cursor:cursor+b_len] if b_word == '' else b_word
                    if value[cursor:cursor+b_len] != b_word:
                        matched = False
                        break
                    cursor += b_len
            if matched:
                return True
        return False

if __name__ == "__main__":
    from db.dev.leetcode import Solution20
    import itertools

    pattern = "abba"
    value = "dogdogdogdog"
    res = Solution20().patternMatching(pattern, value)
    print(res)
