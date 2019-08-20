FROM python:3.7-slim
WORKDIR /
COPY . /
RUN pip install flask
RUN pip install glob3
RUN pip install -U spacy
RUN python -m spacy download en_core_web_sm
RUN pip install sklearn
RUN pip install nltk
EXPOSE 5000
CMD ["python", "./app.py"]
