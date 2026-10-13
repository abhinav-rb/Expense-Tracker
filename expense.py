class Expense:
    def __init__(self, id: int, description: str, amount: float, date, category: str):
        self.id = id
        self.description = description
        self.amount = amount
        self.date = date
        self.category = category
    
    def toDict(self):
        return{
            "id": self.id,
            "description": self.description,
            "amount": self.amount,
            "date": str(self.date),
            "category": self.category
        }
    
    #def fromDict(self, data: dict):