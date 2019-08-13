# TODO: 小数点没解决；"三五万"、"一万五"被省略；运行速度过慢
import re
import os
import sys
import time
import pandas as pd
import numpy as np
from time import sleep
from tqdm import tqdm
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)
import ralib.mkfile

current_path = ''
transform_rate = {
                  "文件名": [],
                  "转换率": [],
                  "转换题型": []
}


# Chinese num to arabic num
def chinese_to_arabic(cn: str) -> int:
    """
    Convert Chinese number to arabic num.
    :param cn: string type of chinese number
    :return: int type of arabic number
    """
    cn_num = {
        '〇': 0, '一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9, '零': 0,
        '壹': 1, '贰': 2, '叁': 3, '肆': 4, '伍': 5, '陆': 6, '柒': 7, '捌': 8, '玖': 9, '貮': 2, '两': 2,
    }
    cn_unit = {
        '十': 10,
        '拾': 10,
        '百': 100,
        '佰': 100,
        '千': 1000,
        '仟': 1000,
        '万': 10000,
        '萬': 10000,
        '亿': 100000000,
        '億': 100000000,
        '兆': 1000000000000,
    }
    if cn == '':
        return np.nan

    if cn[0] in cn_unit and cn[0] not in ["十", "拾"]:
        return np.nan

    if cn[-1] in cn_num and len(cn) > 1:
        for i in cn[::-1][1:]:
            if i == "零" or i == "〇":
                break
            elif i in cn_unit and i not in ["十", "拾"]:
                return np.nan
            else:
                break

    unit = 0
    ldig = []
    last_is_num = False
    last_is_unit = False
    last_letter = ''
    for cndig in reversed(cn):
        if cndig in cn_unit:
            if last_is_unit and (last_letter not in ["万", "萬", "亿", "億", "兆"]):
                return np.nan
            last_is_unit = True
            last_is_num = False
            unit = cn_unit.get(cndig)
            if unit == 10000 or unit == 100000000:
                last_letter = cndig
                ldig.append(unit)
                unit = 1
        else:
            if last_is_num and cndig not in ["零", "〇"]:
                return np.nan
            last_is_num = True
            last_is_unit = False
            dig = cn_num.get(cndig)
            if unit:
                dig *= unit
                unit = 0
            ldig.append(dig)
    if unit == 10:
        ldig.append(10)
    val, tmp = 0, 0
    for x in reversed(ldig):
        if x == 10000 or x == 100000000:
            val += tmp * x
            tmp = 0
        else:
            tmp += x
    val += tmp
    return val


# arabic num to Chinese num
def arabic_to_chinese(num: int) -> str:
    """
    Convert arabic number to Chinese number.
    :param num: int type of arabic number
    :return: string type of Chinese number
    """
    mapping = ['零', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十',
               '十一', '十二', '十三', '十四', '十五', '十六', '十七', '十八', '十九']
    p0 = ['', '十', '百', '千']
    s4 = 10 ** 4
    if num < 0 or num >= s4:
        return ''
    if num < 20:
        return mapping[num]
    else:
        lst = []
        while num >= 10:
            lst.append(num % 10)
            num = num // 10
        lst.append(num)
        c = len(lst)  # 位数
        result = ''
        for idx, val in enumerate(lst):
            val = int(val)
            if val != 0:
                result += p0[idx] + mapping[val]
                if (idx < c - 1) and (lst[idx + 1] == 0):
                    result += '零'
        return result[::-1]


# arabic + Chinese number to arabic number
def hybrid_to_arabic(hy: str):
    """
    Convert mixed arabic-Chinese number to pure arabic number
    :param hy: string type of hybrid number
    :return: int type of arabic number; '' if hy is ''
    """
    if hy == '':
        return np.nan
    elif hy.isdigit():
        if int(hy) >= 100000000000000000000:
            return np.nan
        return int(hy)
    else:
        lst = re.split(r'(\d+)', hy)
        for i, s in enumerate(lst):
            if s.isdigit() and 0 <= int(s) < 10**4:
                lst[i] = arabic_to_chinese(int(s))
            elif s.isdigit() and (int(s) < 0 or int(s) >= 10**4):
                return np.nan
        return chinese_to_arabic(''.join(lst))


# helper function for robust_clean()
def re_compile() -> list:
    valid_num = [
        '〇', '一', '二', '三', '四', '五', '六', '七', '八', '九', '零',
        '壹', '贰', '叁', '肆', '伍', '陆', '柒', '捌', '玖', '貮', '两',
        '十', '拾'
    ]
    valid_unit = [
        '百', '佰', '千', '仟', '万', '萬', '亿', '億', '兆'
    ]
    valid_char = [
        '来', '多', '几', '左', '吧', '以', '之', '内'
    ]
    re1 = '[^' + ''.join(valid_num) + ''.join(valid_unit) + '\\d]+'
    re_obj1 = re.compile(re1)
    re2a = '[0-9' + ''.join(valid_num) + ']+'
    re2b = '[^0-9' + ''.join(valid_num) + ''.join(valid_unit) + ''.join(valid_char) + '元 ]+'
    re2 = re2a + re2b
    re_obj2 = re.compile(re2)
    re3a = '[0-9' + ''.join(valid_num) + ''.join(valid_unit) + ']+'
    re3b = '[^0-9' + ''.join(valid_num) + ''.join(valid_unit) + ']+'
    re3c = '[0-9' + ''.join(valid_num) + ']+'
    re3d = '[' + ''.join(valid_unit) + ']*'
    re3 = re3a + re3b + re3c + re3d
    re_obj3 = re.compile(re3)
    return [re_obj1, re_obj2, re_obj3]


# clean dirty data to hybrid number
def robust_clean(num) -> str:
    re_obj1, re_obj2, re_obj3 = re_compile()
    # 先将num转化为str类型
    num = str(num)
    # 忽略多次出现数字字符的情形（空格也算分割点），如“1号113万”、“118. 25万”、”200 0万“、“2o万”
    if re_obj3.search(num):
        return ''
    # 忽略数字之后跟随非有效词缀的词/字，如“100号”，“一般”
    if re_obj2.search(num):
        return ''
    result = re_obj1.sub('', num)
    return result


# helper function for robust_clean_percent()
def re_compile2() -> list:
    valid_num_percent = [
        '〇', '一', '二', '三', '四', '五', '六', '七', '八', '九', '零',
        '壹', '贰', '叁', '肆', '伍', '陆', '柒', '捌', '玖', '貮', '两',
        '十', '拾'
    ]
    valid_char_percent = [
        '来', '多', '几', '左', '吧', '以', '之', '内', '%'
    ]
    re1 = '[^' + ''.join(valid_num_percent) + '\\d]+'
    re_obj1 = re.compile(re1)
    re2a = '[0-9' + ''.join(valid_num_percent) + ']+'
    re2b = '[^0-9' + ''.join(valid_num_percent) + ''.join(valid_char_percent) + ' ]+'
    re2 = re2a + re2b
    re_obj2 = re.compile(re2)
    re3a = '[百分之0-9' + ''.join(valid_num_percent) + '%]+'
    re3b = '[^百分之0-9' + ''.join(valid_num_percent) + ']+'
    re3c = '[百分之0-9' + ''.join(valid_num_percent) + ']+'
    re3 = re3a + re3b + re3c
    re_obj3 = re.compile(re3)
    return [re_obj1, re_obj2, re_obj3]


def robust_clean_percent(num) -> str:
    re_obj1, re_obj2, re_obj3 = re_compile2()
    # 先将num转化为str类型
    num = str(num)
    words_all = ["百分之百", "百分百", "百分之一百", "一百", "基本都了解",
                 "所有", "全部", "全都了解", "都知道", "全了解", "全知道"]
    words_almost = ["大多数", "大部分", "一大半", "一多半"]
    if num.find("一半") != -1:
        return '50'
    for word in words_almost:
        if num.find(word) != -1:
            return '70'
    for word in words_all:
        if num.find(word) != -1 or num == "都了解":
            return '100'
    # 忽略多次出现数字字符的情形（空格也算分割点），如“1% 80%”、“118. 25%”、”200 0%“、“2o%”
    if re_obj3.search(num):
        return ''
    # 忽略数字之后跟随非有效词缀的词/字，如“100号”，“一般”
    if re_obj2.search(num):
        return ''
    result = re_obj1.sub('', num)
    # 如果转换后的值大于100，返回空值
    if result.isdigit():
        if int(result) > 100:
            return ''
    return result


# 判断答案中是否包含“不清楚”、“不知道”等语句
def unknown(answer: str) -> bool:
    words = ["不清楚", "不太清楚", "不是很清楚", "不是太清楚",
             "不确定", "不太确定", "不是很确定", "不是太确定",
             "不了解", "不太了解", "不是很了解", "不是太了解",
             "不知道", "不太知道", "未知", "不知"]
    find = False
    for word in words:
        if answer.find(word) != -1:
            find = True
    return find


# 量化选择题答案
def quantify(answer: str) -> int:
    if answer.find("A") != -1:
        return 5
    elif answer.find("B") != -1:
        return 4
    elif answer.find("C") != -1:
        return 3
    elif answer.find("D") != -1:
        return 2
    elif answer.find("E") != -1:
        return 1
    elif answer.find("F") != -1:
        return 0
    else:
        return np.nan


def read_file(path: str):
    file_name = path.split(os.sep)[-1]
    read_df = pd.read_excel(path, sheet_name=0, header=None, skiprows=1)
    # 删除后面多余的空值列
    read_df.dropna(axis=1, how='all', inplace=True)
    # 将0、1两行的nan值填充为’‘，第1行的“问题”字符改为’‘，再将两列相加
    read_df.fillna('', inplace=True)
    row0 = read_df.iloc[0]
    row1 = read_df.iloc[1]
    row1.iloc[row1.values == '问题'] = ''
    header = row0 + row1
    # 将合并后的行作为变量名行插入
    read_df.drop([0, 1], inplace=True)
    read_df.reset_index(drop=True, inplace=True)
    read_df.columns = header
    # 判断属于哪种转换类别
    global transform_rate
    columns_name = header.values
    if "填写答案数字" in columns_name:
        transform_num(read_df, file_name)
    elif "填写答案百分数" in columns_name:
        transform_percentage(read_df, file_name)
    else:
        transform_multiple_choice(read_df, file_name)


# 处理"填写答案数字"类
def transform_num(read_df: pd.DataFrame, file_name: str):
    """
    Clean belief questions data.
    :param read_df: DataFrame object
    :param file_name: raw file name
    """
    # 获取“填写答案数字”的列索引值
    index_of_answer = -1
    index_of_answer2 = -1
    for i in range(len(read_df.columns)):
        if read_df.columns[i] == "填写答案数字":
            index_of_answer = i
        if read_df.columns[i] == "填写答案":
            index_of_answer2 = i
    read_df.insert(index_of_answer, "填写答案数字（改）",
                   read_df[["填写答案数字"]].applymap(robust_clean).applymap(hybrid_to_arabic))
    if index_of_answer2 != -1:
        if index_of_answer2 > index_of_answer:
            index_of_answer2 += 1
        read_df.insert(index_of_answer2, "填写答案（改）", read_df[["填写答案"]].applymap(quantify))
    read_df.sort_values(by="填写答案数字（改）", inplace=True)
    read_df.reset_index(drop=True, inplace=True)
    # 插入另一列，将小于100的数字改为100,000；同时添加排序标识符，用于排序
    if -1 < index_of_answer2 < index_of_answer:
        index_of_answer += 1
    read_df.insert(index_of_answer, "填写答案数字（改+）", read_df[["填写答案数字（改）"]])
    read_df['排序标识符'] = 2
    for i in range(len(read_df)):
        answer = read_df.loc[i, "填写答案数字（改）"]
        initial_answer = read_df.loc[i, "填写答案数字"]
        if not np.isnan(answer):
            read_df.loc[i, "排序标识符"] = 0
        elif unknown(initial_answer):
            read_df.loc[i, "填写答案数字（改）"] = "不确定"
            read_df.loc[i, "填写答案数字（改+）"] = "不确定"
            read_df.loc[i, "排序标识符"] = 1
        if read_df.loc[i, "排序标识符"] == 0 and answer < 100:
            read_df.loc[i, "填写答案数字（改+）"] = answer * 10000
    read_df.sort_values(by="排序标识符", kind='mergesort', inplace=True)
    read_df.reset_index(drop=True, inplace=True)
    file_path = current_path + os.sep + file_name
    read_df.to_excel(file_path)
    # 转换率
    transform_rate["文件名"].append(file_name.split('.')[0])
    transform_rate["转换率"].append(len(read_df[read_df["排序标识符"] != 2]) / len(read_df))
    transform_rate["转换题型"].append("期望类")


# 处理"填写答案百分数"类
def transform_percentage(read_df: pd.DataFrame, file_name: str):
    """
    Clean belief questions data.
    :param read_df: DataFrame object
    :param file_name: raw file name
    """
    # 获取“填写答案百分数”的列索引值
    index_of_answer = -1
    for i in range(len(read_df.columns)):
        if read_df.columns[i] == "填写答案百分数":
            index_of_answer = i
    read_df.insert(index_of_answer, "填写答案百分数（改）",
                   read_df[["填写答案百分数"]].applymap(robust_clean_percent).applymap(hybrid_to_arabic))
    read_df.sort_values(by="填写答案百分数（改）", inplace=True)
    read_df.reset_index(drop=True, inplace=True)
    # 添加排序标识符，用于排序
    read_df['排序标识符'] = 2
    for i in range(len(read_df)):
        answer = read_df.loc[i, "填写答案百分数（改）"]
        initial_answer = read_df.loc[i, "填写答案百分数"]
        if not np.isnan(answer):
            read_df.loc[i, "排序标识符"] = 0
        elif unknown(initial_answer):
            read_df.loc[i, "填写答案百分数（改）"] = 0
            read_df.loc[i, "排序标识符"] = 0
    read_df.sort_values(by="排序标识符", kind='mergesort', inplace=True)
    read_df.reset_index(drop=True, inplace=True)
    file_path = current_path + os.sep + file_name
    read_df.to_excel(file_path)
    # 转换率
    transform_rate["文件名"].append(file_name.split('.')[0])
    transform_rate["转换率"].append(len(read_df[read_df["排序标识符"] != 2]) / len(read_df))
    transform_rate["转换题型"].append("了解类")


def transform_multiple_choice(read_df: pd.DataFrame, file_name: str):
    """
    Clean belief questions data.
    :param read_df: DataFrame object
    :param file_name: raw file name
    """
    # 获取“填写答案”的列索引值
    index_of_answer = -1
    index_of_answer2 = -1
    for i in range(len(read_df.columns)):
        if read_df.columns[i] == "填写答案1":
            index_of_answer = i
        if read_df.columns[i] == "填写答案2":
            index_of_answer2 = i
    if index_of_answer != -1:
        read_df.insert(index_of_answer, "填写答案1（改）", read_df[["填写答案1"]].applymap(quantify))
    if index_of_answer2 != -1:
        read_df.insert(index_of_answer2+1, "填写答案2（改）", read_df[["填写答案2"]].applymap(quantify))
    file_path = current_path + os.sep + file_name
    read_df.to_excel(file_path)
    # 转换率
    transform_rate["文件名"].append(file_name.split('.')[0])
    transform_rate["转换率"].append(1.0)
    transform_rate["转换题型"].append("选择题")


def write_to_excel(dir_path: str):
    """
    Write transformed data files to a new directory.
    :param dir_path: the directory storing the raw data files
    """
    # 在运行目录创建一个新的文件夹用于存放处理后的excel表格
    global current_path
    current_path = os.getcwd() + os.sep + "BQD转换-" + time.strftime("%Y%m%d%H%M%S")
    current_path = ralib.mkfile.convert_path(current_path)
    ralib.mkfile.mkdir(current_path)
    #
    path = ralib.mkfile.convert_path(dir_path)
    file_list = ralib.mkfile.traverse_files(path, "xlsx")
    for file_path in tqdm(file_list):
        read_file(file_path)
        sleep(0.1)


def statistics():
    """
    Returns statistics summary.
    :return: statistics summary
    """
    stat = pd.DataFrame(transform_rate)
    stat.sort_values(by="转换题型", kind='mergesort', inplace=True)
    stat.reset_index(drop=True, inplace=True)
    file_path = current_path + os.sep + "summary.xlsx"
    file_path = ralib.mkfile.convert_path(file_path)
    stat.to_excel(file_path)
    print("筛选完成！转换后数据文件和描述文件summary已存至 " + current_path)


def main():
    print("文件读取中，请稍等...")
    write_to_excel(sys.argv[1])
    statistics()


if __name__ == "__main__":
    main()
