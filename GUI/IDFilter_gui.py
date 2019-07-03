# TODO(Chenyin): check for corner cases; set up proper check standard
import time
import pandas as pd
import os
import sys
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)
import ralib.helper
import ralib.time
import ralib.mkfile

current_path = ''
num_of_region = 0   # 《门店分组表》同龄人，区域种数
num_of_region2 = 0  # 《员工信息表》有效区域种数
num_of_store = 0    # 《门店分组表》同龄人，门店种数
num_of_store2 = 0   # 《员工信息表》有效门店种数
num_of_worker = 0   # 《员工信息表》所需门店技师总数
worker_by_group = [{}, {}, {}, {}]  # 用于数据统计


# 预处理excel文件
# path1: 《门店分组表》路径
# path2: 《员工信息表》路径
def readfile(path1: str, path2: str) -> pd.DataFrame:
    # step 1: excel转换成df
    df1 = pd.read_excel(path1)
    df2 = pd.read_excel(path2)

    # 所有nan值转换为'-'
    df1.fillna('-', inplace=True)
    df2.fillna('-', inplace=True)

    # step 2: df1初步操作
    df1[["组别", "门店名称", "所属区域"]] = df1[["组别", "门店名称", "所属区域"]].\
        applymap(ralib.helper.rm_space)  # 去除元素首尾空格
    df11 = df1[df1["组别"] == "同龄人现在"]        # 选择同龄人组
    df11 = df11[["门店名称", "所属区域"]]
    df11.reset_index(drop=True, inplace=True)
    # TODO(Chenyin): make the assignment below more suitable
    df11.iloc[7]["门店名称"] = "呼市海亮店"         # 若《门店分组表》更新，检查门店名称命名问题

    # 区域个数（非重复）和门店个数
    global num_of_region, num_of_store
    num_of_region, num_of_store = len(df11["所属区域"].unique()), len(df11["门店名称"])

    # TODO(Chenyin): 添加维护表信息
    # step 3: df2初步操作
    # 去除元素首尾空格
    df2[["二级部门", "部门", "岗位名称", "入职日期"]] = df2[["二级部门", "部门", "岗位名称", "入职日期"]].\
        applymap(ralib.helper.rm_space)
    df22 = df2[df2["岗位名称"].isin(["SPA师", "理疗师", "专家"])]       # 筛选出技师
    df22 = df22[["二级部门", "部门", "员工号", "岗位名称", "入职日期"]]
    df22.reset_index(drop=True, inplace=True)

    # step 4: df2保留选定门店
    df22["区域部门"] = df22["二级部门"] + df22["部门"]
    df11["区域部门"] = df11["所属区域"] + "区域" + df11["门店名称"]
    df222 = df22[df22["区域部门"].isin(df11["区域部门"])]
    df222.reset_index(drop=True, inplace=True)

    # step 5: 插入新变量“群体”
    df222a = df222.copy()            # avoid SettingWithCopyWarning
    df222a["群体"] = df222a["入职日期"].map(ralib.time.peer_group)
    df2222 = df222a[df222a["群体"].isin([1, 2, 3, 4])]
    global num_of_worker, num_of_region2, num_of_store2
    num_of_worker = df2222.shape[0]  # 最终被推送员工总人数
    num_of_region2 = len(df2222["二级部门"].unique())
    num_of_store2 = len(df2222["部门"].unique())
    return df2222


# step 6b: 在当前目录生成文件夹，并生成csv。data_frame必须为df2的最终版
def write_csv(data_frame: pd.DataFrame):
    region = data_frame["二级部门"].unique()
    group_name = ["0-3组", "4-6组", "7-12组", "12plus"]
    global current_path
    current_path = os.getcwd() + os.sep + "csv-files-" + time.strftime("%Y%m%d%H%M%S")
    current_path = ralib.mkfile.convert_path(current_path)
    ralib.mkfile.mkdir(current_path)
    global worker_by_group
    for r in region:
        dir_path = current_path + os.sep + r
        dir_path = ralib.mkfile.convert_path(dir_path)
        ralib.mkfile.mkdir(dir_path)
        for g in range(4):
            result = data_frame[(data_frame["二级部门"] == r) & (data_frame["群体"] == g+1)][["员工号"]]
            worker_by_group[g][r] = len(result)
            csv_path = dir_path + os.sep + r + group_name[g] + ".csv"
            csv_path = ralib.mkfile.convert_path(csv_path)
            result.T.to_csv(csv_path, index=False, header=0)


def statistics():
    stat = pd.DataFrame(worker_by_group)
    stat["按组求和"] = stat.apply(lambda x: x.sum(), axis=1)
    stat.loc["按区域求和"] = stat.apply(lambda x: x.sum())
    stat.index = ["0-3个月", "4-6个月", "7-12个月", "1年以上", "按区域求和"]
    file_path = current_path + os.sep + "summary.xlsx"
    file_path = ralib.mkfile.convert_path(file_path)
    stat.to_excel(file_path)
    print("筛选完成！描述文件summary和被推送人员名单已存至 " + current_path)
    print("数据统计:")
    print("《门店分组表》有效区域{}个，门店{}家".format(num_of_region, num_of_store))
    print("《员工信息表》有效区域{}个，门店{}家，技师{}人".format(num_of_region2, num_of_store2, num_of_worker))


def main():
    print("开始筛选，请稍等...")
    df = readfile(sys.argv[1], sys.argv[2])
    write_csv(df)
    statistics()


if __name__ == "__main__":
    main()
