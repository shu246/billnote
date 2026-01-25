import pandas as pd
from fpdf import FPDF

def convert_excel_to_pdf(excel_path: str, pdf_path: str):
    # Excelファイルを読み込む
    df = pd.read_excel(excel_path)

    # PDFオブジェクトを作成
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # ヘッダー行（列名）を出力
    header = " | ".join(df.columns)
    pdf.cell(200, 10, txt=header, ln=True)

    # 各行のデータを出力
    for _, row in df.iterrows():
        line = " | ".join(str(cell) for cell in row)
        pdf.cell(200, 10, txt=line, ln=True)

    # PDFファイルとして保存
    pdf.output(pdf_path)
