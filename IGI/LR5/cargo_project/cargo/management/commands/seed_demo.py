"""Populate the database with demo data (10+ rows per table)."""
import io
import random
from datetime import date, datetime, timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils import timezone
from PIL import Image, ImageDraw, ImageFont


def _make_image(text: str, bg: tuple, size=(400, 260)) -> ContentFile:
    """Generate a simple PNG image with a colored background and label."""
    img = Image.new('RGB', size, color=bg)
    draw = ImageDraw.Draw(img)
    # draw a lighter inner rectangle as a border
    draw.rectangle([8, 8, size[0]-9, size[1]-9], outline=(255, 255, 255, 180), width=2)
    # try to use a basic font; fall back to default if unavailable
    try:
        font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 22)
    except Exception:
        font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((size[0] - tw) // 2, (size[1] - th) // 2), text, fill=(255, 255, 255), font=font)
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    return ContentFile(buf.getvalue())

from cargo.models import (
    BodyType, CargoType, Client, Driver, Order, Organization, Service,
    Vehicle, VehicleType,
)
from main.models import (
    CompanyInfo, Contact, FAQ, News, PromoCode, Review, Vacancy,
)
from users.models import UserProfile


def _phone(idx):
    return f'+375 (29) {100+idx:03d}-{idx:02d}-{idx:02d}'


class Command(BaseCommand):
    help = 'Seed demo data — 10+ records in each table'

    def handle(self, *args, **opts):
        self.stdout.write('Seeding demo data...')

        # --- Vehicle, body, cargo dictionaries ---
        vt_data = ['Грузовик', 'Фургон', 'Тягач', 'Самосвал', 'Бортовой',
                   'Рефрижератор', 'Автоцистерна', 'Микроавтобус']
        for name in vt_data:
            VehicleType.objects.get_or_create(name=name)

        bt_data = ['Тентованный', 'Изотермический', 'Открытый бортовой',
                   'Самосвальный', 'Цистерна', 'Контейнерный',
                   'Рефрижератор', 'Закрытый']
        for name in bt_data:
            BodyType.objects.get_or_create(name=name)

        ct_data = [
            ('Продукты питания', False), ('Бытовая техника', False),
            ('Стройматериалы', False), ('Мебель', False),
            ('Топливо', True), ('Химия', True), ('Одежда', False),
            ('Электроника', False), ('Сыпучие грузы', False), ('Медикаменты', False),
            ('Скоропортящиеся', False), ('Авто', False),
        ]
        for name, dang in ct_data:
            CargoType.objects.get_or_create(name=name, defaults={'is_dangerous': dang})

        # --- Organizations ---
        for i in range(1, 11):
            Organization.objects.get_or_create(
                inn=f'19000000{i:02d}',
                defaults=dict(
                    name=f'ООО «ТрансКом-{i}»',
                    legal_address=f'г. Минск, ул. Магистральная, {i}',
                    phone=_phone(i),
                    email=f'org{i}@example.com',
                ),
            )

        # --- Drivers (with users) ---
        first_names = ['Иван', 'Пётр', 'Андрей', 'Сергей', 'Дмитрий',
                       'Алексей', 'Михаил', 'Николай', 'Виктор', 'Олег',
                       'Артём', 'Владимир']
        last_names = ['Иванов', 'Петров', 'Сидоров', 'Кузнецов', 'Смирнов',
                      'Соколов', 'Попов', 'Лебедев', 'Козлов', 'Новиков',
                      'Морозов', 'Волков']

        for i in range(10):
            uname = f'driver{i+1}'
            user, created = User.objects.get_or_create(
                username=uname,
                defaults=dict(
                    email=f'{uname}@example.com',
                    first_name=first_names[i],
                    last_name=last_names[i],
                ),
            )
            if created:
                user.set_password('passdriver123')
                user.save()
            if not hasattr(user, 'profile'):
                UserProfile.objects.create(
                    user=user, role=UserProfile.ROLE_DRIVER,
                    phone=_phone(20 + i),
                    birth_date=date(1990 - i, (i % 12) + 1, (i % 27) + 1),
                    timezone='Europe/Minsk',
                )
            Driver.objects.get_or_create(
                user=user,
                defaults=dict(
                    first_name=first_names[i],
                    last_name=last_names[i],
                    birth_date=date(1990 - i, (i % 12) + 1, (i % 27) + 1),
                    phone=_phone(20 + i),
                    license_number=f'AB{1000+i*7}BY',
                    hired_at=date(2020 + (i % 4), 5, 15),
                ),
            )

        # --- Vehicles ---
        vt_list = list(VehicleType.objects.all())
        bt_list = list(BodyType.objects.all())
        drivers = list(Driver.objects.all())
        brands_models = [
            ('MAN', 'TGS'), ('Volvo', 'FH'), ('Scania', 'R'),
            ('MAZ', '5440'), ('DAF', 'XF'), ('Mercedes', 'Actros'),
            ('Iveco', 'Stralis'), ('Renault', 'T'), ('KAMAZ', '5490'),
            ('Ford', 'Cargo'), ('Hyundai', 'Mighty'), ('Isuzu', 'NQR'),
        ]
        for i, (brand, model) in enumerate(brands_models):
            Vehicle.objects.get_or_create(
                plate_number=f'AB{1234+i}-7',
                defaults=dict(
                    brand=brand, model=model,
                    vehicle_type=vt_list[i % len(vt_list)],
                    body_type=bt_list[i % len(bt_list)],
                    capacity_tons=Decimal(str(round(3 + i * 1.5, 2))),
                    year=2018 + (i % 6),
                    driver=drivers[i % len(drivers)] if i < len(drivers) else None,
                ),
            )

        # --- Clients (with users) ---
        orgs = list(Organization.objects.all())
        cl_first = ['Анна', 'Мария', 'Светлана', 'Ольга', 'Татьяна',
                    'Елена', 'Наталья', 'Юлия', 'Дарья', 'Алина',
                    'Карина', 'Полина']
        cl_last = ['Смирнова', 'Иванова', 'Кузнецова', 'Попова', 'Соколова',
                   'Лебедева', 'Козлова', 'Новикова', 'Морозова', 'Петрова',
                   'Волкова', 'Соловьёва']
        for i in range(11):
            uname = f'client{i+1}'
            user, created = User.objects.get_or_create(
                username=uname,
                defaults=dict(
                    email=f'{uname}@example.com',
                    first_name=cl_first[i],
                    last_name=cl_last[i],
                ),
            )
            if created:
                user.set_password('passclient123')
                user.save()
            if not hasattr(user, 'profile'):
                UserProfile.objects.create(
                    user=user, role=UserProfile.ROLE_CLIENT,
                    phone=_phone(50 + i),
                    birth_date=date(1985 + i, ((i + 2) % 12) + 1, (i % 27) + 1),
                    timezone='Europe/Minsk',
                )
            Client.objects.get_or_create(
                user=user,
                defaults=dict(
                    first_name=cl_first[i],
                    last_name=cl_last[i],
                    birth_date=date(1985 + i, ((i + 2) % 12) + 1, (i % 27) + 1),
                    phone=_phone(50 + i),
                    organization=orgs[i % len(orgs)] if i % 2 == 0 else None,
                ),
            )

        # --- Services ---
        cargoes = list(CargoType.objects.all())
        svc_data = [
            ('Перевозка тентованным грузовиком', '8.50', False),
            ('Перевозка изотермическим фургоном', '12.00', False),
            ('Перевозка контейнера 20ft', '15.00', False),
            ('Перевозка рефрижератором', '18.50', False),
            ('Перевозка сыпучих грузов', '7.20', False),
            ('Доставка опасных грузов (ADR)', '25.00', False),
            ('Экспресс-доставка', '14.30', False),
            ('Грузчик в комплекте', '5.00', True),
            ('Страховка груза', '2.50', True),
            ('Сопровождение охраной', '11.00', True),
            ('Упаковка груза', '4.50', True),
            ('Подъём на этаж', '3.50', True),
        ]
        for name, price, is_add in svc_data:
            svc, created = Service.objects.get_or_create(
                name=name,
                defaults=dict(
                    description=f'Услуга: {name}.',
                    price_per_km=Decimal(price),
                    is_additional=is_add,
                ),
            )
            if created:
                svc.suitable_cargo.set(random.sample(cargoes, k=min(4, len(cargoes))))

        # --- PromoCodes ---
        today = date.today()
        promos_def = [
            ('WELCOME10', 10, False), ('SUMMER15', 15, False),
            ('CARGO20', 20, False), ('BIG30', 30, False),
            ('LOYAL5', 5, False), ('SPRING12', 12, False),
            ('FREIGHT25', 25, False), ('NEW5', 5, False),
            ('OLD2022', 20, True), ('OLD2023', 25, True),
            ('OLDWINTER', 10, True),
        ]
        for code, disc, arch in promos_def:
            PromoCode.objects.get_or_create(
                code=code,
                defaults=dict(
                    discount_percent=disc,
                    description=f'Промокод {code}',
                    valid_from=today - timedelta(days=30),
                    valid_to=today + (timedelta(days=-10) if arch else timedelta(days=60)),
                    is_archived=arch,
                ),
            )

        # --- Orders ---
        clients = list(Client.objects.all())
        drivers = list(Driver.objects.all())
        vehicles = list(Vehicle.objects.all())
        services = list(Service.objects.all())
        cargoes = list(CargoType.objects.all())
        promos_active = list(PromoCode.objects.filter(is_archived=False))
        statuses = [s[0] for s in Order.STATUS_CHOICES]

        if not Order.objects.exists():
            for i in range(12):
                ord_obj = Order.objects.create(
                    client=clients[i % len(clients)],
                    driver=drivers[i % len(drivers)],
                    vehicle=vehicles[i % len(vehicles)],
                    cargo_type=cargoes[i % len(cargoes)],
                    cargo_name=f'Заказ-партия №{i+1}',
                    distance_km=Decimal(str(50 + i * 35)),
                    weight_tons=Decimal(str(1 + i * 0.7)),
                    status=statuses[i % len(statuses)],
                    promo_code=promos_active[i % len(promos_active)] if i % 3 == 0 else None,
                    scheduled_at=timezone.now() + timedelta(days=(i - 3)),
                )
                ord_obj.services.set(
                    random.sample(services, k=min(3, len(services)))
                )

        _news_colors = [
            (220, 38, 38), (37, 99, 235), (5, 150, 105), (124, 58, 237),
            (217, 119, 6), (14, 116, 144), (190, 18, 60), (21, 128, 61),
            (29, 78, 216), (180, 83, 9),
        ]
        _contact_colors = [
            (55, 65, 81), (79, 70, 229), (6, 95, 70), (91, 33, 182),
            (153, 27, 27), (15, 23, 42), (20, 83, 45), (126, 29, 230),
            (30, 64, 175), (146, 64, 14),
        ]

        # --- Site-wide info ---
        if not CompanyInfo.objects.exists():
            info = CompanyInfo(
                title='О компании CargoGo',
                text='Мы занимаемся грузоперевозками автотранспортом по всей Беларуси и за её пределами.',
                history='2018 — основание компании.\n2020 — открытие филиала в Гомеле.\n2023 — собственный парк >100 машин.',
                requisites='УНП 190000001\nр/с BY00 ALFA 3012 5555 5555 5555 5555\nЮр. адрес: г. Минск, ул. Магистральная, 1',
            )
            info.save()
            info.logo.save('company/logo.png', _make_image('CargoGo', (37, 99, 235)), save=True)
        else:
            info = CompanyInfo.objects.first()
            if not info.logo:
                info.logo.save('company/logo.png', _make_image('CargoGo', (37, 99, 235)), save=True)

        contacts_data = [
            ('Иванов Иван Иванович', 'Директор', 'Общее руководство', _phone(70), 'director@cargo.example'),
            ('Петрова Анна Сергеевна', 'Главный бухгалтер', 'Финансы и отчётность', _phone(71), 'accounting@cargo.example'),
            ('Сидоров Алексей Петрович', 'Логист', 'Маршруты и расписание', _phone(72), 'logistics@cargo.example'),
            ('Кузнецова Мария Ивановна', 'HR-менеджер', 'Подбор персонала', _phone(73), 'hr@cargo.example'),
            ('Смирнов Дмитрий Олегович', 'Технический директор', 'Парк ТС', _phone(74), 'tech@cargo.example'),
            ('Попова Ольга Викторовна', 'Менеджер по работе с клиентами', 'Сопровождение клиентов', _phone(75), 'sales@cargo.example'),
            ('Соколов Виктор Андреевич', 'Юрист', 'Договоры и претензии', _phone(76), 'legal@cargo.example'),
            ('Лебедев Андрей Сергеевич', 'IT-специалист', 'Поддержка IT-систем', _phone(77), 'it@cargo.example'),
            ('Козлов Сергей Иванович', 'Главный механик', 'Ремонт техники', _phone(78), 'service@cargo.example'),
            ('Новикова Юлия Александровна', 'Маркетолог', 'Продвижение услуг', _phone(79), 'marketing@cargo.example'),
        ]
        for i, (fn, pos, descr, ph, em) in enumerate(contacts_data):
            contact, _ = Contact.objects.get_or_create(
                full_name=fn,
                defaults=dict(position=pos, description=descr, phone=ph, email=em),
            )
            if not contact.photo:
                initials = ''.join(p[0] for p in fn.split()[:2])
                contact.photo.save(
                    f'contacts/contact_{i}.png',
                    _make_image(initials, _contact_colors[i % len(_contact_colors)], size=(200, 200)),
                    save=True,
                )

        faqs = [
            ('Что такое грузоперевозка?', 'Это услуга по доставке груза автомобильным транспортом.'),
            ('Как рассчитывается стоимость?', 'Стоимость = расстояние × цена за км по выбранным услугам.'),
            ('Что такое ADR?', 'Соглашение о международной перевозке опасных грузов.'),
            ('Какие документы нужны?', 'ТТН, договор, паспорт груза.'),
            ('Что такое сборный груз?', 'Партия от нескольких отправителей в одной машине.'),
            ('Можно ли застраховать груз?', 'Да, через нашу услугу «Страховка груза».'),
            ('Что значит «тент»?', 'Грузовик с тентованным закрытым кузовом.'),
            ('Что такое рефрижератор?', 'Авто с холодильной установкой для скоропорта.'),
            ('Можно ли отслеживать груз?', 'Да, в личном кабинете отображается статус заказа.'),
            ('Доставка по выходным?', 'Да, при срочной доставке возможна доставка 24/7.'),
            ('Что входит в услугу «грузчик»?', 'Погрузка и разгрузка силами наших грузчиков.'),
        ]
        for q, a in faqs:
            FAQ.objects.get_or_create(question=q, defaults={'answer': a})

        vacancies = [
            ('Водитель категории C', 'Опыт от 3 лет, опыт международных перевозок приветствуется.', '2500.00'),
            ('Водитель-экспедитор', 'Доставка по РБ.', '1800.00'),
            ('Логист', 'Опыт работы с TMS.', '2200.00'),
            ('Механик СТО', 'Ремонт грузового транспорта.', '2100.00'),
            ('Менеджер по продажам', 'Активная работа с клиентами.', '1700.00'),
            ('Кладовщик', 'Склад в Минске.', '1400.00'),
            ('Бухгалтер', 'Опыт от 2 лет.', '1900.00'),
            ('Грузчик', 'Полная занятость.', '1100.00'),
            ('Диспетчер', 'Сменный график.', '1600.00'),
            ('IT-специалист', 'Поддержка 1С и сайта.', '2400.00'),
        ]
        for t, d, s in vacancies:
            Vacancy.objects.get_or_create(
                title=t,
                defaults=dict(description=d, salary=Decimal(s), is_active=True),
            )

        # --- Reviews (need users; use existing clients) ---
        users_for_reviews = list(User.objects.filter(profile__role='client'))[:10]
        review_texts = [
            ('Очень доволен сервисом, доставили быстро и в срок.', 5),
            ('Хорошая цена, рекомендую.', 4),
            ('Менеджер вежливый, ответил на все вопросы.', 5),
            ('Доставка немного задержалась, но в целом ок.', 3),
            ('Отличный сервис!', 5),
            ('Спасибо за оперативность.', 5),
            ('Удобный личный кабинет.', 4),
            ('Можно было бы быстрее, но всё на уровне.', 4),
            ('Постоянно пользуюсь — нравится.', 5),
            ('Хорошее соотношение цена/качество.', 4),
        ]
        for u, (text, rating) in zip(users_for_reviews, review_texts):
            Review.objects.get_or_create(
                author=u, text=text, defaults={'rating': rating}
            )

        # --- News ---
        news_titles = [
            'Открыли филиал в Бресте', 'Расширили автопарк',
            'Новая услуга — экспресс-доставка', 'Скидки на перевозки в марте',
            'Получили сертификат ISO 9001', 'Открыли вакансии для водителей',
            'Запустили личный кабинет', 'Поездки в ЕС возобновлены',
            'Подписали договор с крупным сетевым ритейлером',
            'Обновили парк рефрижераторов',
        ]
        for i, title in enumerate(news_titles):
            news_obj, _ = News.objects.get_or_create(
                title=title,
                defaults=dict(
                    summary=f'Кратко: {title.lower()}.',
                    content=f'Полный текст новости «{title}». Подробности — в статье.',
                    published_at=timezone.now() - timedelta(days=i * 3),
                ),
            )
            if not news_obj.image:
                news_obj.image.save(
                    f'news/news_{i}.png',
                    _make_image(f'№{i+1}', _news_colors[i % len(_news_colors)]),
                    save=True,
                )

        self.stdout.write(self.style.SUCCESS('Demo data seeded.'))
