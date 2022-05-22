FROM python:3.8
WORKDIR /app
COPY requirements.txt ./requirements.txt
RUN pip3 install -r requirements.txt 

ADD . /app
CMD "streamlit run app.py --server.port ${PORT}"