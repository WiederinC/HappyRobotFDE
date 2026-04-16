FROM python:3.11-slim

WORKDIR /app

# Install dashboard dependencies
RUN pip install --no-cache-dir streamlit==1.56.0 plotly==6.7.0 requests==2.33.1

# Copy dashboard source
COPY dashboard/streamlit_app.py ./dashboard/streamlit_app.py

EXPOSE 8501

CMD ["streamlit", "run", "dashboard/streamlit_app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true"]
