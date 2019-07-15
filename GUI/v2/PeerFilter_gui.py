# TODO(Chenyin): 统一变量名称；检查临界点；添加维护表信息；总表部分员工缺少id信息；判断rehire员工；
#  员工如何借取；中间1/3人数标准；设定检查标准
import pandas as pd
import datetime
import time
from time import sleep
from tqdm import tqdm
import os
import sys
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)
import ralib.helper
import ralib.time
import ralib.mkfile

dir_path = ""                            # directory path
region = []                              # list of regions
num_of_workers = [{}, {}, {}, {}, {}]    # list of dictionary {region: number of workers},
# each dic represents for a group


# STEP 1 & 2 & 3
def preprocess_files(path1: str, path2: str, path3: str) -> list:
    """
    Transfer the excel files to DataFrames, and preprocess them.

    :param path1: 上月业绩表《X月汇总》path
    :param path2: 员工信息表《员工信息表》path
    :param path3: 总数据库《总表》path
    :return: list of processed DataFrames
    """
    df_list = []
    df_perform = pd.read_excel(path1)
    df_info = pd.read_excel(path2)
    df_database = pd.read_excel(path3)

    # pre-process df_perform
    # keep variables of the interest
    df_perform = pd.DataFrame(df_perform, columns=["店名", "工号", "岗位", "姓名", "点号合计", "销售业绩"])
    df_perform.fillna({"店名": '-', "岗位": '-', "姓名": '-'}, inplace=True)
    df_perform[["店名", "岗位", "姓名"]] = df_perform[["店名", "岗位", "姓名"]].applymap(ralib.helper.rm_space)
    df_perform = df_perform[df_perform["岗位"].isin(["SPA师", "理疗师", "专家"])]
    df_perform.reset_index(drop=True, inplace=True)
    df_perform = df_perform.rename(columns={"店名": "部门"})

    # df_info 待修改为维护表内容, 先进行维护表更新函数，再进行后续操作
    # pre-process df_info
    df_info = pd.DataFrame(df_info, columns=["二级部门", "部门", "员工号", "岗位名称", "姓名", "入职日期"])
    df_info.fillna({"二级部门": '-', "部门": '-', "岗位名称": '-', "姓名": '-', "入职日期": '-'}, inplace=True)
    df_info["入职日期"] = df_info["入职日期"].map(ralib.time.to_date)
    df_info[["二级部门", "部门", "岗位名称", "姓名", "入职日期"]] = \
        df_info[["二级部门", "部门", "岗位名称", "姓名", "入职日期"]].applymap(ralib.helper.rm_space)
    df_info = df_info[df_info["岗位名称"].isin(["SPA师", "理疗师", "专家"])]
    df_info.reset_index(drop=True, inplace=True)
    df_info = df_info.rename(columns={"二级部门": "区域", "员工号": "工号", "岗位名称": "岗位"})

    # pre-process df_database
    df_database = pd.DataFrame(df_database, columns=["工号", "姓名", "岗位", "入职日期", "出勤", "点号合计", "销售业绩",
                                                     "工资年月", "部门", "区域", "最早的入职日期", "最近的入职日期"])
    df_database.fillna({"姓名": '-', "岗位": '-', "部门": '-', "区域": '-', "入职日期": '-',
                        "工资年月": '-', "最早的入职日期": '-', "最近的入职日期": '-'}, inplace=True)
    df_database["入职日期"] = df_database["入职日期"].map(ralib.time.to_date)
    df_database["工资年月"] = df_database["工资年月"].map(ralib.time.to_date)
    df_database["最早的入职日期"] = df_database["最早的入职日期"].map(ralib.time.to_date)
    df_database["最近的入职日期"] = df_database["最近的入职日期"].map(ralib.time.to_date)
    df_database[["姓名", "岗位", "部门", "区域", "入职日期", "工资年月", "最早的入职日期", "最近的入职日期"]] \
        = df_database[["姓名", "岗位", "部门", "区域", "入职日期", "工资年月", "最早的入职日期", "最近的入职日期"]].\
        applymap(ralib.helper.rm_space)
    # 总表中每个员工包含多个observation，可能这个员工从技师变为其他工种，之前的筛选方法就不对了: 应该取反~
    not_in_id = df_database[~df_database["岗位"].isin(["SPA师", "理疗师", "专家"])]["工号"]
    df_database = df_database[~df_database["工号"].isin(not_in_id)]
    df_database.reset_index(drop=True, inplace=True)
    # 补全id为空值的信息

    # process df_perform
    # based on df_info, insert two new columns "入职日期", "区域" for df_perform
    # 【此处待修改】维护表完成后，df_perform所需的"入职日期"、"区域"从维护表中生成，不再需要员工信息表df_info的内容，因为
    # 员工信息表的内容在维护表更新时就载入了
    df_perform = pd.merge(df_perform, df_info, on="工号", how="inner")
    df_perform = df_perform.drop(["部门_x", "岗位_x", "姓名_x"], axis=1)
    df_perform = df_perform.rename(columns={"姓名_y": "姓名", "部门_y": "部门", "岗位_y": "岗位"})
    # exist single worker with more than one rows of information, thus need to modify them
    df_perform = df_perform.drop_duplicates()                               # delete duplicated rows
    df_perform = df_perform.groupby("工号")[["点号合计", "销售业绩"]].sum()  # sum the worker's performance
    df_perform.reset_index(drop=False, inplace=True)
    df_perform = pd.merge(df_perform, df_info, on="工号", how="inner")

    # update 入职日期
    id_and = set(df_perform["工号"]).intersection(set(df_database["工号"]))
    for i in range(len(df_perform)):
        id_num = df_perform.loc[i, "工号"]
        if id_num in id_and:
            s = df_database[df_database["工号"] == id_num]["最早的入职日期"].iloc[0]
            if (s != '-') and (s is not pd.NaT):
                df_perform.loc[i, "入职日期"] = s

    # generate random numbers for the workers in df_perform
    df_perform["随机数"] = ralib.helper.sample_floats(0, 1, len(df_perform))
    global region
    region = df_perform["区域"].unique()
    df_list.append(df_perform)
    df_list.append(df_database)
    return df_list


# LEVEL 1
def peer_to_excel(df_perform: pd.DataFrame):
    """
    Filter the peer group's information, and store it to excel files.

    :param df_perform: DataFrame that stores the worker performance information
    """
    df_copy = df_perform.copy()
    # group workers
    df_copy["群体"] = df_copy["入职日期"].map(ralib.time.peer_group)
    df_copy = df_copy[df_copy["群体"].isin([1, 2, 3, 4])]  # ignore '-'
    # start to write files
    global dir_path
    dir_path = (os.getcwd() + os.sep + str(ralib.time.last_day(datetime.date.today(), 1).month)
                + "月筛选人员-" + time.strftime("%Y%m%d%H%M%S"))
    dir_path = ralib.mkfile.convert_path(dir_path)
    ralib.mkfile.mkdir(dir_path)
    group_name = ["0-3个月", "4-6个月", "7-12个月", "1年以上"]
    print("写入同龄人组数据:")
    global num_of_workers
    for r in tqdm(region):
        # group 1-3: 理疗师 first, then SPA师+专家
        file_path = dir_path + os.sep + r + ".xlsx"
        file_path = ralib.mkfile.convert_path(file_path)
        writer = pd.ExcelWriter(file_path)
        for g in range(3):
            df = df_copy[(df_copy["区域"] == r) & (df_copy["群体"] == (g + 1))]
            df1 = df[df["岗位"] == "理疗师"]
            df2 = df[(df["岗位"] == "SPA师") | (df["岗位"] == "专家")]
            # sort by performance: descending
            df1 = df1.sort_values(by="销售业绩", ascending=False)
            df1.reset_index(drop=True, inplace=True)
            df2 = df2.sort_values(by="销售业绩", ascending=False)
            df2.reset_index(drop=True, inplace=True)

            # select middle 1/3 individuals. If too small, select of all them
            cutoff1 = len(df1) // 3
            cutoff2 = len(df2) // 3
            if cutoff1 >= 3:
                df1_selected = df1[cutoff1: cutoff1 * 2 + 2]  # workers >= 5
            else:
                df1_selected = df1
            if cutoff2 >= 6:
                df2_selected = df2[cutoff2: cutoff2 * 2 + 4]  # workers >= 10
            else:
                df2_selected = df2
            df1_selected.reset_index(drop=True, inplace=True)
            df2_selected.reset_index(drop=True, inplace=True)
            # 理疗师: first 5 workers，SPA师+专家: first 10 workers
            # corner case: not enough, stealing from siblings
            df1_selected = df1_selected[:5]
            df2_selected = df2_selected[:10]
            len1 = len(df1_selected)
            len2 = len(df2_selected)
            # difference list
            df1_unselected_id = set(df1["工号"]).difference(set(df1_selected["工号"]))
            df2_unselected_id = set(df2["工号"]).difference(set(df2_selected["工号"]))
            # stealing
            if (len1 < 5) and (len(df2_unselected_id) > 0):
                n = 5 - len1
                # if n > len(df2_unselected_id), iloc func can still work, and choose full range
                df1_selected = pd.concat([df1_selected, df2[df2["工号"].isin(df2_unselected_id)].
                                         sort_values(by="随机数").
                                         iloc[:n]], ignore_index=True)
            elif (len(df1_unselected_id) > 0) and (len2 < 10):
                n = 10 - len2
                df2_selected = pd.concat([df2_selected, df1[df1["工号"].isin(df1_unselected_id)].
                                         sort_values(by="随机数").
                                         iloc[:n]], ignore_index=True)
            # merge, sort by descending random numbers
            df_result = pd.concat([df1_selected, df2_selected], ignore_index=True)
            df_result = df_result.sort_values(by="随机数", ascending=False)
            df_result = df_result.reindex(["工号", "岗位", "姓名", "点号合计", "销售业绩",
                                           "区域", "部门", "入职日期", "随机数", "群体"], axis=1)
            num_of_workers[g][r] = len(df_result)
            df_result.to_excel(writer, sheet_name=group_name[g], index=None)

        # group 4
        df = df_copy[(df_copy["区域"] == r) & (df_copy["群体"] == 4)]
        df = df[(df["岗位"] == "理疗师") | (df["岗位"] == "SPA师") | (df["岗位"] == "专家")]
        # sort by performance: descending
        df = df.sort_values(by="销售业绩", ascending=False)
        df.reset_index(drop=True, inplace=True)
        # select middle 1/3
        cutoff = len(df) // 3
        if cutoff >= 9:
            df = df[cutoff: cutoff * 2 + 6]  # workers >= 15
        # select first 15 workers
        df = df[:15]
        df.reset_index(drop=True, inplace=True)
        # sort by descending random numbers
        df = df.sort_values(by="随机数", ascending=False)
        df = df.reindex(["工号", "岗位", "姓名", "点号合计",
                         "销售业绩", "区域", "部门", "入职日期", "随机数", "群体"], axis=1)
        num_of_workers[3][r] = len(df)
        df.to_excel(writer, sheet_name=group_name[3], index=None)
        writer.save()
        writer.close()
        sleep(0.1)


# LEVEL 2
def senior_to_excel(df_perform: pd.DataFrame, df_database: pd.DataFrame):
    """
    Filter the senior group's information, and store it to excel files.

    :param df_perform:  DataFrame that stores the worker performance information
    :param df_database: DataFrame that stores the database information
    """
    df_perform_copy = df_perform.copy()
    df_database_copy = df_database.copy()
    # group senior workers
    print("写入老人组数据:")
    for r in tqdm(region):
        df_by_region = df_perform_copy[df_perform_copy["区域"] == r]
        # sort workers by performance, and select the first half of them
        df_by_region = df_by_region.sort_values(by="销售业绩", ascending=False)
        df_by_region.reset_index(drop=True, inplace=True)
        # ??? corner case
        cutoff = len(df_by_region) // 2
        if cutoff >= 15:
            df_by_region = df_by_region[:cutoff]
        # group the seniors in DataFrame that stores worker performance
        df_senior_id = df_by_region[df_by_region["入职日期"].map(ralib.time.is_senior)]
        df_senior_id.reset_index(drop=True, inplace=True)

        # "老人组long" sheet
        # select senior workers from df_database based on df_senior_id
        df_senior_long = df_database_copy[df_database_copy["工号"].isin(df_senior_id["工号"])]
        df_senior_long = df_senior_long.sort_values(by="工号")
        df_senior_long.reset_index(drop=True, inplace=True)
        # compute the duration of work time: n
        # ??? corner case: rehire/more than one employment date
        df_senior_long["第n月工作"] = df_senior_long.\
            apply(lambda row: ralib.time.month_delta(row["最早的入职日期"], row["工资年月"]), axis=1)
        df_senior_long = df_senior_long.reindex(["工号", "姓名", "区域", "部门", "岗位", "出勤", "点号合计", "销售业绩",
                                                 "工资年月", "最早的入职日期", "第n月工作"], axis=1)
        df_senior_long.reset_index(drop=True, inplace=True)
        # generate random floats
        unique_id_list = df_senior_long["工号"].unique()
        df_id_rand = pd.DataFrame([unique_id_list, ralib.helper.sample_floats(0, 1, len(unique_id_list))],
                                  index=["工号", "随机数"]).T
        df_id_15 = df_id_rand.sort_values("随机数", ascending=False)[:15]
        df_id_15.reset_index(drop=True, inplace=True)
        # merge to add random float column into df_senior
        df_senior_long = pd.merge(df_senior_long, df_id_15, on="工号", how="inner")
        # sort "第n月工作" by n from lowest to highest
        df_senior_long = df_senior_long.groupby("随机数").apply(lambda x: x.sort_values("第n月工作"))
        df_senior_long.reset_index(drop=True, inplace=True)
        # sort by random floats, using merge sort to keep it stable
        df_senior_long = df_senior_long.sort_values(by="随机数", kind="mergesort", ascending=False)
        df_senior_long.reset_index(drop=True, inplace=True)

        # "老人组" sheet
        df_senior = df_senior_id.drop("随机数", axis=1)
        df_senior = pd.merge(df_senior, df_id_15, on="工号", how="inner")
        df_senior.sort_values("随机数", ascending=False, inplace=True)
        df_senior = df_senior.reindex(["工号", "岗位", "姓名", "点号合计", "销售业绩",
                                       "区域", "部门", "入职日期", "随机数"], axis=1)
        df_senior.reset_index(drop=True, inplace=True)
        num_of_workers[4][r] = len(df_senior)

        # 老人组long最近工资月份缺少销售业绩，从老人组数据补充
        for i in range(len(df_senior_long)):
            id_num = df_senior_long.loc[i, "工号"]
            salary_date = df_senior_long.loc[i, "工资年月"]
            recent_day = ralib.time.last_day(datetime.date.today(), 1)  # 2nd argument should be 1
            if ralib.time.same_month(salary_date, str(recent_day)):
                df_senior_long.loc[i, "销售业绩"] = df_senior[df_senior["工号"] == id_num]["销售业绩"].iloc[0]
                df_senior_long.loc[i, "点号合计"] = df_senior[df_senior["工号"] == id_num]["点号合计"].iloc[0]
                df_senior_long.loc[i, "部门"] = df_senior[df_senior["工号"] == id_num]["部门"].iloc[0]

        # write sheets
        file_path = dir_path + os.sep + r + ".xlsx"
        file_path = ralib.mkfile.convert_path(file_path)
        ralib.mkfile.to_existing_excel(df_senior, file_path, "老人组")
        ralib.mkfile.to_existing_excel(df_senior_long, file_path, "老人组long")
        sleep(0.1)


def statistics():
    """
    Returns statistics summary.
    :return: statistics summary
    """
    stat = pd.DataFrame(num_of_workers)
    stat.index = ["0-3个月", "4-6个月", "7-12个月", "1年以上", "老人组"]
    file_path = dir_path + os.sep + "summary.xlsx"
    file_path = ralib.mkfile.convert_path(file_path)
    stat.to_excel(file_path)
    print("筛选完成！描述文件summary和推送人员名单已存至 " + dir_path)


def main():
    print("文件读取中，请稍等...")
    perform, database = preprocess_files(sys.argv[1], sys.argv[2], sys.argv[3])
    peer_to_excel(perform)
    senior_to_excel(perform, database)
    statistics()


if __name__ == "__main__":
    main()


