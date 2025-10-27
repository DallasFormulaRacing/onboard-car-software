FROM arm64v8/ubuntu:22.04


RUN apt-get update && apt-get install -y \
   build-essential \
   cmake \
   iproute2 \
   can-utils \
   net-tools \
   kmod \
   linux-modules-extra-raspi\
   sudo \
   && rm -rf /var/lib/apt/lists/*


WORKDIR /app


COPY . .


RUN mkdir -p build && cd build && cmake .. && make -j$(nproc)


#COPY entrypoint.sh /entrypoint.sh


RUN chmod +x /app/entrypoint.sh


USER root


ENTRYPOINT ["/app/entrypoint.sh"]