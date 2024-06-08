FROM python
RUN mkdir /app
WORKDIR /app
# Cài đặt các gói thư viện cần thiết
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libegl1 \
    libxkbcommon0 \
    libdbus-1-3 \
    libxcb-cursor0 \
    && rm -rf /var/lib/apt/lists/*
# Tạo thư mục /app và cài đặt PyQt6

RUN pip install PyQt6


# Sao chép mã nguồn của ứng dụng vào container
COPY . /app

# Thiết lập lệnh CMD để chạy ứng dụng khi container được khởi chạy
CMD ["python", "UI_Login.py"]
