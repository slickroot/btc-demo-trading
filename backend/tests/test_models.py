import unittest
import datetime
from models.db_models import Account, TradeOrder
from models.schemas import TradeRequest, TradeOrderResponse

class TestModels(unittest.TestCase):
    """Test case for data models"""
    
    def test_account_model(self):
        """Test Account model initialization"""
        account = Account(cash_balance=5000.0, btc_balance=0.5)
        self.assertEqual(account.cash_balance, 5000.0)
        self.assertEqual(account.btc_balance, 0.5)
    
    def test_trade_order_model(self):
        """Test TradeOrder model initialization"""
        order = TradeOrder(
            type="buy", 
            amount=0.2, 
            price=45000.0, 
            status="open",
            created_at=datetime.datetime(2025, 3, 1, 12, 0, 0)
        )
        self.assertEqual(order.type, "buy")
        self.assertEqual(order.amount, 0.2)
        self.assertEqual(order.price, 45000.0)
        self.assertEqual(order.status, "open")
        self.assertEqual(order.created_at, datetime.datetime(2025, 3, 1, 12, 0, 0))
        self.assertIsNone(order.closed_at)
    
    def test_trade_request_schema(self):
        """Test TradeRequest Pydantic schema"""
        data = {"type": "buy", "amount": 0.1}
        request = TradeRequest(**data)
        self.assertEqual(request.type, "buy")
        self.assertEqual(request.amount, 0.1)
    
    def test_trade_order_response_schema(self):
        """Test TradeOrderResponse Pydantic schema"""
        created_at = datetime.datetime(2025, 3, 1, 12, 0, 0)
        closed_at = datetime.datetime(2025, 3, 1, 14, 0, 0)
        
        data = {
            "id": 1,
            "type": "buy",
            "amount": 0.1,
            "price": 50000.0,
            "status": "closed",
            "created_at": created_at,
            "closed_at": closed_at
        }
        
        response = TradeOrderResponse(**data)
        self.assertEqual(response.id, 1)
        self.assertEqual(response.type, "buy")
        self.assertEqual(response.amount, 0.1)
        self.assertEqual(response.price, 50000.0)
        self.assertEqual(response.status, "closed")
        self.assertEqual(response.created_at, created_at)
        self.assertEqual(response.closed_at, closed_at)

if __name__ == "__main__":
    unittest.main()
