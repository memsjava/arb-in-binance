from email.policy import default
from enum import unique
from peewee import *
from regex import E

db = SqliteDatabase('tahiry.sqlite')


class BaseModel(Model):

    class Meta:
        database = db


class Pair(BaseModel):
    paire = CharField(unique=False)
    side = CharField(unique=False)
    price = DecimalField(decimal_places=5)
    amount = DecimalField(decimal_places=5, default=0)
    order_id = CharField(unique=False, null=True)
    is_active = BooleanField(default=False)
    is_succeed = BooleanField(default=False)


class Tahiry(BaseModel):
    voalohany_ = ForeignKeyField(Pair, backref='voalohany', default=None)
    faharoa_ = ForeignKeyField(Pair, backref='faharoa', default=None)
    fahatelo_ = ForeignKeyField(Pair, backref='fahatelo', default=None)


class dbManager():
    '''
    if there is an order in first pair
    
    '''

    def __init__(self):
        self._order_number = 0
        self.connect_db()

    def ignore_current_arb(self):
        pair, err = self.getActiveOrder()
        pair.is_active = False
        pair.save()
        return pair, err

    def connect_db(self):
        try:
            db.connect()
        except:
            pass
        try:
            db.create_tables([Pair, Tahiry])
        except:
            pass

    def check_written_db(self):
        try:
            sel = Tahiry.select()
            sel.get()
            return True
        except:
            return False

    '''
    set orders and list 
    to_store = [{
        "paire": "REIUSDT",
        "side": "buy",
        "price": 0.0405,
        "amount": 1233.3333333333333
        }, {
        "paire": "REIBUSD",
        "side": "buy",
        "price": 0.0407,
        "amount":0
        },{
        "paire": "BUSDUSDT",
        "side": "sell",
        "price": 1.0011,
        "amount":0
        },
    ]
    
    '''

    def set_orders(self, list_orders):
        orders, error = None, None
        tahirys = []
        try:
            for order in list_orders:
                tahirys.append(
                    Pair.create(
                        paire=order['paire'],
                        side=order['side'],
                        price=order['price'],
                        amount=order['amount'],
                    ))
            orders = Tahiry.create(voalohany_=tahirys[0],
                                   faharoa_=tahirys[1],
                                   fahatelo_=tahirys[2])
        except Exception as e:
            error = e
        return orders, error

    def getActiveOrder(self):
        res, err = None, None
        try:
            res = Pair.get(Pair.is_active == True)
        except Exception as e:
            err = e
        return res, err

    def updateAndSwitchOrder(self):
        res, err = None, None
        try:
            active_pair = Pair.get(Pair.is_active == True)
            try:
                t = Tahiry.get(Tahiry.voalohany_ == active_pair)
                res = t.faharoa_
            except:
                pass
            if not res:
                try:
                    t = Tahiry.get(Tahiry.faharoa_ == active_pair)
                    res = t.fahatelo_
                except:
                    pass
                    #delete
        except Exception as e:
            err = e
            print(err)
        return res, err

    def closeLastOrder(self):
        active_pair = Pair.get(Pair.is_active == True)
        try:
            Tahiry.get(Tahiry.fahatelo_ == active_pair)
            active_pair.is_active = False
            active_pair.save()
        except Exception as e:
            print(e)
