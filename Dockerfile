FROM python:3.11-slim

# Set thư mục làm việc trong container
WORKDIR /app

# Cài các thư viện yêu cầu
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ mã nguồn vào container
COPY . .

# Mở port Django
EXPOSE 8000

# Lệnh mặc định
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
