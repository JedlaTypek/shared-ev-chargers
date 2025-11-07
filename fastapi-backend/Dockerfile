FROM python:3.11-slim           # malý obraz s Pythonem 3.11
WORKDIR /app                    # pracovní adresář v kontejneru

COPY requirements.txt .         # zkopíruje requirements
RUN pip install --no-cache-dir -r requirements.txt
                                # nainstaluje knihovny bez mezipaměti

COPY . .                        # zkopíruje zbytek projektu

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
                                # spustí API server
