def run(items: list, declared_total: int) -> dict:
    """
    経費明細の合計金額を検証する。

    Args:
        items: [{"name": "新幹線往復", "amount": 28000}, ...]
        declared_total: 申請者が記載した合計金額（整数）

    Returns:
        calculated_total: 明細から計算した合計金額
        declared_total: 申請書に記載された合計金額
        matched: 一致していれば True
        diff: declared_total - calculated_total（正なら申請額が多い、負なら少ない）
    """
    calculated = sum(item["amount"] for item in items)
    matched = calculated == declared_total
    return {
        "calculated_total": calculated,
        "declared_total": declared_total,
        "matched": matched,
        "diff": declared_total - calculated,
    }
