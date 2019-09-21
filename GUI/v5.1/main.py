import tkinter as tk
from tkinter import filedialog
import tkinter.messagebox
import os

window = tk.Tk()

window.title("公司实验")

window.geometry("500x300")

window.maxsize(500, 320)
window.minsize(500, 320)

tk.Label(window, text="请选择一个功能", fg='white',
         bg='#4169E1', font=('Arial', 25), width=35, height=2).pack()


def select_path():
    return tk.filedialog.askopenfilename()


def select_dir_path():
    return tk.filedialog.askdirectory()


def hit1():
    tkinter.messagebox.showinfo(message="(1/3)请选择一个门店分组表")
    file_path1 = select_path()
    if file_path1 == '':  # 取消选择文件时，取消整个动作
        tkinter.messagebox.showwarning(message="已取消")
        return

    tkinter.messagebox.showinfo(message="(2/3)请选择一个员工信息表")
    file_path2 = select_path()
    if file_path2 == '':
        tkinter.messagebox.showwarning(message="已取消")
        return

    tkinter.messagebox.showinfo(message="(3/3)请选择一个总数据表")
    file_path3 = select_path()
    if file_path2 == '':
        tkinter.messagebox.showwarning(message="已取消")
        return

    current_path = os.getcwd()
    n = os.system("python3 " + current_path + os.sep + "IDFilter_gui.py " +
                  file_path1 + ' ' + file_path2 + ' ' + file_path3)
    if n == 0:
        result = tkinter.messagebox.askyesno(message="筛选完成！名单已存至" + current_path + "，是否打开？")
        if result:
            os.system("open " + current_path)
    else:
        tkinter.messagebox.showerror(message="筛选失败，请重试！")


def hit2():
    tkinter.messagebox.showinfo(message="(1/3)请选择一个汇总表")
    file_path1 = select_path()
    if file_path1 == '':  # 取消选择文件时，取消整个动作
        tkinter.messagebox.showwarning(message="已取消")
        return

    tkinter.messagebox.showinfo(message="(2/3)请选择一个员工信息表")
    file_path2 = select_path()
    if file_path2 == '':
        tkinter.messagebox.showwarning(message="已取消")
        return

    tkinter.messagebox.showinfo(message="(3/3)请选择一个总数据表")
    file_path3 = select_path()
    if file_path2 == '':
        tkinter.messagebox.showwarning(message="已取消")
        return

    current_path = os.getcwd()
    n = os.system("python3 " + current_path + os.sep + "PeerFilter_gui.py " +
                  file_path1 + ' ' + file_path2 + ' ' + file_path3)

    if n == 0:
        result = tkinter.messagebox.askyesno(message="筛选完成！名单已存至" + current_path + "，是否打开？")
        if result:
            os.system("open " + current_path)
    else:
        tkinter.messagebox.showerror(message="筛选失败，请重试！")


def hit3():
    tkinter.messagebox.showwarning(message="暂未开启")


def hit4():
    tkinter.messagebox.showinfo(message="(1/1)请选择一个问卷回答文件夹")
    file_path1 = select_dir_path()
    if file_path1 == '':  # 取消选择文件时，取消整个动作
        tkinter.messagebox.showwarning(message="已取消")
        return

    current_path = os.getcwd()
    n = os.system("python3 " + current_path + os.sep + "BQDFormat_gui.py " +
                  file_path1)
    if n == 0:
        result = tkinter.messagebox.askyesno(message="筛选完成！数据已存至" + current_path + "，是否打开？")
        if result:
            os.system("open " + current_path)
    else:
        tkinter.messagebox.showerror(message="筛选失败，请重试！")


def hit5():
    tkinter.messagebox.showinfo(message="(1/1)请选择一个筛选名单文件夹")
    file_path1 = select_dir_path()
    if file_path1 == '':  # 取消选择文件时，取消整个动作
        tkinter.messagebox.showwarning(message="已取消")
        return

    def input_date():
        file_path2 = entry1.get()
        print(file_path2)
        current_path = os.getcwd()
        n = os.system("python3 " + current_path + os.sep + "IC_gui.py " +
                      file_path1 + ' ' + file_path2)
        if n == 0:
            result = tkinter.messagebox.askyesno(message="筛选完成！推送内容已存至" + current_path + "，是否打开？")
            if result:
                os.system("open " + current_path)
        else:
            tkinter.messagebox.showerror(message="筛选失败，请重试！")
        root.destroy()

    def cancel_input():
        tkinter.messagebox.showwarning(message="已取消")
        root.destroy()
        return

    tkinter.messagebox.showinfo(message="(2/2)请填写推送起始日期")
    root = tk.Tk()
    root.title("参数二")
    root.geometry('400x100')
    root.maxsize(400, 100)
    root.minsize(400, 100)
    tk.Label(root, text="请输入本月推送起始日期：", fg='#2E8B57', font=('Arial', 16)).place(x=10, y=20)
    tk.Label(root, text="（日期必须为星期三或星期六）", fg='#2E8B57', font=('Arial', 14)).place(x=1, y=40)
    var = tk.StringVar()
    var.set('2019-8-17')
    entry1 = tk.Entry(root, textvariable=var, fg='#696969', font=('Arial', 16))
    entry1.place(x=200, y=20)

    btn1 = tk.Button(root, text="确定", command=input_date)
    btn2 = tk.Button(root, text="取消", command=cancel_input)
    btn2.place(x=200, y=60)
    btn1.place(x=315, y=60)

    root.mainloop()


def on_closing():
    if tkinter.messagebox.askokcancel(message="确定退出？"):
        window.destroy()


tk.Label(window, text="1. 被推送名单筛选", fg='#8B4513', font=('Arial', 16)).place(x=130, y=70)
id_b = tk.Button(window, text="点击开始", width=6, command=hit1)
id_b.place(x=280, y=70)

tk.Label(window, text="2. 推送名单筛选    ", fg='#8B4513', font=('Arial', 16)).place(x=130, y=110)
peer_b = tk.Button(window, text="点击开始", width=6, command=hit2)
peer_b.place(x=280, y=110)

tk.Label(window, text="3. 维护表更新        ", fg='#8B4513', font=('Arial', 16)).place(x=130, y=150)
hire_b = tk.Button(window, text="点击开始", width=6, command=hit3)
hire_b.place(x=280, y=150)

tk.Label(window, text="4. 问卷数据转换       ", fg='#8B4513', font=('Arial', 16)).place(x=130, y=190)
bqd_b = tk.Button(window, text="点击开始", width=6, command=hit4)
bqd_b.place(x=280, y=190)

tk.Label(window, text="5. 推送内容填写       ", fg='#8B4513', font=('Arial', 16)).place(x=130, y=230)
ic_b = tk.Button(window, text="点击开始", width=6, command=hit5)
ic_b.place(x=280, y=230)

exit_b = tk.Button(window, text="点击退出", width=6, command=on_closing)
exit_b.place(x=280, y=270)

window.mainloop()
