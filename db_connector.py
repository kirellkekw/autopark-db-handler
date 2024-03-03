from sqlalchemy import create_engine, Column, Integer, String, Float, SMALLINT
from sqlalchemy.orm import declarative_base, Session
import datetime

# db in the same directory as the script
_db_string = 'sqlite:///autopark_database.db'

if _db_string is None:
    raise ValueError("DATABASE_URL environment variable is not set")

# Create the database engine
_engine = create_engine(_db_string)


def create_session():
    """Creates a new session for the database. Close the session when done by calling session.close()."""
    return Session(bind=_engine)


# base object for all tables
_Base = declarative_base()


class Parking(_Base):
    """Class for creating, updating and deleting parking entries."""
    __tablename__ = "autopark_test_drive"

    id = Column(Integer,
                primary_key=True,
                autoincrement=True,
                nullable=False)
    lot_number = Column(SMALLINT, nullable=False)
    plate_number = Column(String(length=20), nullable=False)
    entry_time = Column(String(length=19), nullable=False,
                        default=datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"))
    exit_time = Column(String(length=19), nullable=True)
    fee = Column(Float, nullable=True)

    def __repr__(self):
        return f"<Parking(id={self.id}, " \
            f"lot_number={self.lot_number}, " \
            f"plate_number={self.plate_number}, " \
            f"entry_time={self.entry_time}, " \
            f"exit_time={self.exit_time}, " \
            f"fee={self.fee})>"

    @staticmethod
    def _wipe():
        """Deletes all entries in the table. Use with caution!"""
        session = create_session()
        passphrase = input("Are you sure you want to wipe the table? (yes/no)")
        if passphrase.lower() == "yes":
            session.query(Parking).delete()
            session.commit()
        else:
            print("Wipe aborted")

        session.close()

    @staticmethod
    def calculate_fee(entry_time: str, exit_time: str, hourly_rate: float = 10.0):
        entry_time = datetime.datetime.strptime(
            entry_time, "%d-%m-%Y %H:%M:%S")
        exit_time = datetime.datetime.strptime(exit_time, "%d-%m-%Y %H:%M:%S")

        time_spent_in_hrs = datetime.timedelta.total_seconds(
            exit_time - entry_time) / 3600

        fee = time_spent_in_hrs * hourly_rate
        # return fee in 2 decimal places
        return round(fee, 2)

    @staticmethod
    def get(id: int):
        """Returns the parking entry with the given id. If no entry is found, returns None."""
        session = create_session()

        new_entry = session.get(Parking, id)

        session.close()

        return new_entry

    @staticmethod
    def create(lot_number: int,
               plate_number: str,
               entry_time: str = None,
               exit_time: str = None,
               fee: float = None):
        """
        Creates a new parking entry and returns it.

        if `entry_time` is not provided, the current time is used.
        """

        if entry_time is None:  # if entry time is not provided, use current time
            entry_time = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")

        new_entry = Parking(lot_number=lot_number,
                            plate_number=plate_number,
                            entry_time=entry_time,
                            exit_time=exit_time,
                            fee=fee)

        return new_entry

    def modify(id: int,
               lot_number: int = None,
               plate_number: str = None,
               entry_time: str = None,
               exit_time: str = None,
               fee: float = None):
        """
        Modifies the parking entry with the given id.

        if `entry_time` is not provided, the current time is used.
        """

        entry = Parking.get(id)

        if entry is None:
            raise ValueError(f"No entry with id {id} found")

        if lot_number is not None:
            entry.lot_number = lot_number

        if plate_number is not None:
            entry.plate_number = plate_number

        if entry_time is not None:
            entry.entry_time = entry_time

        if exit_time is not None:
            entry.exit_time = exit_time

        if fee is not None:
            entry.fee = fee

        return entry

    @staticmethod
    def delete(id: int):
        """
        Deletes a parking entry with the given id. 
        This is irreversible by session.rollback() by design. Use with caution!
        """

        session = create_session()
        try:
            entry = Parking.get(id)
            session.delete(entry)
            session.commit()
        except Exception as e:
            print(f"Error: {e}")
        finally:
            session.close()

    @staticmethod
    def checkout(id: int, exit_time: str = None, fee: float = None):
        """
        Updates the exit time and fee for a parking entry.

        if `exit_time` is not provided, the current time is used.

        if `fee` is not provided, it is calculated using the entry and exit times.
        """

        entry = Parking.get(id)

        if entry is None:
            raise ValueError(f"No entry with id {id} found")

        if exit_time is None:  # if exit time is not provided, use current time
            exit_time = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")

        if fee is None:  # if fee is not provided, calculate it
            fee = entry.calculate_fee(entry.entry_time, exit_time)

        entry.exit_time = exit_time
        entry.fee = fee

        return entry


# This line has to come after the tables are defined
_Base.metadata.create_all(_engine, checkfirst=True)


if __name__ == "__main__":

    Parking._wipe()  # wipe the table

    session = create_session()

    test2 = Parking.create(lot_number=2, plate_number="ABC1234")

    session.add(test2)

    session.commit()  # before commit you can't get the id

    myobj = Parking.get(test2.id)

    print(myobj)

    session.close()
