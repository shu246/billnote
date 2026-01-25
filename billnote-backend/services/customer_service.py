from models.customer import Customer

# 仮の顧客データ（後でDynamoDBに置き換える）
fake_customers = []

def create_customer(customer: Customer):
    fake_customers.append(customer)
    return customer

def list_customers():
    return fake_customers
