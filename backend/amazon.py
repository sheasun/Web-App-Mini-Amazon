from socket import socket
from sqlalchemy import and_, func
from db import *
import interface
import world_amazon_pb2 as amazonBuffer
import web_pb2 as webBuffer
import world_ups_pb2 as upsBuffer

class Amazon:
    def __init__(self) -> None:
        '''default constructor
        
        '''
        self.dbSession = create_db_session()

    def connect_to_world(self, worldId: int, warehouseId: int, warehouseX: int, warehouseY: int):
        '''connect an amazon to world
        
        '''
        aConnect = amazonBuffer.AConnect()
        aConnect.worldid = worldId
        aInitWarehouse = aConnect.initwh.add()
        aInitWarehouse.id = warehouseId
        aInitWarehouse.x = warehouseX
        aInitWarehouse.y = warehouseY
        aConnect.isAmazon = True

        interface.send_proto_message(self.worldSocket, aConnect)
        response = interface.received_proto_message(self.worldSocket, amazonBuffer.AConnected)

        return response

    def list_stocks(self, user: Users):
        stocksJson = {}
        stocksJson['product'] = []

        col =  func.abs(Warehouses.location_x - user.location_x) + func.abs(Warehouses.location_y - user.location_y)

        closestWareHouse: Warehouses = self.dbSession.query(Warehouses).order_by(col.asc())

        if(closestWareHouse.count() == 0):
            return stocksJson

        closestWareHouse = closestWareHouse[0]
        print(closestWareHouse.location_x, closestWareHouse.location_y)
       
        stocks = self.dbSession.query(Stocks).filter(Stocks.whid == closestWareHouse.id).order_by(Stocks.item_id)
        for stock in stocks:
            item = self.dbSession.query(Items).filter(Items.id == stock.item_id)[0]

            stockJson = {}
            stockJson['id'] = stock.id
            stockJson['name'] = item.description
            stockJson['count'] = stock.count
            stockJson['warehouseId'] = closestWareHouse.id

            stocksJson['product'].append(stockJson)

        return stocksJson

    def list_cart(self, user):
        stocksJson = {}
        stocksJson['product'] = []

        order = self.dbSession.query(Orders).filter(and_(Orders.user_id == user.id, Orders.status == Status_enum.zero))
        print(order.count())
        if(order.count() == 0):
            return stocksJson

        order: Orders = order[0]
        orderDetails = self.dbSession.query(OrderDetails).filter(OrderDetails.order_id == order.id)
        print("orderDetails:", orderDetails.count())

        for orderDetail in orderDetails:
            stockJson = {}
            stockJson['id'] = orderDetail.item_id
            stockJson['name'] = self.dbSession.query(Items).filter(Items.id == orderDetail.item_id)[0].description
            stockJson['count'] = orderDetail.count
    
            stocksJson['product'].append(stockJson)

        stocksJson['orderId'] = order.id
        
        return stocksJson

    def update_cart(self, user: Users, stockId: int, count: int):
        '''add a item to shopping cart for specific user
        
        '''
        count = int(count)

        stock = self.dbSession.query(Stocks).filter(Stocks.id == stockId)
        if(stock.count() == 0):
            return

        stock = stock[0]
        stock: Stocks = self.dbSession.query(Stocks).filter(Stocks.id == stockId)[0]

        order = self.dbSession.query(Orders).filter(and_(Orders.user_id == user.id, Orders.status == Status_enum.zero))
        orderId = -1

        if(order.count() == 0):
            newOrder = Orders(wh_id=stock.whid, user_id=user.id, status=Status_enum.zero, note="in shopping cart")
            self.dbSession.add(newOrder)
            self.dbSession.flush()
            orderId = newOrder.id
        else:
            orderId = order[0].id

        orderDetail = self.dbSession.query(OrderDetails).filter(
            and_(OrderDetails.order_id == orderId, OrderDetails.item_id == stock.item_id)
        )

        if(orderDetail.count() == 0):
            newOrderDetail = OrderDetails(order_id=orderId, item_id=stock.item_id, count=count)
            self.dbSession.add(newOrderDetail)
        else:
            orderDetail: OrderDetails = orderDetail[0]
            orderDetail.count += count

        stock.count -= count
        self.dbSession.commit()


    def list_deliveries(self, user: Users):
        '''get list of orders for a given user
        
        '''
        ordersJson = {}
        ordersJson['orders'] = []

        orders = self.dbSession.query(Orders).filter(and_(Orders.user_id == user.id, Orders.status != Status_enum.zero))

        if(orders.count() == 0):
            return ordersJson
        
        for order in orders:
            orderJson = {}

            orderJson['id'] = order.id
            orderJson['wh_id'] = order.wh_id
            orderJson['status'] = order.status.value
            orderJson['truck_id'] = order.truck_id
            orderJson['note'] = order.note

            ordersJson['orders'].append(orderJson)

        return ordersJson

    def get_delivery_details(self, orderId: int):
        stocksJson = {}
        stocksJson['product'] = []

        order = self.dbSession.query(Orders).filter(and_(Orders.id == orderId, Orders.status != Status_enum.zero))
        print(order.count())
        if(order.count() == 0):
            return stocksJson

        order = order[0]
        orderDetails = self.dbSession.query(OrderDetails).filter(OrderDetails.order_id == order.id)
        print("orderDetails:", orderDetails.count())

        for orderDetail in orderDetails:
            stockJson = {}
            stockJson['id'] = orderDetail.item_id
            stockJson['name'] = self.dbSession.query(Items).filter(Items.id == orderDetail.item_id)[0].description
            stockJson['count'] = orderDetail.count
    
            stocksJson['product'].append(stockJson)
        
        return stocksJson

    def go_purchase_more(self, stockId: int, amount: int):
        ''' send to user handler to purchase more
        
        '''
        stock = self.dbSession.query(Stocks).filter(Stocks.id == stockId)
        if(stock.count() == 0):
            return
        stock: Stocks = stock[0]

        webCommands = webBuffer.WebCommands()
        webPurchaseMore = webCommands.purchaseMores.add()
        webPurchaseMore.whnum = stock.whid
        webPurchaseMore.itemId = stock.item_id
        webPurchaseMore.count = amount
        
        webSocket: socket = interface.create_socket('web')
        interface.send_proto_message(webSocket, webCommands)

        return

    def go_purchase_new(self, user: Users, description: str, count: int):
        ''' send to user handler to purchase new items 
        
        '''
        col =  func.abs(Warehouses.location_x - user.location_x) + func.abs(Warehouses.location_y - user.location_y)
        closestWareHouse = self.dbSession.query(Warehouses).order_by(col.asc())

        if(closestWareHouse.count() == 0):
            return
        closestWareHouse: Warehouses = closestWareHouse[0]

        webCommands = webBuffer.WebCommands()
        webPurchaseNew = webCommands.newProducts.add()
        webPurchaseNew.whnum = closestWareHouse.id
        webPurchaseNew.description = description
        webPurchaseNew.count = count

        webSocket: socket = interface.create_socket('web')
        interface.send_proto_message(webSocket, webCommands)

        return

    def place_order(self, userId: int, orderId: int):
        ''' send to user handler to place order
        
        '''
        order = self.dbSession.query(Orders).filter(Orders.id == orderId)
        if(order.count() == 0):
            return
        order: Orders = order[0]
        order.status = Status_enum.one
        self.dbSession.commit()

        webCommands = webBuffer.WebCommands()
        webOrder = webCommands.orders.add()
        webOrder.orderID = orderId
        webOrder.userID = userId

        webSocket: socket = interface.create_socket('web')
        interface.send_proto_message(webSocket, webCommands)

        return
