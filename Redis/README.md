### Tugas Implementasi Redis Cluster pada Wordpress
# Implementasi Redis Cluster
Ferdinand Jason Gondowijoyo 

- [Implementasi Redis Cluster](#implementasi-redis-cluster)
  - [Deskripsi Tugas](#deskripsi-tugas)
  - [Implementasi Redis Cluster](#implementasi-redis-cluster-1)
  - [Menjalankan Redis Cluster](#menjalankan-redis-cluster)
  - [Menginstall Wordpress pada server wordpress](#menginstall-wordpress-pada-server-wordpress)
    - [Menginstall Redis Object Cache pada server wordpress1](#menginstall-redis-object-cache-pada-server-wordpress1)
  - [Pengujian menggunakan JMeter](#pengujian-menggunakan-jmeter)
    - [Pengujian 50 Koneksi](#pengujian-50-koneksi)
    - [Pengujian 133 Koneksi](#pengujian-133-koneksi)
    - [Pengujian 233 Koneksi](#pengujian-233-koneksi)
  - [Proses Fail Over](#proses-fail-over)
    - [Simulasi Redis Master Down](#simulasi-redis-master-down)
    - [Proses Fail Over](#proses-fail-over-1)

## Deskripsi Tugas
## Implementasi Redis Cluster
1. Terdapat beberapa server yang digunakan pada Tugas ini, dengan pembagian IP dan spesifikasinya sebagai berikut:
   - Server Wordpress dan MySQL:
     - `wordpress1` :
       - OS: `ubuntu-18.04`
       - RAM: `512` MB
       - IP: `192.168.16.33`
     - `wordpress2` :
       - OS: `ubuntu-18.04`
       - RAM: `512` MB
       - IP: `192.168.16.34`
   - Server Redis:
     - `redis1` :
       - OS: `ubuntu-18.04`
       - RAM: `512` MB
       - IP: `192.168.16.35`
     - `redis2` :
       - OS: `ubuntu-18.04`
       - RAM: `512` MB
       - IP: `192.168.16.36`
     - `redis3` :
       - OS: `ubuntu-18.04`
       - RAM: `512` MB
       - IP: `192.168.16.37`
2. Implementasi Vagrant
   1. Membuat `Vagrantfile` \
      Vagrantfile dapat dibuat dengan mengetikkan
      ```bash
      vagrant init
      ```
      Setelah melakukan perintah tersebut, maka `Vagrantfile` terbuat pada direktori tempat perintah tersebut dijalankan.  
   2. Memodifikasi `Vagrantfile` tersebut menjadi sebagai berikut
      ```ruby
        # -*- mode: ruby -*-
        # vi: set ft=ruby :

        # All Vagrant configuration is done below. The "2" in Vagrant.configure
        # configures the configuration version (we support older styles for
        # backwards compatibility). Please don't change it unless you know what
        # you're doing.
        Vagrant.configure("2") do |config|

            (1..2).each do |i|
                config.vm.define "wordpress#{i}" do |node|
                    node.vm.hostname = "wordpress#{i}"
                    node.vm.box = "bento/ubuntu-18.04"
                    node.vm.network "private_network", ip: "192.168.16.#{32+i}"

                    node.vm.provider "virtualbox" do |vb|
                        vb.name = "wordpress#{i}"
                        vb.gui = false
                        vb.memory = "512"
                    end
                    node.vm.provision "shell", path: "bash/wordpress.sh", privileged: false
                end
            end

            (1..3).each do |i|
                config.vm.define "redis#{i}" do |node|
                node.vm.hostname = "redis#{i}"
                node.vm.box = "bento/ubuntu-18.04"
                node.vm.network "private_network", ip: "192.168.16.#{34+i}"

                node.vm.provider "virtualbox" do |vb|
                    vb.name = "redis#{i}"
                    vb.gui = false
                    vb.memory = "512"
                end

                node.vm.provision "shell", path: "bash/redis#{i}.sh", privileged: false
                end
            end
        end
      ```

3. Membuat Script Provision
    1. Script Provision untuk `wordpress.sh` : 
        ```bash
        sudo cp /vagrant/sources/hosts /etc/hosts
        sudo cp '/vagrant/sources/sources.list' '/etc/apt/'

        sudo apt update -y

        # Install Apache2
        sudo apt install apache2 -y
        sudo ufw allow in "Apache Full"

        # Install PHP
        sudo apt install php libapache2-mod-php php-mysql php-pear php-dev -y
        sudo a2enmod mpm_prefork && sudo a2enmod php7.0
        sudo pecl install redis
        sudo echo 'extension=redis.so' >> /etc/php/7.2/apache2/php.ini

        # Install MySQL
        sudo debconf-set-selections <<< 'mysql-server mysql-server/root_password password admin'
        sudo debconf-set-selections <<< 'mysql-server mysql-server/root_password_again password admin'
        sudo apt install mysql-server -y
        sudo mysql_secure_installation -y
        sudo ufw allow 3306

        # Configure MySQL for Wordpress
        sudo mysql -u root -padmin < /vagrant/sql/wordpress.sql

        # Install Wordpress
        cd /tmp
        wget -c http://wordpress.org/latest.tar.gz
        tar -xzvf latest.tar.gz
        sudo mkdir -p /var/www/html
        sudo mv wordpress/* /var/www/html
        sudo cp /vagrant/wp-config.php /var/www/html/
        sudo chown -R www-data:www-data /var/www/html/
        sudo chmod -R 755 /var/www/html/
        sudo systemctl restart apache2

        ```
    2. Script Provision untuk `redis1.sh` : 
        ```bash
        sudo cp /vagrant/sources/hosts /etc/hosts
        sudo cp '/vagrant/sources/sources.list' '/etc/apt/'

        sudo apt update -y

        sudo apt-get install build-essential tcl -y
        sudo apt-get install libjemalloc-dev -y

        curl -O http://download.redis.io/redis-stable.tar.gz
        tar xzvf redis-stable.tar.gz
        cd redis-stable
        make
        # make test
        sudo make install

        sudo mkdir /etc/redis

        sudo cp /vagrant/config/redis1.conf /etc/redis/redis.conf
        sudo cp /vagrant/config/sentinel1.conf /etc/redis-sentinel.conf

        sudo cp /vagrant/service/redis.service /etc/systemd/system/redis.service
        sudo cp /vagrant/service/redisentinel.service /etc/systemd/system/redisentinel.service

        sudo adduser --system --group --no-create-home redis
        sudo mkdir /var/lib/redis
        sudo chown redis:redis /var/lib/redis
        sudo chmod 770 /var/lib/redis

        sudo systemctl start redis
        sudo systemctl status redis

        sudo chmod 777 /etc/redis-sentinel.conf
        sudo systemctl start redisentinel
        sudo systemctl status redisentinel

        sudo chmod -R 777 /etc/redis
        sudo systemctl restart redis
        sudo systemctl status redis
        ```
    3. Script Provision untuk `redis2.sh` : 
        ```bash
        sudo cp /vagrant/sources/hosts /etc/hosts
        sudo cp '/vagrant/sources/sources.list' '/etc/apt/'

        sudo apt update -y

        sudo apt-get install build-essential tcl -y
        sudo apt-get install libjemalloc-dev -y

        curl -O http://download.redis.io/redis-stable.tar.gz
        tar xzvf redis-stable.tar.gz
        cd redis-stable
        make
        # make test
        sudo make install

        sudo mkdir /etc/redis

        sudo cp /vagrant/config/redis2.conf /etc/redis/redis.conf
        sudo cp /vagrant/config/sentinel2.conf /etc/redis-sentinel.conf

        sudo cp /vagrant/service/redis.service /etc/systemd/system/redis.service
        sudo cp /vagrant/service/redisentinel.service /etc/systemd/system/redisentinel.service

        sudo adduser --system --group --no-create-home redis
        sudo mkdir /var/lib/redis
        sudo chown redis:redis /var/lib/redis
        sudo chmod 770 /var/lib/redis

        sudo systemctl start redis
        sudo systemctl status redis

        sudo chmod 777 /etc/redis-sentinel.conf
        sudo systemctl start redisentinel
        sudo systemctl status redisentinel

        sudo chmod -R 777 /etc/redis
        sudo systemctl restart redis
        sudo systemctl status redis
        ```
    4. Script Provision untuk `redis3.sh` : 
        ```bash
        sudo cp /vagrant/sources/hosts /etc/hosts
        sudo cp '/vagrant/sources/sources.list' '/etc/apt/'

        sudo apt update -y

        sudo apt-get install build-essential tcl -y
        sudo apt-get install libjemalloc-dev -y

        curl -O http://download.redis.io/redis-stable.tar.gz
        tar xzvf redis-stable.tar.gz
        cd redis-stable
        make
        # make test
        sudo make install

        sudo mkdir /etc/redis

        sudo cp /vagrant/config/redis3.conf /etc/redis/redis.conf
        sudo cp /vagrant/config/sentinel3.conf /etc/redis-sentinel.conf

        sudo cp /vagrant/service/redis.service /etc/systemd/system/redis.service
        sudo cp /vagrant/service/redisentinel.service /etc/systemd/system/redisentinel.service

        sudo adduser --system --group --no-create-home redis
        sudo mkdir /var/lib/redis
        sudo chown redis:redis /var/lib/redis
        sudo chmod 770 /var/lib/redis

        sudo systemctl start redis
        sudo systemctl status redis

        sudo chmod 777 /etc/redis-sentinel.conf
        sudo systemctl start redisentinel
        sudo systemctl status redisentinel

        sudo chmod -R 777 /etc/redis
        sudo systemctl restart redis
        sudo systemctl status redis
        ```
4. Membuat File Konfigurasi
    1. File Konfigurasi `redis1` : `redis1.conf` dan `sentinel1.conf`
        `redis.conf`\
        ```bash
        bind 192.168.16.35
        port 6379
        dir "/etc/redis"
        ```

        `sentinel.conf`\
        ```bash
        bind 192.168.16.35
        port 26379

        sentinel monitor redis-cluster 192.168.16.35 6379 2
        sentinel down-after-milliseconds redis-cluster 5000
        sentinel parallel-syncs redis-cluster 1
        sentinel failover-timeout redis-cluster 10000
        ```
    2. File Konfigurasi `redis2` : `redis2.conf` dan `sentinel2.conf`
        `redis.conf`\
        ```bash
        bind 192.168.16.36
        port 6379
        dir "/etc/redis"
        ```

        `sentinel.conf`\
        ```bash
        bind 192.168.16.36
        port 26379

        sentinel monitor redis-cluster 192.168.16.35 6379 2
        sentinel down-after-milliseconds redis-cluster 5000
        sentinel parallel-syncs redis-cluster 1
        sentinel failover-timeout redis-cluster 10000
        ```
    3. File Konfigurasi `redis3` : `redis3.conf` dan `sentinel3.conf`
        `redis.conf`\
        ```bash
        bind 192.168.16.37
        port 6379
        dir "/etc/redis"
        ```

        `sentinel.conf`\
        ```bash
        bind 192.168.16.37
        port 26379

        sentinel monitor redis-cluster 192.168.16.35 6379 2
        sentinel down-after-milliseconds redis-cluster 5000
        sentinel parallel-syncs redis-cluster 1
        sentinel failover-timeout redis-cluster 10000
        ```
5. Membuat File Tambahan
    1. Membuat file service `redis.service`
        ```ini
        [Unit]
        Description=Redis In-Memory Data Store
        After=network.target

        [Service]
        User=redis
        Group=redis
        ExecStart=/usr/local/bin/redis-server /etc/redis/redis.conf
        ExecStop=/usr/local/bin/redis-cli shutdown
        Restart=always

        [Install]
        WantedBy=multi-user.target
        ```
    2. Membuat file service `redisentinel.service`
        ```ini
        [Unit]
        Description=Redis Sentinel
        After=network.target

        [Service]
        User=redis
        Group=redis
        ExecStart=/usr/local/bin/redis-server /etc/redis-sentinel.conf --sentinel
        ExecStop=/usr/local/bin/redis-cli shutdown
        Restart=always

        [Install]
        WantedBy=multi-user.target
        ```

## Menjalankan Redis Cluster
Menjalankan Redis Cluster dapat dilakukan dengan mengetikkan perintah 
```
vagrant up
```
Kemudian apabila di test akan menghasilkan sebagai berikut.
![Redis Cluster](img/Redis%20Cluster.PNG)

## Menginstall Wordpress pada server wordpress
Tahap instalasi wordpress bisa dilakukan dengan membuka browser dengan url : `<alamat_ip_wordpress>/index.php` kemudian ikuti langkah - langkah yang tertera.

![Wordpress](img/Wordpress%20Dashboard.PNG)

### Menginstall Redis Object Cache pada server wordpress1
1. Login pada `/wp-admin`, kemudian pada bagian `Plugins` cari `Redis Cache Object` kemudian install.
   ![Redis Installed](img/Redis%20Cache%20Object%20Wordpress%20Installed.PNG)
2. Tambahkans Konfigurasi pada `/var/www/html/wp-config.php` pada server `wordpress1`, kemudian tambahkan line berikut
   ```
   define('WP_REDIS_HOST', '192.168.16.35');
   ```
3. Aktifkan Redis Cache Plugin\
   Kemudian lihat pada bagian `Diagnostics` agar seperti pada Gambar berikut.
   ![Redis Diagnostic](img/Redis%20Cluster%20Installed%20in%20Wordpress.PNG)
4. Redis Cache Object sudah terinstall

## Pengujian menggunakan JMeter
Langkah selanjutnya adalah pengujian JMeter, sebelum menginstall JMeter pastikan komputer sudah terinstall `JDK` dan `JRE`, serta sudah mendownload JMeter

### Pengujian 50 Koneksi
![J50](img/JMeter%2050.PNG)

### Pengujian 133 Koneksi
![J133](img/JMeter%20133.PNG)

### Pengujian 233 Koneksi
![J233](img/JMeter%20233.PNG)


## Proses Fail Over
### Simulasi Redis Master Down
1. Simulasi Redis Master Down bisa dilakukan dengan 2 cara yaitu dengan mengetikkan pada server `redis1`:
    ```
    sudo systemctl stop redis
    sudo systemctl stop redisentinel
    ```
    atau
    ```
    redis-cli -h 192.168.16.35 -p 5379 DEBUG sleep 60
    ```

    ![Master Down](img/Master%20Down%20Simulation.PNG)
2. Master telah down
### Proses Fail Over
1. Masuk kedalam `redis2` dan `redis3`, kemudian cek siapa master baru yang terpilih dengan mengetikkan `info replication` pada `redis-cli`.
   ![Redis Cluster Master Down](img/Redis%20Cluster%20Master%20Down.PNG)

2. Dapat dilihat bahwa master yang terpilih adalah `redis3`.