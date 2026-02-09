class Store:
    def __init__(self, product):
        self.product = product


class Bill(Store):
    def purchase(self):
        return f"Bill detail: {self.product}"


class Stock:
    stock = ["Lenin Shirt", "Laptop", "Mobile", "Jeans-Pant"]

    def Check(self, product):  # Fixed parameter usage
        return "Yes It is in Stock" if product in self.stock else "No it is not in Stock"


class Inventory(Stock, Bill):
    def __init__(self, product):
        Stock.__init__(self)  # Pass self!
        Bill.__init__(self, product)  # Initialize Bill (which calls Store)

    def Info(self):
        check_result = self.Check(self.product)
        purchase_result = self.purchase()
        return f"Check: {check_result},   {purchase_result}"


# Test
product = "Lenin Shirt"
obj = Inventory(product)

print("Stock:", obj.stock)
print("Info:", obj.Info())
