import os
from openpyxl import load_workbook
import pandas as pd
from .helper import rm_space


def to_existing_excel(df, file_path, sheet_name):
    """
    Write DataFrame to a existing excel file, adding a new sheet not covering old sheets.

    :param df: DateFrame to write
    :param file_path: path of the destination excel file
    :param sheet_name: name of the new sheet
    :return:
    """
    book = load_workbook(file_path)
    writer = pd.ExcelWriter(file_path, engine='openpyxl')
    writer.book = book
    df.to_excel(writer, sheet_name, index=None)
    writer.save()
    writer.close()


def mkdir(path: str):
    """
    Make a new directory if it doesn't exist.

    :param path: the path of the directory
    """
    path = rm_space(path)
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
    return path.replace(r'\/'.replace(os.sep, ''), os.sep)
