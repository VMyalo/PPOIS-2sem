#!/usr/bin/env python3
"""Генерация демонстрационных XML-файлов (≥50 осмысленных записей)."""

import random
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.model.patient import PatientRecord
from src.model import xml_io

SURNAMES = [
    "Иванов", "Петров", "Сидоров", "Козлов", "Новиков", "Морозов",
    "Волков", "Соколов", "Лебедев", "Кузнецов", "Попов", "Орлов",
    "Белый", "Черный", "Зайцев", "Медведев", "Громов", "Крылов",
]
NAMES = [
    "Александр", "Дмитрий", "Максим", "Иван", "Артём", "Никита",
    "Анна", "Мария", "Елена", "Ольга", "Наталья", "Виктория",
]
PATRONYMICS = [
    "Александрович", "Дмитриевич", "Сергеевич", "Иванович",
    "Александровна", "Дмитриевна", "Сергеевна", "Ивановна",
]
STREETS = [
    "пр-т Независимости", "ул. Ленина", "ул. Сурганова",
    "ул. Притыцкого", "пр-т Дзержинского", "ул. Каховская",
    "ул. Якуба Коласа", "ул. Бобруйская", "ул. Козлова",
]
DOCTORS = [
    "Смирнова Елена Викторовна",
    "Ковалёв Пётр Анатольевич",
    "Лисова Татьяна Игоревна",
    "Баранов Олег Станиславович",
    "Федорова Нина Петровна",
    "Гришин Андрей Владимирович",
]
CONCLUSIONS = [
    "ОРВИ, назначено симптоматическое лечение.",
    "Гипертония I ст., рекомендован контроль АД.",
    "Гастрит, назначена диета и обследование.",
    "Аллергический ринит, антигистаминные препараты.",
    "Остеохондроз, физиотерапия и ЛФК.",
    "Бронхит, ингаляции и отхаркивающие средства.",
    "Сахарный диабет 2 типа, коррекция питания.",
    "Мигрень, профилактика и обезболивание.",
    "Варикозное расширение вен, компрессионный трикотаж.",
    "Анемия лёгкой степени, препараты железа.",
]


def random_date(start: date, end: date) -> date:
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))


def make_records(count: int, seed: int) -> list[PatientRecord]:
    random.seed(seed)
    records = []
    for i in range(count):
        surname = random.choice(SURNAMES)
        name = random.choice(NAMES)
        patr = random.choice(PATRONYMICS)
        patient_fio = f"{surname} {name} {patr}"
        street = random.choice(STREETS)
        house = random.randint(1, 120)
        flat = random.randint(1, 200)
        city = random.choice(["г. Минск", "г. Гомель", "г. Брест", "г. Витебск"])
        address = f"{city}, {street}, д. {house}, кв. {flat}"
        birth = random_date(date(1955, 1, 1), date(2010, 12, 31))
        appointment = random_date(date(2023, 1, 1), date(2025, 12, 31))
        if appointment < birth:
            appointment = birth + timedelta(days=random.randint(365, 15000))
        doctor = random.choice(DOCTORS)
        conclusion = random.choice(CONCLUSIONS)
        records.append(
            PatientRecord(
                patient_fio=patient_fio,
                address=address,
                birth_date=birth,
                appointment_date=appointment,
                doctor_fio=doctor,
                conclusion=conclusion,
            )
        )
    return records


def main() -> None:
    out_dir = ROOT / "data" / "demo"
    out_dir.mkdir(parents=True, exist_ok=True)
    configs = [
        ("patients_clinic_1.xml", 55, 1),
        ("patients_clinic_2.xml", 60, 2),
        ("patients_clinic_3.xml", 52, 3),
    ]
    for filename, count, seed in configs:
        path = out_dir / filename
        records = make_records(count, seed)
        xml_io.write_xml(path, records)
        print(f"Создан {path} ({len(records)} записей)")


if __name__ == "__main__":
    main()
