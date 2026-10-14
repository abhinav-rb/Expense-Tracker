from datetime import date


class Expense:
    def __init__(self, id: int, description: str, amount: float, date: date, category: str = "General"):
        self.id = id
        self.description = description
        self.amount = amount
        self.date = date
        self.category = category

    def to_Dict(self):
        return {
            "id": self.id,
            "description": self.description,
            "amount": self.amount,
            "date": self.date.isoformat(),
            "category": self.category,
        }

    @classmethod
    def from_Dict(cls, data: dict):
        return cls(
            id=data["id"],
            description=data["description"],
            amount=data["amount"],
            date=date.fromisoformat(data["date"]),
            category=data.get("category", "General"),
        )