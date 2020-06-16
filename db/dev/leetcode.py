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
                min_index.append(index + 1 )

        return min_index
    def longestCommonPrefix(self, strs: List[str]) -> str:
        if len(strs) == 0:
            return ''
        res = ''
        min_index = self.find_min(strs)[0]
        min_str = strs[min_index]
        for char_index,char in enumerate(min_str):
            for item in strs:
                if item[char_index] != char:
                    return res
            res = res + char
        return res

if __name__ == "__main__":
    nums = [-1, 0, 1, 2, -1, -4]
    nums = [1, 2, -2, -1]
    nums = [-1, 0, 1, 2, -1, -4]
    nums = [3, 0, -2, -1, 1, 2]
    nums = [-4, -2, 1, -5, -4, -4, 4, -2, 0, 4, 0, -2, 3, 1, -5, 0]
    from db.dev.leetcode import Solution9

    x = Solution9().longestCommonPrefix(["dog","racecar","car"])
    print(x)
