from database import cursor, db

class UserModel:
    @staticmethod
    def get_user_by_id(user_id):
        cursor.execute("SELECT * FROM users WHERE id=%s", (user_id,))
        return cursor.fetchone()

    @staticmethod
    def get_user_by_email(email):
        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        return cursor.fetchone()

class ServiceModel:
    @staticmethod
    def get_service_by_id(service_id):
        cursor.execute("SELECT * FROM services WHERE id=%s", (service_id,))
        return cursor.fetchone()

    @staticmethod
    def get_provider_services(provider_id):
        cursor.execute("SELECT * FROM services WHERE provider_id=%s", (provider_id,))
        return cursor.fetchall()

class BookingModel:
    @staticmethod
    def get_booking_by_id(booking_id):
        cursor.execute("SELECT * FROM bookings WHERE id=%s", (booking_id,))
        return cursor.fetchone()

    @staticmethod
    def update_booking_status(booking_id, status):
        cursor.execute("UPDATE bookings SET status=%s WHERE id=%s", (status, booking_id))
        db.commit()