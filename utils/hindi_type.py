def get_hindi_type(tx_type):
    return {
        "purchase": "खरीद",
        "payment_give": "नकद दी गई राशि/बाकी",
        "payment_take": "नकद किसान द्वारा/देना",
        "add_balance": "हफ़्ता",
        "settled": "खाता सेटल"
    }.get(tx_type, tx_type)