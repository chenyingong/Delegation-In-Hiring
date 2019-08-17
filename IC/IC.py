import pandas as pd
import numpy as np
import datetime
import os
import sys
import time
from time import sleep
from tqdm import tqdm
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)
import ralib.helper
import ralib.mkfile
import ralib.time
from ralib.constant import Const


current_path = ''
first_sen_peer = [
    "为了增进良子人之间的相互了解，今天我们向您介绍{}（化名）的工作业绩。",
    "在良子，有很多人像您一样在为公司和自己的未来努力。今天我们向您介绍{}（化名）的工作业绩。",
    "您是否知道，有很多和您经历相近的良子人也在和您一样努力工作。今天我们向您介绍{}（化名）的工作业绩。",
    "您在努力工作的同时，是否关注到身边的良子人也在努力进步？今天我们向您介绍{}（化名）的工作业绩。"
]
middle_sen_peer = [
    "{}{}年{}月加入{}，目前是一名{}。上个月{}的点号数是{}，销售业绩是{}元。",
    "{}{}年{}月加入{}，目前是一名{}。{}年{}月{}的点号数是{}，销售业绩是{}元。"
]
first_sen_senior = [
    "为了增进良子人之间的相互了解，今天我们向您介绍{}（化名）在良子的成长历程。",
    "很多技艺精湛、业绩突出的老员工也经历了一步一个脚印的学习过程。今天我们向您介绍{}（化名）在良子的成长历程。",
    "华夏良子大家庭有很多优秀的老员工。大家看到的往往是老员工现在的优秀，看不到的是他们长时间默默努力进步的过程。今天我们向您介绍{}（化名）在良子的成长历程。"
]
middle_sen_senior = "{}{}年{}月加入{}，目前是一名{}。入职第一个月，{}的点号数是{}，销售业绩是{}。此后，{}在工作中取得了{}的成绩。"
end_sen_senior = [
    "*入职后第{}个月，{}的点号是{}，销售业绩是{}。",
    "*上个月，{}的点号达到了{}，销售业绩是{}。",
    "*{}年{}月，{}的点号达到了{}，销售业绩是{}。"
]
profession = ["理疗师", "spa师", "专家"]
gender = ["她", "他"]
days = ["星期三", "星期六"]
names_male = [
    "小云",
    "小杜",
    "小文",
    "小安",
    "小凡",
    "小平",
    "小聪",
    "小叶",
    "小李",
    "小淇",
    "小建",
    "小龙",
    "小陆",
    "小涛",
    "小白",
    "小阳",
    "小刚",
    "小军",
    "小华",
    "小鹏"
]
names_female = [
    "小羽",
    "小李",
    "小梅",
    "小南",
    "小静",
    "小冰",
    "小琳",
    "小杨",
    "小美",
    "小冉",
    "小婷",
    "小雪",
    "小燕",
    "小琴",
    "小莹",
    "小雅",
    "小娟",
    "小娜",
    "小张",
    "小妍"
]
const = Const()
const.DELTA_3 = datetime.timedelta(days=3)
const.DELTA_4 = datetime.timedelta(days=4)
const.DELTA_7 = datetime.timedelta(days=7)


# peers
def peer_sentence(df_peer: pd.DataFrame, sdate: datetime.date, region_name: str) -> str:
    """
    Convert peer group data to IC sentence.
    :param df_peer: DataFrame object of peer group data
    :param sdate: start date of IC
    :param region_name: region name
    :return: IC sentence
    """
    start_weekday = sdate.weekday()
    if start_weekday != 2 and start_weekday != 5:
        if start_weekday != 7:
            cn_weekday = "星期" + str(start_weekday+1)
        else:
            cn_weekday = "星期1"
        raise ValueError("输入时间为：{}-{}，推送起始时间必须为星期3或者星期6".format(sdate, cn_weekday))
    valid_df = df_peer.copy()
    this_month = sdate.month
    result = ralib.helper.sample_int(0, len(names_male), len(valid_df))
    sentence_peer = ''
    for i in range(len(valid_df)):
        # 岗位
        position = valid_df.iloc[i]["岗位"]
        # 区域
        # region = valid_df.iloc[i]["区域"]
        region = region_name
        # 入职日期
        employ_date = str(valid_df.iloc[i]["入职日期"])
        # 点号、销售
        num1 = valid_df.iloc[i]["点号合计"]
        num2 = valid_df.iloc[i]["销售业绩"]
        year = int(employ_date.split('-')[0])
        month = int(employ_date.split('-')[1])
        k = i % len(days)
        gender_index = np.random.randint(0, 2)
        if gender_index == 0:
            name1 = names_female[result[i]]
        else:
            name1 = names_male[result[i]]
        if start_weekday == 2:
            ic_date = sdate + k * const.DELTA_3 + i // 2 * const.DELTA_7
            ic_week = days[k]
        else:
            ic_date = sdate + k * const.DELTA_4 + i // 2 * const.DELTA_7
            ic_week = days[k - 1]
        ic_year = ic_date.year
        ic_month = ic_date.month
        ic_day = ic_date.day
        sentence0 = ic_week + "({}月{}日)".format(ic_month, ic_day) + "\n"
        sentence1 = first_sen_peer[i % len(first_sen_peer)].format(name1)
        if ic_month == this_month:
            sentence2 = middle_sen_peer[0].format(name1, year, month, region, position, name1, num1, num2) + "\n"
        else:
            if this_month == 1:
                ic_year -= 1
                ic_month = 12
            else:
                ic_month = this_month - 1
            sentence2 = middle_sen_peer[1].format(name1, year, month, region, position, ic_year, ic_month, name1, num1,
                                                  num2) + "\n"
        # this_month-1 需要修改
        sentence_peer += sentence0 + sentence1 + sentence2 + "\n"
    return sentence_peer


# senior
def senior_sentence(df_senior: pd.DataFrame, sdate: datetime.date, region_name: str) -> str:
    """
    Convert peer group data to IC sentence.
    :param df_senior: DataFrame object of peer group data
    :param sdate: start date of IC
    :param region_name: region name
    :return: IC sentence
    """
    start_weekday = sdate.weekday()
    if start_weekday != 2 and start_weekday != 5:
        if start_weekday != 7:
            cn_weekday = "星期" + str(start_weekday + 1)
        else:
            cn_weekday = "星期1"
        raise ValueError("输入时间为：{}-{}，推送起始时间必须为星期3或者星期6".format(sdate, cn_weekday))
    valid_df = df_senior.copy()
    senior_list = list(valid_df["工号"])
    senior = list(set(senior_list))
    senior.sort(key=senior_list.index)
    this_month = sdate.month
    result = ralib.helper.sample_int(0, len(names_male), len(senior))
    sentence_senior = ''
    i = 0
    for ID in senior:
        latest_info = valid_df[valid_df["工号"] == ID].iloc[-1]
        # 上个月是第n月工作？
        latest_n = latest_info["第n月工作"]
        # 岗位
        position = latest_info["岗位"]
        # 区域
        # region = latest_info["区域"]
        region = region_name
        # 入职日期
        employ_date = str(latest_info["最早的入职日期"])
        # 上月点号、销售
        num1 = latest_info["点号合计"]
        num2 = latest_info["销售业绩"]
        year = int(employ_date.split('-')[0])
        month = int(employ_date.split('-')[1])
        gender_index = np.random.randint(0, 2)
        gender1 = gender[gender_index]
        if gender1 == "她":
            name1 = names_female[result[i]]
        else:
            name1 = names_male[result[i]]
        # progress1 = progress[i%len(progress)]
        k = i % len(days)
        if start_weekday == 2:
            ic_date = sdate + k * const.DELTA_3 + i // 2 * const.DELTA_7
            ic_week = days[k]
        else:
            ic_date = sdate + k * const.DELTA_4 + i // 2 * const.DELTA_7
            ic_week = days[k - 1]
        ic_year = ic_date.year
        ic_month = ic_date.month
        ic_day = ic_date.day
        sentence0 = ic_week + "({}月{}日)".format(ic_month, ic_day) + "\n"
        sentence1 = first_sen_senior[i % len(first_sen_senior)].format(name1)
        this_df = valid_df[valid_df["工号"] == ID]
        progress1 = this_df.iloc[0]["评价"]
        temp = this_df[this_df["第n月工作"] == 1]
        sentence2 = '\n'
        if len(temp) != 0:
            num10 = temp.iloc[0]["点号合计"]
            num20 = temp.iloc[0]["销售业绩"]
            sentence2 = middle_sen_senior.format(name1, year, month, region, position, gender1, num10, num20, gender1,
                                                 progress1) + "\n"
        sentence3 = ''
        n = 3
        for l in range(3):
            temp = this_df[this_df["第n月工作"] == n]
            if len(temp) == 0:
                continue
            num11 = temp.iloc[0]["点号合计"]
            num22 = temp.iloc[0]["销售业绩"]
            if n == latest_n:
                break
            sentence3 += end_sen_senior[0].format(n, gender1, num11, num22) + "\n"
            n *= 2
        if ic_month == this_month:
            sentence3 += end_sen_senior[1].format(gender1, num1, num2) + "\n"
        else:
            sentence3 += end_sen_senior[2].format(ic_year, this_month - 1, gender1, num1, num2) + "\n"
        sentence_senior += sentence0 + sentence1 + sentence2 + sentence3 + "\n"
        i += 1
    return sentence_senior


# write to txt
def rw_to_txt(from_path: str, sdate: str):
    """
    Read and write IC sentences to txt files.
    :param from_path: input directory path
    :param sdate: start date of IC
    """
    global current_path
    current_path = (os.getcwd() + os.sep + str(ralib.time.last_day(datetime.date.today(), 1).month)
                    + "月推送内容-" + time.strftime("%Y%m%d%H%M%S"))
    current_path = ralib.mkfile.convert_path(current_path)
    ralib.mkfile.mkdir(current_path)
    group_name = ["-0-3个月", "-4-6个月", "-7-12个月", "-12个月以上", "-老人推送语"]
    sdate = datetime.datetime.strptime(sdate, '%Y-%m-%d').date()
    file_list = ralib.mkfile.traverse_files(from_path, "xlsx")
    for f_path in tqdm(file_list):
        region_name = f_path.split(os.sep)[-1].split('.')[0]
        dir_path = current_path + os.sep + region_name
        dir_path = ralib.mkfile.convert_path(dir_path)
        ralib.mkfile.mkdir(dir_path)
        df = ralib.mkfile.from_existing_excel(f_path,
                                              "0-3个月", "4-6个月", "7-12个月", "1年以上", "老人组long")
        i = 0
        for d in df:
            to_path = dir_path + os.sep + region_name + group_name[i] + ".txt"
            to_path = ralib.mkfile.convert_path(to_path)
            if i == 4:
                sen = senior_sentence(d, sdate, region_name)
            else:
                sen = peer_sentence(d, sdate, region_name)
            with open(to_path, 'w') as f:
                f.write(sen)
            i += 1
        sleep(0.1)


def main():
    print("文件读取中，请稍等...")
    dir_path = sys.argv[1]
    sdate = sys.argv[2]
    rw_to_txt(dir_path, sdate)
    print("筛选完成！文件已存至 " + current_path)


if __name__ == "__main__":
    main()
