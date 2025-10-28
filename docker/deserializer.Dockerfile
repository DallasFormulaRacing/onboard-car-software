FROM arm64v8/ubuntu:22.04

# Install necessary packages
RUN apt-get update && apt-get install -y \
   build-essential \
   iproute2 \
   can-utils \
   net-tools \
   kmod \
   linux-modules-extra-raspi\
   sudo \
   ca-certificates \
   wget \
   gnupg \
   && rm -rf /var/lib/apt/lists/*

# Add Kitware APT repository and install newer CMake
RUN wget -O - https://apt.kitware.com/keys/kitware-archive-latest.asc 2>/dev/null | gpg --dearmor - | tee /usr/share/keyrings/kitware-archive-keyring.gpg >/dev/null && \
    echo 'deb [signed-by=/usr/share/keyrings/kitware-archive-keyring.gpg] https://apt.kitware.com/ubuntu/ jammy main' | tee /etc/apt/sources.list.d/kitware.list >/dev/null && \
    apt-get update && \
    apt-get install -y cmake && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy the project
COPY . .

# Build the deserializer application
WORKDIR /app/apps/deserializer
RUN mkdir -p build && \
    cd build && \
    cmake .. && \
    make -j$(nproc)

# Make entrypoint script executable
RUN chmod +x /app/apps/deserializer/entrypoint.sh

USER root
WORKDIR /app

ENTRYPOINT ["/app/apps/deserializer/entrypoint.sh"]