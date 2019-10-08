# Tugas ETS BDT

1. Desain Infrastruktur
    * Desain Infrastruktur Basis Data Terdistribusi
        - Gambar Infrastruktur<br>
            ![InfrastructureDB](https://user-images.githubusercontent.com/32932112/66381162-f98a9380-e9e2-11e9-96f5-0d8922de9dac.jpg)
        - Jumlah Server<br>
            Total server yang digunakan = 5<br>
            1. Server Database = 3 buah
            2. Proxy = 1 buah
            3. Apache web server = 1 buah
        - Spesifikasi Hardware
            1. Server Database<br>
                - OS menggunakan bento/ubuntu-16.04<br>
                - RAM 512MB
                - MySQL server
            2. Proxy<br>
                - MySQL
                - Menggunakan bento/ubuntu-16.04
                - RAM 512MB
            3. Apache Webserver<br>
                - Windows 10
                - RAM 4096MB
        - Pembagian IP<br>
            1. Server Database<br>
                - 192.168.16.22
                - 192.168.16.23
                - 192.168.16.24
            2. Proxy<br>
                - 192.168.16.21
            3. Apache Webserver<br>
                - localhost