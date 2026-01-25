import boto3

def analize_invoice(file_path: str):
    textract = boto3.client("textract")

    with open(file_path, "rb") as document:
        image_bytes = document.read()

    response = textract.analyze_expense(Document={"Bytes": image_bytes})    

    extracted = {
        "customer_name": None,
        "date": None,
        "address": None,
        "phone": None,
    }

    for field in response.get("SummaryFields", []):
        label = field.get("LabelDetection", {}).get("Text", "")
        value = field.get("ValueDetection", {}).get("Text", "")

        #全項目の空白削除（前後のスペース・改行など）
        label = label.strip()
        value = value.strip()

        # 自社情報の除外
        if "坂上" in value or "T6810916438013" in value or "0276-73-8840" in value:
            continue

        # 氏名　（様付きから様削除）
        if "様" in value:
            extractd["customer_name"] = value.replace("様", "").strip()

        # 日付（和暦でも西暦でもOK）
        if "年" in value and "月" in value and "日" in value:
            cleaned_date = convert_japanese_date_to_seireki(value)
            extracted["date"] = cleaned_date

        def convert_japanese_date_to_seireki(date_str: str) -> str:
            # 例: "令和5年1月20日" → "2023-1-20"
            date_str = date_str.strip()

            # 令和
            if date_str.startswith("令和"):
                parts = date_str.replace("令和", "").replace("日", "").split("年")
                year = int(parts[0])
                rest = parts[1].replace("月", "-")
                seireki_year = 2018 + year
                return f"{seireki_year}-{rest}"
            # 平成
            if date_str.startswith("平成"):
                parts = date_str.replace("平成", "").replace("日", "").split("年")
                year = int(parts[0])
                rest = parts[1].replace("月", "-")
                seireki_year = 1988 + year
                return f"{seireki_year}-{rest}"
            # すでに西暦の場合（例: 2026年1月20日）
            if "年" in date_str:
                cleaned = (
                    date_str.replace("年", "-")
                            .replace("月", "-")
                            .replace("日", "")
                )
                return cleaned

            return date_str
        # 住所（ラベルが「住所」）
        if "住所" in label:
            extracted["address"] = value

        # 電話番号（ラベルが「電話番号」）
        if "電話番号" in label.upper():
            extracted["phone"] = value

    return extracted
