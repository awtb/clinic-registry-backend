"""Seed the database with dental clinic test data in Russian.

Wipes non-root users and all procedures/categories/medical records, then inserts
a coherent set of dental clinic users, categories, procedures, patients, and
medical records linking them together.

Run from the repository root:

    PYTHONPATH=. uv run python scripts/seed_dental_data.py
"""
from __future__ import annotations

import asyncio
import random
from datetime import date
from datetime import datetime
from datetime import timedelta
from decimal import Decimal

from sqlalchemy import delete
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from ulid import ULID

from clinic_registry.core.enums.patient import PatientGender
from clinic_registry.core.enums.user import UserRole
from clinic_registry.core.security.hasher import PasswordHasher
from clinic_registry.db.models.log import Log
from clinic_registry.db.models.medical_record import MedicalRecord
from clinic_registry.db.models.medical_record_procedure import (
    medical_record_procedures,
)
from clinic_registry.db.models.patient import Patient
from clinic_registry.db.models.procedure import Procedure
from clinic_registry.db.models.procedure_category import ProcedureCategory
from clinic_registry.db.models.user import User
from clinic_registry.settings import Settings

ROOT_EMAIL = "root@clinic.local"
RANDOM_SEED = 42


USERS = [
    {
        "username": "i.petrov",
        "first_name": "Иван",
        "last_name": "Петров",
        "email": "i.petrov@clinic.local",
        "role": UserRole.admin,
        "password": "petrov123",
    },
    {
        "username": "o.smirnova",
        "first_name": "Ольга",
        "last_name": "Смирнова",
        "email": "o.smirnova@clinic.local",
        "role": UserRole.user,
        "password": "smirnova123",
    },
    {
        "username": "a.kuznetsova",
        "first_name": "Анна",
        "last_name": "Кузнецова",
        "email": "a.kuznetsova@clinic.local",
        "role": UserRole.user,
        "password": "kuznetsova123",
    },
    {
        "username": "s.volkov",
        "first_name": "Сергей",
        "last_name": "Волков",
        "email": "s.volkov@clinic.local",
        "role": UserRole.user,
        "password": "volkov123",
    },
    {
        "username": "m.fedorov",
        "first_name": "Михаил",
        "last_name": "Фёдоров",
        "email": "m.fedorov@clinic.local",
        "role": UserRole.user,
        "password": "fedorov123",
    },
]


CATEGORIES = [
    ("THER", "Терапевтическая стоматология", "Лечение кариеса, пульпита, периодонтита"),
    ("SURG", "Хирургическая стоматология", "Удаление зубов и амбулаторные операции"),
    ("ORTH", "Ортопедическая стоматология", "Протезирование: коронки, виниры, мосты"),
    ("ORTD", "Ортодонтия", "Исправление прикуса и положения зубов"),
    ("HYG", "Гигиена и профилактика", "Профессиональная гигиена и профилактика"),
    ("ENDO", "Эндодонтия", "Лечение корневых каналов"),
    ("IMPL", "Имплантология", "Установка дентальных имплантатов"),
    ("PARO", "Пародонтология", "Лечение заболеваний дёсен и пародонта"),
    ("PED", "Детская стоматология", "Стоматологическая помощь детям"),
    ("DIAG", "Диагностика", "Рентгенологические и инструментальные исследования"),
]


PROCEDURES = [
    (
        "DIAG",
        "DG-001",
        "Первичная консультация стоматолога",
        "Осмотр, сбор анамнеза, план лечения",
        "1000.00",
    ),
    (
        "DIAG",
        "DG-002",
        "Прицельный рентгеновский снимок зуба",
        "Радиовизиография одного зуба",
        "500.00",
    ),
    (
        "DIAG",
        "DG-003",
        "Ортопантомограмма (ОПТГ)",
        "Панорамный снимок обеих челюстей",
        "1500.00",
    ),
    (
        "DIAG",
        "DG-004",
        "Компьютерная томография челюсти (КЛКТ)",
        "3D-исследование",
        "4500.00",
    ),
    (
        "THER",
        "TH-001",
        "Лечение поверхностного кариеса",
        "Препарирование и пломба светового отверждения",
        "3500.00",
    ),
    (
        "THER",
        "TH-002",
        "Лечение среднего кариеса",
        "Лечение с постановкой пломбы из композита",
        "4500.00",
    ),
    (
        "THER",
        "TH-003",
        "Лечение глубокого кариеса",
        "С наложением лечебной прокладки",
        "5500.00",
    ),
    (
        "THER",
        "TH-004",
        "Реставрация скола фронтального зуба",
        "Художественная реставрация",
        "6500.00",
    ),
    (
        "ENDO",
        "EN-001",
        "Лечение пульпита одноканального зуба",
        "Эндодонтическое лечение, обтурация канала",
        "7000.00",
    ),
    (
        "ENDO",
        "EN-002",
        "Лечение пульпита двухканального зуба",
        "Лечение каналов и пломбирование",
        "9500.00",
    ),
    (
        "ENDO",
        "EN-003",
        "Лечение пульпита трёх- и многоканального зуба",
        "Полное эндодонтическое лечение",
        "12500.00",
    ),
    (
        "ENDO",
        "EN-004",
        "Перелечивание корневых каналов",
        "Распломбировка и повторная обтурация",
        "11000.00",
    ),
    (
        "SURG",
        "SU-001",
        "Удаление зуба простое",
        "Удаление подвижного или однокорневого зуба",
        "2500.00",
    ),
    ("SURG", "SU-002", "Удаление зуба сложное", "С разделением корней", "5000.00"),
    (
        "SURG",
        "SU-003",
        "Удаление ретинированного зуба мудрости",
        "С выкраиванием слизисто-надкостничного лоскута",
        "9500.00",
    ),
    (
        "SURG",
        "SU-004",
        "Резекция верхушки корня",
        "Зубосохраняющая операция",
        "8500.00",
    ),
    (
        "HYG",
        "HG-001",
        "Профессиональная гигиена полости рта",
        "Ультразвуковая чистка + Air Flow + полировка",
        "5500.00",
    ),
    ("HYG", "HG-002", "Фторирование зубов", "Глубокое фторирование эмали", "1800.00"),
    ("HYG", "HG-003", "Снятие зубных отложений ультразвуком", "Скейлинг", "2500.00"),
    (
        "ORTH",
        "OR-001",
        "Металлокерамическая коронка",
        "Изготовление и фиксация",
        "18000.00",
    ),
    (
        "ORTH",
        "OR-002",
        "Цельнокерамическая коронка E-max",
        "Безметалловая керамика",
        "32000.00",
    ),
    (
        "ORTH",
        "OR-003",
        "Керамический винир",
        "Фарфоровый винир на фронтальный зуб",
        "35000.00",
    ),
    (
        "ORTH",
        "OR-004",
        "Съёмный пластиночный протез",
        "Частичный или полный",
        "27000.00",
    ),
    (
        "ORTD",
        "OD-001",
        "Консультация ортодонта",
        "Осмотр и план ортодонтического лечения",
        "1500.00",
    ),
    (
        "ORTD",
        "OD-002",
        "Установка металлических брекетов на одну челюсть",
        "Лигатурная брекет-система",
        "35000.00",
    ),
    ("ORTD", "OD-003", "Активация брекет-системы", "Плановая коррекция", "2500.00"),
    (
        "IMPL",
        "IM-001",
        "Установка дентального имплантата",
        "Имплант системы Straumann/Osstem",
        "45000.00",
    ),
    (
        "IMPL",
        "IM-002",
        "Установка формирователя десны",
        "Через 3-4 месяца после имплантации",
        "5000.00",
    ),
    ("IMPL", "IM-003", "Коронка на имплантате", "Абатмент и коронка", "38000.00"),
    (
        "PARO",
        "PA-001",
        "Лечение гингивита",
        "Профессиональная гигиена + противовоспалительная терапия",
        "4500.00",
    ),
    (
        "PARO",
        "PA-002",
        "Кюретаж пародонтальных карманов закрытый",
        "В области одного зуба",
        "1200.00",
    ),
    (
        "PARO",
        "PA-003",
        "Шинирование подвижных зубов",
        "Стекловолоконной лентой",
        "8500.00",
    ),
    (
        "PED",
        "PD-001",
        "Лечение кариеса молочного зуба",
        "С использованием детских пломбировочных материалов",
        "3000.00",
    ),
    (
        "PED",
        "PD-002",
        "Серебрение молочных зубов",
        "Профилактика прогрессирования кариеса",
        "1500.00",
    ),
    (
        "PED",
        "PD-003",
        "Герметизация фиссур",
        "Профилактическая запечатывающая обработка",
        "2200.00",
    ),
]


PATIENTS = [
    (
        "Александр",
        "Иванов",
        PatientGender.MALE,
        "1985-03-12",
        "4501123456",
        "+79161234567",
        "Хронический пародонтит лёгкой степени",
    ),
    (
        "Мария",
        "Соколова",
        PatientGender.FEMALE,
        "1992-07-21",
        "4502234567",
        "+79161234568",
        "Аллергия на лидокаин",
    ),
    (
        "Дмитрий",
        "Морозов",
        PatientGender.MALE,
        "1978-11-04",
        "4503345678",
        "+79161234569",
        "Бруксизм",
    ),
    (
        "Елена",
        "Васильева",
        PatientGender.FEMALE,
        "1990-01-30",
        "4504456789",
        "+79161234570",
        None,
    ),
    (
        "Никита",
        "Попов",
        PatientGender.MALE,
        "2001-05-17",
        "4505567890",
        "+79161234571",
        "Скученность фронтальной группы зубов",
    ),
    (
        "Светлана",
        "Новикова",
        PatientGender.FEMALE,
        "1965-09-09",
        "4506678901",
        "+79161234572",
        "Полное отсутствие жевательной группы 36, 37, 46",
    ),
    (
        "Артём",
        "Лебедев",
        PatientGender.MALE,
        "1995-12-25",
        "4507789012",
        "+79161234573",
        None,
    ),
    (
        "Татьяна",
        "Козлова",
        PatientGender.FEMALE,
        "1982-06-14",
        "4508890123",
        "+79161234574",
        "Беременность 24 недели",
    ),
    (
        "Виктор",
        "Павлов",
        PatientGender.MALE,
        "1958-02-28",
        "4509901234",
        "+79161234575",
        "Частичная вторичная адентия",
    ),
    (
        "Ирина",
        "Никитина",
        PatientGender.FEMALE,
        "1999-08-03",
        "4510012345",
        "+79161234576",
        "Чувствительность шеек зубов",
    ),
    (
        "Роман",
        "Соловьёв",
        PatientGender.MALE,
        "1987-04-19",
        "4511123450",
        "+79161234577",
        None,
    ),
    (
        "Юлия",
        "Орлова",
        PatientGender.FEMALE,
        "1973-10-11",
        "4512234501",
        "+79161234578",
        "Хронический генерализованный гингивит",
    ),
    (
        "Максим",
        "Захаров",
        PatientGender.MALE,
        "2015-06-08",
        "4513345012",
        "+79161234579",
        "Множественный кариес молочных зубов",
    ),
    (
        "София",
        "Беляева",
        PatientGender.FEMALE,
        "2017-02-14",
        "4514450123",
        "+79161234580",
        "Профилактический детский осмотр",
    ),
    (
        "Григорий",
        "Зайцев",
        PatientGender.MALE,
        "1969-08-22",
        "4515561234",
        "+79161234581",
        "Дистальный прикус",
    ),
]


# (patient_idx, diagnosis, treatment, complaint, procedure_codes)
RECORDS = [
    (
        0,
        "Кариес 36 зуба, средняя форма",
        "Препарирование, медобработка, пломба из светоотверждаемого композита",
        "Боль от сладкого и холодного на нижней челюсти слева",
        ["DG-001", "DG-002", "TH-002"],
    ),
    (
        1,
        "Острый пульпит 26 зуба",
        "Депульпирование, обтурация трёх каналов гуттаперчей, временная пломба",
        "Самопроизвольная пульсирующая боль, усиление ночью",
        ["DG-001", "DG-002", "EN-003"],
    ),
    (
        2,
        "Хронический периодонтит 11 зуба",
        "Распломбировка каналов, медикаментозная обработка, перелечивание",
        "Дискомфорт при накусывании, ранее леченный зуб",
        ["DG-001", "DG-004", "EN-004"],
    ),
    (
        6,
        "Ретинированный зуб мудрости 48",
        "Сложное удаление с выкраиванием лоскута, наложение швов",
        "Боль и отёк в области нижней челюсти справа",
        ["DG-001", "DG-003", "SU-003"],
    ),
    (
        11,
        "Хронический генерализованный гингивит",
        "Профессиональная гигиена, антисептические аппликации, обучение гигиене",
        "Кровоточивость дёсен при чистке зубов",
        ["DG-001", "HG-001", "PA-001"],
    ),
    (
        4,
        "Скол угла 21 зуба",
        "Художественная реставрация композитом",
        "Косметический дефект после травмы",
        ["DG-001", "DG-002", "TH-004"],
    ),
    (
        5,
        "Полное отсутствие 46 зуба",
        "Двухэтапная имплантация: установка импланта Straumann",
        "Жалобы на отсутствие жевательного зуба",
        ["DG-001", "DG-004", "IM-001"],
    ),
    (
        5,
        "Установка постоянной коронки на имплантат 46",
        "Фиксация металлокерамической коронки на абатменте",
        "Плановый этап после остеоинтеграции",
        ["DG-001", "IM-002", "IM-003"],
    ),
    (
        4,
        "Дистальный прикус, скученность фронтальной группы зубов",
        "Установка металлической брекет-системы на верхнюю и нижнюю челюсть",
        "Эстетическая неудовлетворённость, нарушение прикуса",
        ["OD-001", "DG-003", "OD-002"],
    ),
    (
        4,
        "Плановая коррекция ортодонтического аппарата",
        "Активация брекетов, замена дуги",
        "Плановый визит, лечение брекетами",
        ["OD-003"],
    ),
    (
        12,
        "Глубокий кариес 75 зуба (молочный)",
        "Лечение под аппликационной анестезией, цветная пломба",
        "Жалобы со слов мамы на боль при еде",
        ["DG-001", "PD-001"],
    ),
    (
        13,
        "Профилактический осмотр ребёнка",
        "Серебрение очагов начального кариеса, рекомендации по гигиене",
        "Плановый осмотр",
        ["DG-001", "PD-002", "PD-003"],
    ),
    (
        0,
        "Хронический локализованный пародонтит лёгкой степени",
        "Закрытый кюретаж, шинирование подвижных зубов 31, 32, 41, 42",
        "Подвижность нижних резцов, оголение шеек",
        ["DG-001", "DG-003", "PA-002", "PA-003"],
    ),
    (
        3,
        "Эстетическая реставрация фронтальной группы зубов",
        "Препарирование 11, 12, 21, 22 под виниры, временные накладки",
        "Изменение цвета и формы передних зубов",
        ["DG-001", "OR-003"],
    ),
    (
        9,
        "Профессиональная гигиена полости рта",
        "Ультразвуковая чистка, Air Flow, полировка, фторирование",
        "Профилактический визит каждые 6 месяцев",
        ["HG-001", "HG-002"],
    ),
    (
        2,
        "Острый гнойный периостит от 36 зуба",
        "Удаление 36, разрез по переходной складке, дренирование, антибиотикотерапия",
        "Сильная боль, отёк щеки, температура 37.8",
        ["DG-001", "DG-002", "SU-002"],
    ),
    (
        10,
        "Подозрение на кисту в области 22 зуба",
        "Резекция верхушки корня с цистэктомией",
        "Свищевой ход, дискомфорт при пальпации",
        ["DG-001", "DG-004", "SU-004"],
    ),
    (
        8,
        "Дефект зубного ряда нижней челюсти",
        "Изготовление частичного съёмного пластиночного протеза",
        "Затруднение при жевании",
        ["DG-001", "DG-003", "OR-004"],
    ),
    (
        14,
        "Дистальный прикус, II класс по Энглю",
        "Консультация ортодонта, план лечения брекет-системой",
        "Эстетический дефект, выпирание верхних резцов",
        ["OD-001", "DG-003"],
    ),
    (
        7,
        "Гиперестезия твёрдых тканей зубов на фоне беременности",
        "Профессиональная гигиена, реминерализующая терапия",
        "Чувствительность зубов на холодное",
        ["DG-001", "HG-001", "HG-002"],
    ),
]


def _build_dsn(settings: Settings) -> str:
    return (
        f"{settings.db_driver}://{settings.db_user}:{settings.db_password}"
        f"@{settings.db_host}:{settings.db_port}/{settings.db_name}"
    )


async def seed() -> None:
    settings = Settings()  # type: ignore[call-arg]
    engine = create_async_engine(_build_dsn(settings))
    sessionmaker = async_sessionmaker(engine, expire_on_commit=False)

    async with sessionmaker() as session:
        root_user = (
            await session.execute(select(User).where(User.email == ROOT_EMAIL))
        ).scalar_one_or_none()
        if root_user is None:
            raise RuntimeError(
                f"Root user {ROOT_EMAIL!r} not found — run migrations first"
            )

        await session.execute(delete(medical_record_procedures))
        await session.execute(delete(MedicalRecord))
        await session.execute(delete(Procedure))
        await session.execute(delete(ProcedureCategory))
        await session.execute(delete(Patient))
        await session.execute(delete(Log))
        await session.execute(delete(User).where(User.email != ROOT_EMAIL))
        await session.commit()
        print("Wiped non-root users, patients, records, procedures, categories, logs")

        new_users: list[User] = []
        for u in USERS:
            user = User(
                id=str(ULID()),
                username=u["username"],
                first_name=u["first_name"],
                last_name=u["last_name"],
                email=u["email"],
                role=UserRole(u["role"]),
                is_active=True,
                password_hash=PasswordHasher.hash_password(u["password"]),
            )
            session.add(user)
            new_users.append(user)
        await session.commit()
        print(f"Inserted {len(new_users)} users")

        cats: dict[str, ProcedureCategory] = {}
        for code, name, desc in CATEGORIES:
            cat = ProcedureCategory(
                id=str(ULID()),
                code=code,
                name=name,
                description=desc,
                is_active=True,
            )
            session.add(cat)
            cats[code] = cat
        await session.commit()
        print(f"Inserted {len(cats)} categories")

        procs: dict[str, Procedure] = {}
        for cat_code, code, name, desc, price in PROCEDURES:
            proc = Procedure(
                id=str(ULID()),
                code=code,
                name=name,
                description=desc,
                category_id=cats[cat_code].id,
                default_price=Decimal(price),
                is_active=True,
            )
            session.add(proc)
            procs[code] = proc
        await session.commit()
        print(f"Inserted {len(procs)} procedures")

        patient_list: list[Patient] = []
        for first, last, gender, dob, passport, phone, notes in PATIENTS:
            patient = Patient(
                id=str(ULID()),
                first_name=first,
                last_name=last,
                gender=gender,
                date_of_birth=date.fromisoformat(dob),
                passport_number=passport,
                phone_number=phone,
                notes=notes,
                last_visit=date.today() - timedelta(days=random.randint(1, 60)),
            )
            session.add(patient)
            patient_list.append(patient)
        await session.commit()
        print(f"Inserted {len(patient_list)} patients")

        random.seed(RANDOM_SEED)
        creators = [root_user, *new_users]
        for patient_idx, diag, treat, complaint, codes in RECORDS:
            record = MedicalRecord(
                id=str(ULID()),
                patient_id=patient_list[patient_idx].id,  # type: ignore
                diagnosis=diag,
                treatment=treat,
                chief_complaint=complaint,
                creator_id=random.choice(creators).id,
                created_at=datetime.now() - timedelta(days=random.randint(0, 90)),
            )
            session.add(record)
            await session.flush()
            for code in dict.fromkeys(codes):
                await session.execute(
                    medical_record_procedures.insert().values(
                        medical_record_id=record.id,
                        procedure_id=procs[code].id,
                    )
                )
        await session.commit()
        print(f"Inserted {len(RECORDS)} medical records")

    await engine.dispose()


if __name__ == "__main__":
    random.seed(RANDOM_SEED)
    asyncio.run(seed())
