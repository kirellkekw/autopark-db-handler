from db_connector import Parking, create_session

session = create_session()

new_parking = Parking.create(lot_number=1, plate_number="ABC123")

session.add(new_parking)

session.commit()

session.close()
