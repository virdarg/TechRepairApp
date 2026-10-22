import os
import unittest

TEST_DB = "test_integration.db"
import data_access as dal
dal.DB_NAME = TEST_DB

import business_logic as bl


class TestIntegrationAppointmentToDB(unittest.TestCase):


    def setUp(self):
        if os.path.exists(TEST_DB):
            os.remove(TEST_DB)
        dal.init_db()
        self.service = bl.AppointmentService()

    def test_appointment_saved_to_db(self):
        self.service.book_appointment(1, 2, "02.02.2026 12:00")
        rows = dal.get_all_appointments()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["specialist_name"], "Витя Коряга")

    def test_duplicate_slot_blocked_by_service(self):
        self.service.book_appointment(1, 1, "03.03.2026 15:00")
        with self.assertRaises(bl.SpecialistNotAvailableError):
            self.service.book_appointment(2, 1, "03.03.2026 15:00")


if __name__ == "__main__":
    unittest.main()