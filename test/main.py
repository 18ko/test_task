from typing import Union, List
from datetime import date
from fastapi import FastAPI
from pydantic import BaseModel
import xlrd
import datetime
import random
import sqlite3

path_to_file = "0.xlsx"


class Db():
    def connect(self):
        try:
            connect = sqlite3.connect("test_task.db")
            cursor = connect.cursor()
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS test_task (id INTEGER PRIMARY KEY AUTOINCREMENT, date DATE, company VARCHAR(255), f_qliq_d1 INT, f_qliq_d2 INT, f_qoil_d1 INT, f_qoil_d2 INT, fc_qliq_d1 INT, fc_qliq_d2 INT, fc_qoil_d1 INT, fc_qoil_d2 INT)"
            )
        except Exception as e:
            print("Ошибка БД: ")
            print(e)

    def create(self, item):
        try:
            connect = sqlite3.connect("test_task.db")
            cursor = connect.cursor()
            cmd = f"INSERT INTO test_task ({item[0]}) VALUES({item[1]})"
            cursor.execute(cmd)
            connect.commit()
        except Exception as e:
            print("Ошибка БД: ")
            print(e)
            pass

    def read(self, filter, item=None):
        if filter == 'id':
            try:
                connect = sqlite3.connect("test_task.db")
                cursor = connect.cursor()
                cmd = f"SELECT * FROM test_task WHERE id = {item.id}"
                result = cursor.execute(cmd)
                return result.fetchone()
            except Exception as e:
                print("Ошибка БД: ")
                print(e)
        elif filter == 'params':
            try:
                params = []
                cmd_str = ''
                for key in item:
                    if type(item[key]) is str:
                        if key is 'date':
                            params.append(
                                key + " = date('" + str(item[key]) + "')")
                        else:
                            params.append(key + " = '" + str(item[key]) + "'")
                    elif type(item[key]) is int:
                        params.append(key + " = " + str(item[key]))
                for i in range(0, len(params)):
                    if (len(params)-1) == i:
                        cmd_str += params[i]
                    else:
                        cmd_str += params[i] + ' AND '
                connect = sqlite3.connect("test_task.db")
                cursor = connect.cursor()
                cmd = f"SELECT * FROM test_task WHERE {cmd_str}"
                result = cursor.execute(cmd)
                return result.fetchall()
            except Exception as e:
                print("Ошибка БД: ")
                print(e)
        elif filter == 'all':
            try:
                connect = sqlite3.connect("test_task.db")
                cursor = connect.cursor()
                cmd = f"SELECT * FROM test_task"
                result = cursor.execute(cmd)
                return result.fetchall()
            except Exception as e:
                print("Ошибка БД: ")
                print(e)


class Item(BaseModel):
    id: int
    date: date
    company: Union[str, None] = None
    f_qliq_d1: Union[int, None] = None
    f_qliq_d2: Union[int, None] = None
    f_qoil_d1: Union[int, None] = None
    f_qoil_d2: Union[int, None] = None
    fc_qliq_d1: Union[int, None] = None
    fc_qliq_d2: Union[int, None] = None
    fc_qoil_d1: Union[int, None] = None
    fc_qoil_d2: Union[int, None] = None

    def save(self):
        params = ['id, date, company, f_qliq_d1, f_qliq_d2, f_qoil_d1, f_qoil_d2, fc_qliq_d1, fc_qliq_d2, fc_qoil_d1, fc_qoil_d2',
                  f'{self.id}, "{self.date}", "{self.company}", {self.f_qliq_d1}, {self.f_qliq_d2}, {self.f_qoil_d1}, {self.f_qoil_d2}, {self.fc_qliq_d1}, {self.fc_qliq_d2}, {self.fc_qoil_d1}, {self.fc_qoil_d2}']
        db = Db()
        db.create(params)


class Groups(BaseModel):
    date: date
    items: List[Item]
    qliq_f: int
    qoil_f: int
    qliq_fc: int
    qoil_fc: int


class Result(BaseModel):
    groups: List[Groups]
    qliq: int
    qoil: int


def add_items():
    db = Db()
    db.connect()
    try:
        workbook = xlrd.open_workbook(path_to_file)
        worksheet = workbook.sheet_by_index(0)
        for i in range(3, 23):
            item = Item(
                id=int(worksheet.cell_value(i, 0)),
                date=datetime.date(2022, 4, random.randint(1, 5)),
                company=str(worksheet.cell_value(i, 1)),
                f_qliq_d1=int(worksheet.cell_value(i, 2)),
                f_qliq_d2=int(worksheet.cell_value(i, 3)),
                f_qoil_d1=int(worksheet.cell_value(i, 4)),
                f_qoil_d2=int(worksheet.cell_value(i, 5)),
                fc_qliq_d1=int(worksheet.cell_value(i, 6)),
                fc_qliq_d2=int(worksheet.cell_value(i, 7)),
                fc_qoil_d1=int(worksheet.cell_value(i, 8)),
                fc_qoil_d2=int(worksheet.cell_value(i, 9)),
            )
            item.save()
    except Exception as e:
        print("Ошибка: " + str(i))
        print(e)


app = FastAPI()


@app.get("/")
def read_root():
    add_items()
    return {"status": "Данные из файла импортированы в бд test_task.db", "help": "Документация находится по url /docs"}


@app.get("/items/")
async def read_items():
    db = Db()
    items = []
    for item in db.read('all'):
        items.append(Item(
            id=item[0],
            date=item[1],
            company=item[2],
            f_qliq_d1=item[3],
            f_qliq_d2=item[4],
            f_qoil_d1=item[5],
            f_qoil_d2=item[6],
            fc_qliq_d1=item[7],
            fc_qliq_d2=item[8],
            fc_qoil_d1=item[9],
            fc_qoil_d2=item[10],
        ))
    days = []
    for item in items:
        if item.date not in days:
            days.append(item.date)
    result = []
    qliq_f = 0
    qoil_f = 0
    qliq_fc = 0
    qoil_fc = 0
    qliq = 0
    qoil = 0
    for day in days:
        group = []
        for item in items:
            if item.date == day:
                group.append(item)
                qliq_f += item.f_qliq_d1 + item.f_qliq_d2
                qliq_fc += item.fc_qliq_d1 + item.fc_qliq_d2
                qoil_f += item.f_qoil_d1 + item.f_qoil_d2
                qoil_fc += item.fc_qoil_d1 + item.fc_qoil_d2
                qliq += item.f_qliq_d1 + item.f_qliq_d2 + item.fc_qliq_d1 + item.fc_qliq_d2
                qoil += item.f_qoil_d1 + item.f_qoil_d2 + item.fc_qoil_d1 + item.fc_qoil_d2
        groups = Groups(
            date=day,
            items=group,
            qliq_f=qliq_f,
            qoil_f=qoil_f,
            qliq_fc=qliq_fc,
            qoil_fc=qoil_fc,
        )
        result.append(groups)
    r = Result(
        groups=result,
        qliq=qliq,
        qoil=qoil
    )
    print(r)
    return r
