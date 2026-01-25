from models.invoice import Invoice
# 仮の請求書データ（後でDynamoDBに置き換える）
fake_invoices = []

def create_invoice(invoice: Invoice):
    fake_invoices.append(invoice)
    return invoice

def list_invoices():
    return fake_invoices
