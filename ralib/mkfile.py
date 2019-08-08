import os
from openpyxl import load_workbook
import pandas as pd
from .helper import rm_space


def to_existing_excel(df: pd.DataFrame, file_path: str, sheet_name: str):
    """
    Write DataFrame to a existing excel file, adding a new sheet not covering old sheets.

    :param df: DateFrame to write
    :param file_path: path of the destination excel file
    :param sheet_name: name of the new sheet
    :return:
    """
    path = rm_space(file_path)
    sheet = rm_space(sheet_name)
    book = load_workbook(path)
    writer = pd.ExcelWriter(path, engine='openpyxl')
    writer.book = book
    df.to_excel(writer, sheet, index=None)
    writer.save()
    writer.close()


def mkdir(dir_path: str):
    """
    Make a new directory if it doesn't exist.

    :param dir_path: the path of the directory
    """
    path = rm_space(dir_path)
    exists = os.path.exists(path)
    if not exists:
        os.makedirs(path)
        # print("{} PATH:{}".format("创建成功!", path))
        return
    else:
        # print("{} PATH:{}".format("目录已存在!", path))
        return


def convert_path(path: str) -> str:
    """
    Convert path to the current OS format.
    :param path: path to be converted
    :return: converted path
    """
    path1 = rm_space(path)
    return path1.replace(r'\/'.replace(os.sep, ''), os.sep)


def traverse_files(dir_path: str, file_type: str) -> list:
    """
    Traverse all files in the directory.
    :param dir_path: directory path
    :param file_type: type of files to be traversed
    :return: list of traversed files
    """
    path = rm_space(dir_path)
    file_type1 = rm_space(file_type)
    file_list = []
    for root, dirs, files in os.walk(path):
        for name in files:
            file_name = os.path.join(root, name)
            if file_name.split('.')[-1] == file_type1:
                file_list.append(file_name)
    return file_list
