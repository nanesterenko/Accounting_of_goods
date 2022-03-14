"""Вы делаете приложение по учёту товаров на складе."""

import json
import sqlite3
from typing import Any
from jsonschema import validate
from jsonschema.exceptions import ValidationError


def read_from_file(path_to_file: str) -> dict:
    """"Считываем схему и входящие данные из json файлов."""
    try:
        with open(path_to_file, "r", encoding="UTF-8") as file_json:
            input_data = json.load(file_json)
        with open("goods.schema_.json", "r", encoding="UTF-8") as json_schema:
            schema = json.load(json_schema)
        """Происходит валидация входных данных."""
        validate(input_data, schema)
    except ValidationError:
        print("Ошибка валидации данных")
    return input_data


def create_tab(connect: Any) -> None:
    """Приложение создаёт таблицы если они не созданы."""
    c = connect.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS packages( \n
        id INTEGER PRIMARY KEY AUTOINCREMENT, \n
        type VARCHAR(50), \n
        height FLOAT CHECK (height > 0), \n
        width FLOAT CHECK (width > 0), \n
        depth FLOAT CHECK (depth > 0));""")
    c.execute("""CREATE TABLE IF NOT EXISTS goods( \n
        id INTEGER PRIMARY KEY, \n
        name VARCHAR(50) UNIQUE NOT NULL, \n
        package_id INTEGER NOT NULL, \n
        FOREIGN KEY (package_id) REFERENCES packages(id));""")
    c.execute("""CREATE TABLE IF NOT EXISTS shops( \n
        id INTEGER PRIMARY KEY AUTOINCREMENT, \n
        address VARCHAR(100));""")
    c.execute("""CREATE TABLE IF NOT EXISTS shops_goods( \n
        id INTEGER PRIMARY KEY AUTOINCREMENT, \n
        id_good INTEGER NOT NULL, \n
        id_shop INTEGER NOT NULL, \n
        amount INTEGER NOT NULL CHECK (amount >0), \n
        FOREIGN KEY (id_good) REFERENCES goods(id), \n
        FOREIGN KEY (id_shop) REFERENCES shops(id));""")
    connect.commit()


def insert_shops(connect: Any, input_data: dict) -> str:
    """Подготовка данных к вставке в БД."""
    pack_type = input_data["package_params"]["type"]
    pack_width = input_data["package_params"]["width"]
    pack_height = input_data["package_params"]["height"]
    pack_depth = input_data["package_params"]["depth"]
    packages = (f"INSERT INTO packages (type, height, width, depth) \n"
                f"     VALUES (\"{pack_type}\", {pack_height}, {pack_width}, {pack_depth});")
    request_execute(connect, packages)

    pack_id = "SELECT MAX(id) FROM packages"
    id_good = input_data["id"]
    goods_name = input_data["name"]
    goods = (f"INSERT INTO goods (id, name, package_id)\n"
             f"VALUES ({id_good}, \"{goods_name}\", ({pack_id}));")
    request_execute(connect, goods)

    data_for_shops = input_data["location_and_quantity"]
    for item in data_for_shops:
        shop_location = item["location"]
        shops = f"INSERT INTO shops (address) VALUES (\"{shop_location}\");"
        request_execute(connect, shops)
        goods_amount = item["amount"]
        id_shop = "SELECT MAX(id) FROM shops"
        shops_goods = (f"INSERT INTO shops_goods (id_good, id_shop, amount)\n"
                       f"VALUES ({id_good}, ({id_shop}), {goods_amount});")
        request_execute(connect, shops_goods)
    return "Данные обновлены"


def request_execute(connect: Any, request: str) -> None:
    """Если пришли новые данные по предмету уже имеющемуся в базе — отвергнуть и написать об этом на экран."""
    c = connect.cursor()
    try:
        c.execute(request)
        connect.commit()
    except sqlite3.Error:
        print(f"Ошибка при добавлении данных в БД \n {request}")


def main(path_to_file: str) -> None:
    """Основная функция."""
    data = read_from_file(path_to_file)
    connect = sqlite3.connect('TASK.db')
    create_tab(connect)
    insert_shops(connect, data)
    connect.close()


if __name__ == "__main__":
    #main("input_example.json")
    main("testss\input2.json")
