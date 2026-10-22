from datetime import datetime
import data_access as dal
import logging

logging.basicConfig(
    filename="techrepair_log.txt",
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    encoding="utf-8"
)


class SpecialistNotAvailableError(Exception):
    pass


class InsufficientStockError(Exception):
    pass


class ValidationError(Exception):
    pass


def validation_check(user_input):
    pattern = '%d.%m.%Y %H:%M'

    try: 
        datetime.strptime(user_input, pattern)
        return True
    except ValueError: 
        return False



class AppointmentService:

    def book_appointment(self, tech_id, specialist_id, datetime_str):
        logging.debug(f"Запись: tech_id={tech_id}, specialist_id={specialist_id}, время={datetime_str}")

        if not tech_id or not specialist_id or not datetime_str:
            raise ValidationError("Все поля должны быть заполнены")
        if datetime_str is None:
            raise ValidationError("Дата и время не указаны")
        if not validation_check(datetime_str):
            raise ValidationError("Неверный формат даты и времени")

        if dal.is_specialist_busy(specialist_id, datetime_str):
            logging.warning(f"Специалист {specialist_id} занят в {datetime_str}")
            raise SpecialistNotAvailableError("Выбранное время занято, выберите другое")

        dal.add_appointment(tech_id, specialist_id, datetime_str)
        logging.info(f"Запись успешно создана: tech={tech_id}, specialist={specialist_id}")
    def get_appointments(self):
        return dal.get_all_appointments()



class OrderService:

    def calculate_order(self, product_id, quantity):
        products = dal.get_all_products()
        product = next((p for p in products if p["id"] == product_id), None)
        if product is None:
            raise ValidationError("Товар не найден")

        if quantity > product["stock"]:
            raise InsufficientStockError(
                f"На складе только {product['stock']} шт. товара '{product['name']}'"
            )

        total = product["price"] * quantity
        if quantity >= 10:
            total = total * 0.9
            logging.info(f"Применена оптовая скидка для товара {product['name']}")

        return product["name"], total