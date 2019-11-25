### Tugas Implementasi Redis Cluster pada Wordpress
# Implementasi Redis Cluster

- [Implementasi Redis Cluster](#implementasi-redis-cluster)
  - [Deskripsi Tugas](#deskripsi-tugas)
  - [Implementasi Redis Cluster](#implementasi-redis-cluster-1)
  - [Menjalankan Redis Cluster](#menjalankan-redis-cluster)
  - [Menginstall Wordpress pada server wordpress](#menginstall-wordpress-pada-server-wordpress)
    - [Menginstall Redis Object Cache pada server wordpress1](#menginstall-redis-object-cache-pada-server-wordpress1)
  - [Pengujian menggunakan JMeter](#pengujian-menggunakan-jmeter)
    - [Pengujian 50 Koneksi](#pengujian-50-koneksi)
    - [Pengujian 133 Koneksi](#pengujian-121-koneksi)
    - [Pengujian 233 Koneksi](#pengujian-221-koneksi)
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
       - IP: `192.168.16.21`
     - `wordpress2` :
       - OS: `ubuntu-18.04`
       - RAM: `512` MB
       - IP: `192.168.16.22`
   - Server Redis:
     - `redis1` :
       - OS: `ubuntu-18.04`
       - RAM: `512` MB
       - IP: `192.168.16.23`
     - `redis2` :
       - OS: `ubuntu-18.04`
       - RAM: `512` MB
       - IP: `192.168.16.24`
     - `redis3` :
       - OS: `ubuntu-18.04`
       - RAM: `512` MB
       - IP: `192.168.16.25`
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
                    node.vm.network "private_network", ip: "192.168.16.#{20+i}"

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
                node.vm.network "private_network", ip: "192.168.16.#{22+i}"

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

        sudo chmod 777 /etc/redis-sentinel.conf
        sudo systemctl start redisentinel

        sudo chmod 777 /etc/redis -R
        sudo systemctl restart redis
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

        sudo chmod 777 /etc/redis-sentinel.conf
        sudo systemctl start redisentinel

        sudo chmod 777 /etc/redis -R
        sudo systemctl restart redis
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

        sudo chmod 777 /etc/redis-sentinel.conf
        sudo systemctl start redisentinel

        sudo chmod 777 /etc/redis -R
        sudo systemctl restart redis
        ```
4. Membuat File Konfigurasi
    1. File Konfigurasi `redis1` :
        `redis1.conf`
        ```bash
        bind 192.168.16.23
        port 6379
        dir "/etc/redis"
        ```

        `sentinel1.conf`
        ```bash
        bind 192.168.16.23
        port 26379

        sentinel monitor redis-cluster 192.168.16.23 6379 2
        sentinel down-after-milliseconds redis-cluster 5000
        sentinel parallel-syncs redis-cluster 1
        sentinel failover-timeout redis-cluster 10000
        ```
    2. File Konfigurasi `redis2` : 
        `redis2.conf`
        ```bash
        bind 192.168.16.24
        port 6379
        dir "/etc/redis"
        ```

        `sentinel2.conf`
        ```bash
        bind 192.168.16.24
        port 26379

        sentinel monitor redis-cluster 192.168.16.23 6379 2
        sentinel down-after-milliseconds redis-cluster 5000
        sentinel parallel-syncs redis-cluster 1
        sentinel failover-timeout redis-cluster 10000
        ```
    3. File Konfigurasi `redis3` :
        `redis3.conf`
        ```bash
        bind 192.168.16.25
        port 6379
        dir "/etc/redis"
        ```

        `sentinel3.conf`
        ```bash
        bind 192.168.16.25
        port 26379

        sentinel monitor redis-cluster 192.168.16.23 6379 2
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
Menjalankan Redis Cluster dilakukan dengan mengetikkan perintah 
```
vagrant up
```
Kemudian setelah selesai, masuk ke redis1 dan ketikkan
    ```bash
    redis-cli -h 192.168.16.23
    ```
Setelah itu ketikkan
    ```bash
    info replication
    ```

![replication](https://user-images.githubusercontent.com/32932112/69533261-10dd0a80-0faa-11ea-96bb-5b1f746b6247.png)


## Menginstall Wordpress pada server wordpress
Tahap instalasi wordpress bisa dilakukan dengan membuka browser dengan url : `192.168.16.21/index.php` kemudian ikuti langkah - langkah yang tertera.

![21-up](https://user-images.githubusercontent.com/32932112/69533293-205c5380-0faa-11ea-90e1-8d28536fa721.png)
![22-up](https://user-images.githubusercontent.com/32932112/69533296-218d8080-0faa-11ea-8792-44775e1f0876.png)


### Menginstall Redis Object Cache pada server wordpress1
1. Masuk di `/wp-admin`, kemudian pada bagian `Plugins` cari `Redis Object Cache` kemudian install.
  
2. Tambahkans Konfigurasi pada `/var/www/html/wp-config.php` pada server `wordpress1`, kemudian tambahkan line berikut
   ```
   define('FS_METHOD', 'direct');
   define('WP_REDIS_SENTINEL', 'redis-cluster');
   define('WP_REDIS_SERVERS', ['tcp://192.168.16.23:26379', 'tcp://192.168.16.24:26379', 'tcp://192.168.16.25:26379']);
   ```
3. Aktifkan Redis Cache Plugin\
   Kemudian lihat pada bagian `Diagnostics` agar seperti pada Gambar berikut.
 
4. Redis Cache Object sudah terinstall
    ![redis-connect](https://user-images.githubusercontent.com/32932112/69533360-41bd3f80-0faa-11ea-9874-478748d9bf95.png)

## Pengujian menggunakan JMeter
Langkah selanjutnya adalah pengujian JMeter

### Pengujian 50 Koneksi
![tes50](https://user-images.githubusercontent.com/32932112/69533504-83e68100-0faa-11ea-965c-8e56f04fa164.png)

### Pengujian 121 Koneksi
![tes121](https://user-images.githubusercontent.com/32932112/69533513-85b04480-0faa-11ea-9486-fc1efa37a0c0.png)

### Pengujian 221 Koneksi
![test221](https://user-images.githubusercontent.com/32932112/69533517-86e17180-0faa-11ea-95ef-661218f608da.png)


## Proses Fail Over
### Simulasi Redis Master Down
1. Simulasi Redis Master Down bisa dilakukan dengan mengetikkan pada server `redis1`:
    ```
    sudo systemctl stop redis
    sudo systemctl stop redisentinel
    ```

    ![stop-redis1](https://user-images.githubusercontent.com/32932112/69533582-a2e51300-0faa-11ea-9a57-3f259006f541.png)
    ![stop-redisentinel1](https://user-images.githubusercontent.com/32932112/69533586-a4164000-0faa-11ea-8e40-fd573f93bcf9.png)

2. Master telah down
### Proses Fail Over
1. Masuk kedalam `redis2` dan `redis3`, kemudian cek siapa master baru yang terpilih dengan mengetikkan `info replication` pada `redis-cli`.
   ![redis3-master](https://user-images.githubusercontent.com/32932112/69533641-b8f2d380-0faa-11ea-81de-88cddf806a72.png)

2. Master yang baru adalah `redis3`.