"""Pedidos Ya DAG."""
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
import imaplib
from email.header import decode_header
import pandas as pd
from airflow import DAG
from airflow.operators.python import PythonOperator
from sqlalchemy.exc import IntegrityError
from sqlite_cli import SqLiteClient
from utils.utils import filter_mail_inbox, create_dataframe
from utils.email_parser import EmailParser
from utils.pedidosya_parser import PedidosYaParser


# Set up Logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")

DB_URI = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DB}"

EMAIL_USERNAME = os.getenv("EMAIL_USERNAME")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
IMAP_SERVER = os.getenv("IMAP_SERVER")

STORE_DIR = Path(__file__).resolve().parent / "tmp-files"
Path.mkdir(STORE_DIR, exist_ok=True, parents=True)


def _download_daily_mails(**context):
    date = context["ds"]
    date_to = datetime.strptime(date, "%Y-%m-%d").strftime("%d-%b-%Y")
    date_from = (datetime.strptime(date, "%Y-%m-%d") - timedelta(days=1)).strftime(
        "%d-%b-%Y"
    )
    logger.info(f"Retrieving Mails from: {date_from} to {date_to}")

    # create an IMAP4 class with SSL
    imap = imaplib.IMAP4_SSL(IMAP_SERVER)
    # authenticate
    imap.login(EMAIL_USERNAME, EMAIL_PASSWORD)

    ids = filter_mail_inbox(imap, date_from, date_to)

    pedidos_ya_daily_values = []

    for i in ids:
        # fetch the email message by ID
        _, msg = imap.fetch(i, "(RFC822)")
        response = msg[0]

        email_resp = EmailParser(response)
        email_id = i.decode()
        email_subject = email_resp.get_email_subject()
        email_sender = email_resp.get_email_sender()
        email_date = email_resp.get_email_send_date()

        logger.info(f"Email ID: {email_id}")
        logger.info(f"Subject: {email_subject}")
        logger.info(f"From: {email_sender}")
        logger.info(f"Date: {email_date}")

        body = email_resp.get_email_body()
        peya = PedidosYaParser(body)
        total_amount = peya.get_total_amount()
        subtotal_amount = peya.get_subtotal_amount()
        tip_amount = peya.get_tip_amount()
        shipping_amount = peya.get_shipping_amount()
        discount_amount = peya.get_discount_amount()
        payment_method = peya.get_payment_method()

        logger.info(f"Total Amount: ${total_amount}")
        logger.info(f"Sub Total Amount: ${subtotal_amount}")
        logger.info(f"Tip Amount: ${tip_amount}")
        logger.info(f"Shipping Amount: ${shipping_amount}")
        logger.info(f"Discount Amount: ${discount_amount}")
        logger.info(f"Payment Method: {payment_method}")

        pedidosya_df = create_dataframe(
            email_id=email_id,
            date=datetime.strptime(email_date, "%a, %d %b %Y %H:%M:%S +0000 (UTC)"),
            total_amount=total_amount,
            subtotal_amount=subtotal_amount,
            tip_amount=tip_amount,
            shipping_amount=shipping_amount,
            discount_amount=discount_amount,
            payment_method=payment_method,
        )
        pedidos_ya_daily_values.append(pedidosya_df)

        logger.info("=" * 100)

    if len(pedidos_ya_daily_values) > 0:
        pedidos_ya_daily_values = pd.concat(pedidos_ya_daily_values).reset_index(
            drop=True
        )
        pedidos_ya_daily_values.to_csv(STORE_DIR / f"{date}.csv", index=False)

    # close the connection and logout
    imap.close()
    imap.logout()


def _insert_daily_data_on_db(**context):
    date = context["ds"]

    if Path(STORE_DIR / f"{date}.csv").is_file():
        pedidosya_df = pd.read_csv(STORE_DIR / f"{date}.csv")

        sql_cli = SqLiteClient(DB_URI)
        for i in range(len(pedidosya_df)):
            row = pedidosya_df.iloc[i : i + 1, :]
            email_id = row.id.values[0]
            try:
                logger.info(f"Inserting Pedidos Ya ID {email_id} values for {date}")
                sql_cli.insert_from_frame(row, "pedidosya_orders")
            except IntegrityError:
                logger.info(
                    f"Already have Pedidos Ya ID {email_id} values for {date} on DB"
                )
            except Exception as e:
                logger.info(f"Unknown error: {e}")
    else:
        logger.info(f"Not file found for {date}")


default_args = {"owner": "luciano.naveiro"}

with DAG(
    "pedidosya_dag",
    schedule_interval="@daily",
    start_date=datetime(2019, 8, 22),
    catchup=True,
    max_active_runs=5,
    default_args=default_args,
) as dag:
    download_daily_mails = PythonOperator(
        task_id="download_daily_mails",
        python_callable=_download_daily_mails,
        retries=3,
        retry_delay=timedelta(seconds=90),
    )

    insert_daily_data_on_db = PythonOperator(
        task_id="insert_daily_data_on_db",
        python_callable=_insert_daily_data_on_db,
    )


download_daily_mails >> insert_daily_data_on_db
