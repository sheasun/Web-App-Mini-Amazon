from flask_login import UserMixin
import enum
from sqlalchemy.types import Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import ForeignKey, Column, Integer, String, Text
from sqlalchemy.orm import sessionmaker

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import config

Base = declarative_base()

def create_db_session():
    # dbEngine = create_engine('postgresql://postgres:passw0rd@localhost:5432/ece568_project')
    dbEngine = create_engine('postgresql://{}:{}@{}:{}/{}'.format(
        config.DB_USER, config.DB_PASSWORD, config.DB_HOST, config.DB_PORT, config.DB_SCHEMA)
    )
    dbSession = sessionmaker(bind=dbEngine)()    
    return dbSession
    
class Status_enum(enum.Enum):
    zero = 'cart'
    one = 'packing'
    two = 'packed'
    three = 'loading'
    four = 'loaded'
    five = 'delivering'
    six = 'delivered'

class Users(Base, UserMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(64), unique=True)
    email = Column(String(64))
    password = Column(String(64))
    location_x = Column(Integer)
    location_y = Column(Integer)
    ups_name = Column(String(64), nullable=True)

    def __init__(self, name, email, password, location_x, location_y, ups_name=None):
        self.name = name
        self.email = email
        self.password = password
        self.location_x = location_x
        self.location_y = location_y
        self.ups_name = ups_name

class Warehouses(Base):
    __tablename__ = "warehouses"

    id = Column(Integer, primary_key=True)
    location_x = Column(Integer)
    location_y = Column(Integer)

    def __init__(self, x, y):
        self.location_x = x
        self.location_y = y

class Items(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True)
    description = Column(String(64))

    def __init__(self, description):
        self.description = description

class Stocks(Base):
    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True)
    item_id = Column(Integer)
    count = Column(Integer, default=1)
    whid = Column(Integer, ForeignKey(Warehouses.id))

    def __init__(self, item_id, count, whid):
        self.item_id = item_id
        self.count = count
        self.whid = whid

class Orders(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    wh_id = Column(Integer, ForeignKey(Warehouses.id))
    user_id = Column(Integer, ForeignKey(Users.id))
    status = Column(Enum(Status_enum))
    truck_id = Column(Integer, nullable=True)
    note = Column(Text, nullable=True)

    def __init__(self, wh_id,  user_id, status, truck_id=None, note=None):
        self.wh_id = wh_id
        self.user_id = user_id
        self.truck_id = truck_id
        self.status = status
        self.note = note

class OrderDetails(Base):
    __tablename__ = "order_details"

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey(Orders.id))
    item_id = Column(Integer, ForeignKey(Items.id))
    count = Column(Integer)

    def __init__(self, order_id, item_id, count):
        self.order_id = order_id
        self.item_id = item_id
        self.count = count

def drop_all_tables():
    dbSession = create_db_session()
    dbSession.execute('drop table if exists users, warehouses, items, stocks, orders, order_details cascade')
    dbSession.execute('drop type if exists status_enum')
    dbSession.commit()


def fill_dummy_data():
    dbSession = create_db_session()

    newUser1 = Users(name="anran", email='anran@gmail.com', password='12345678', location_x=20,location_y=15, ups_name='Liz')
    newUser2 = Users(name="shea", email='shea@gmail.com', password='12345678', location_x=20,location_y=15, ups_name='Liz')

    wareHouse1 = Warehouses(x=3, y=10)
    warehouse2 = Warehouses(x=100, y=200)
    
    item1 = Items(description='Iphone 12 Max Pro')
    item2 = Items(description='Dell Inspiron 5577')
    item3 = Items(description='User Type C Charger 12V')
    item4 = Items(description='Emergency Power Adapter 220V ~ AC')

    dbSession.add(newUser1)
    dbSession.add(newUser2)
    dbSession.commit()

    dbSession.add(wareHouse1)    
    dbSession.add(warehouse2)
    dbSession.commit()

    dbSession.add(item1)
    dbSession.add(item2)
    dbSession.add(item3)
    dbSession.add(item4)
    dbSession.commit()


    stock1 = Stocks(whid=wareHouse1.id, item_id=item1.id, count=0)
    stock2 = Stocks(whid=wareHouse1.id, item_id=item2.id, count=0)
    stock3 = Stocks(whid=wareHouse1.id, item_id=item3.id, count=0)
    stock4 = Stocks(whid=wareHouse1.id, item_id=item4.id, count=0)

    stock5 = Stocks(whid=warehouse2.id, item_id=item1.id, count=0)
    stock6 = Stocks(whid=warehouse2.id, item_id=item2.id, count=0)
    stock7 = Stocks(whid=warehouse2.id, item_id=item3.id, count=0)
    stock8 = Stocks(whid=warehouse2.id, item_id=item4.id, count=0)


    dbSession.add(stock1)
    dbSession.add(stock2)
    dbSession.add(stock3)
    dbSession.add(stock4) 
    dbSession.add(stock5)
    dbSession.add(stock6)
    dbSession.add(stock7)
    dbSession.add(stock8)

    dbSession.commit()

def init_db_for_world():
    print("creating tables")

    drop_all_tables()

    dbEngine = create_engine('postgresql://{}:{}@{}:{}/{}'.format(
        config.DB_USER, config.DB_PASSWORD, config.DB_HOST, config.DB_PORT, config.DB_SCHEMA)
    )
    Base.metadata.create_all(dbEngine)

    print("tables created")
    print("adding dummy data")

    fill_dummy_data()
    print("finished adding dummy data")


if __name__ == '__main__':
    init_db_for_world()