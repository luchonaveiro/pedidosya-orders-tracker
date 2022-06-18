"Utils functions"

import imaplib
from datetime import datetime
import pandas as pd


def filter_mail_inbox(imap: imaplib.IMAP4_SSL, date_from: str, date_to: str):
    """
    Return INBOX mails IDs from "confirmacion@pedidosya.com for a specified date range

    """
    imap.select("INBOX")
    peya_typ, peya_data = imap.search(None, '(FROM "confirmacion@pedidosya.com")')
    date_typ, date_data = imap.search(None, f'(SINCE "{date_from}" BEFORE "{date_to}")')
    ids = list(set(peya_data[0].split()) & set(date_data[0].split()))
    # ids = peya_data[0].split()

    return ids


def create_dataframe(
    email_id: int,
    date: datetime,
    total_amount: float,
    subtotal_amount: float,
    tip_amount: float,
    shipping_amount: float,
    discount_amount: float,
    payment_method: str,
):
    """
    Creates the Pedidos Ya dataframe to insert on the DB
    """
    total_amount = total_amount if total_amount is not None else 0.00
    subtotal_amount = subtotal_amount if subtotal_amount is not None else 0.00
    tip_amount = tip_amount if tip_amount is not None else 0.00
    discount_amount = discount_amount if discount_amount is not None else 0.00
    shipping_amount = shipping_amount if shipping_amount is not None else 0.00

    pedidosya_df = pd.DataFrame(
        {
            "id": [int(email_id)],
            "date": [date],
            "total_amount": [float(total_amount)],
            "subtotal_amount": [float(subtotal_amount)],
            "tip_amount": [float(tip_amount)],
            "shipping_amount": [float(shipping_amount)],
            "discount_amount": [float(discount_amount)],
            "payment_method": [payment_method],
        }
    )

    return pedidosya_df
