import os
import unittest

TEST_DB = "test_techrepair.db"
os.environ["TECHREPAIR_DB"] = TEST_DB

import data_access as dal
dal.DB_NAME = TEST_DB

import business_logic as bl


class TestValidation(unittest.TestCase):
    def test_valid_datetime(self):
        self.assertTrue(bl.validation_check("01.01.2026 10:00"))

    def test_invalid_datetime(self):
        self.assertFalse(bl.validation_check("2026-01-01"))


class TestAppointmentService(unittest.TestCase):
    def setUp(self):

        if os.path.exists(TEST_DB):
            os.remove(TEST_DB)
        dal.init_db()
        self.service = bl.AppointmentService()

    def test_book_success(self):

        self.service.book_appointment(1, 1, "01.01.2026 10:00")

        rows = self.service.get_appointments()
        self.assertEqual(len(rows), 1)

    def test_book_specialist_busy(self):
        self.service.book_appointment(1, 1, "01.01.2026 10:00")
        with self.assertRaises(bl.SpecialistNotAvailableError):
            self.service.book_appointment(2, 1, "01.01.2026 10:00")

    def test_book_empty_fields(self):
        with self.assertRaises(bl.ValidationError):
            self.service.book_appointment("", 1, "01.01.2026 10:00")

    def test_book_bad_datetime_format(self):
        with self.assertRaises(bl.ValidationError):
            self.service.book_appointment(1, 1, "2026-01-01")


class TestOrderService(unittest.TestCase):
    def setUp(self):
        if os.path.exists(TEST_DB):
            os.remove(TEST_DB)
        dal.init_db()
        self.service = bl.OrderService()

    def test_order_no_discount(self):
        name, total = self.service.calculate_order(1, 5)
        self.assertEqual(total, 500.0 * 5)

    def test_order_with_discount(self):
        name, total = self.service.calculate_order(1, 10)
        self.assertAlmostEqual(total, 500.0 * 10 * 0.9)

    def test_order_product_not_found(self):
        with self.assertRaises(bl.ValidationError):
            self.service.calculate_order(999, 1)

    def test_order_insufficient_stock(self):
        with self.assertRaises(bl.InsufficientStockError):
            self.service.calculate_order(1, 999)


if __name__ == "__main__":
    unittest.main()