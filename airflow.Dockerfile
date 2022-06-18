FROM apache/airflow:2.2.2

RUN pip install beautifulsoup4==4.11.1

USER root
RUN apt update
RUN apt install -y git