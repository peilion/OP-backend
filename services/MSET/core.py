import numpy as np

step = 2
delta = 0.001
z = 4


def memory_mat_train(np_D):
    memory_mat = np.zeros((1, np_D.shape[1]))
    for i in range(np_D.shape[1]):
        for k in range(step):
            for j in range(np_D.shape[0]):
                if np.abs(np_D[j, i] - k * (1 / step)) < delta:
                    memory_mat = np.vstack(
                        (memory_mat, np.expand_dims(np_D[j], 0))
                    )  # 添加向量至记忆矩阵
                    break
    memory_mat = memory_mat[1:, :]
    # memory_mat = np.delete(memory_mat, 0, axis=0)
    print("memory_mat:", memory_mat.shape)
    # np.save(memorymat_name, memory_mat)
    return memory_mat


def Temp_MemMat(memorymat):
    memorymat_row = memorymat.shape[0]
    Temp = np.zeros((memorymat_row, memorymat_row))
    for i in range(memorymat_row):
        for j in range(memorymat_row):
            Temp[i, j] = np.linalg.norm(memorymat[i] - memorymat[j])
    return Temp
    # np.save(Temp_name, Temp)


def mset_estimate(memorymat, Kobs, Temp):  # Temp为临时计算的矩阵
    memorymat_row = memorymat.shape[0]
    Kobs_row = Kobs.shape[0]
    Temp1 = np.zeros((memorymat_row, Kobs_row))
    for m in range(memorymat_row):
        for n in range(Kobs_row):
            Temp1[m, n] = np.linalg.norm(memorymat[m] - Kobs[n])
    Kest = np.dot(np.dot(memorymat.T, (np.linalg.pinv(Temp))), Temp1)
    Kest = Kest.T
    return Kest


def calculate_similarity(Kobs, Kest):
    dist_norm = np.zeros((Kobs.shape[0], 1))
    dist_cos = np.zeros((Kobs.shape[0], 1))
    for i in range(Kobs.shape[0]):
        dist_norm[i] = np.linalg.norm(Kobs[i, :] - Kest[i, :])  # 欧式距离
        dist_cos[i] = np.dot(Kobs[i, :], Kest[i, :]) / (
            np.linalg.norm(Kobs[i, :]) * np.linalg.norm(Kest[i, :])
        )  # dot向量内积，norm向量二范数
    dist_cos = dist_cos * 0.5 + 0.5  # 余弦距离平移至[0,1]
    sim = 1 / (1 + dist_norm / dist_cos)  # 相似度公式
    return sim


# 根据区间统计的思想确定动态阈值
def threshold_caculate(sim):
    mu = np.zeros((sim.shape[0], 1))
    sigma = np.zeros((sim.shape[0], 1))
    index = np.empty((1,), dtype=np.int)
    for i in range(sim.shape[0]):
        if i == 0:
            mu[i] = sim[i]
        else:
            # 相似度大于动态阈值且大于0.8，更新动态阈值
            if sim[i - 1] >= (mu[i - 1] - z * sigma[i - 1]) and sim[i - 1] >= 0.8:
                mu[i] = 1 / (i + 1) * sim[i] + i / (i + 1) * sim[i - 1]
                sigma[i] = np.sqrt(
                    (i - 1) / i * (sigma[i - 1] ** 2)
                    + ((sim[i] - mu[i - 1]) ** 2 / (i + 1))
                )
            # 相似度小于动态阈值或相似度大于动态阈值且小于0.8，不更新
            elif sim[i - 1] < (mu[i - 1] - z * sigma[i - 1]) or (
                sim[i - 1] >= (mu[i - 1] - z * sigma[i - 1]) and sim[i - 1] < 0.8
            ):
                mu[i] = mu[i - 1]
                sigma[i] = sigma[i - 1]
                index = np.append(index, i)
    index = np.delete(index, 0)
    thres = mu - z * sigma
    return thres, index
