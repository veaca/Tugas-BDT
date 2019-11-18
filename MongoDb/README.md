### Tugas Implementasi MongoDB 
# Implementasi MongoDB Cluster
Alvin Tanuwijaya
05111640000021

- [Implementasi MongoDB Cluster](#implementasi-mongodb-cluster)
  - [Deskripsi Tugas](#deskripsi-tugas)
  - [Implementasi MongoDB Cluster](#implementasi-mongodb-cluster-1)
  - [Konfigurasi MongoDB Cluster](#konfigurasi-mongodb-cluster)
  - [Import Data dan Hasil](#import-data-dan-hasil)
  - [API](#api)
    - [Create](#create)
    - [Read](#read)
    - [Update](#update)
    - [Delete](#delete)
    - [Aggregation](#aggregation)
    - [Aggregation 2](#aggregation-2)

## Deskripsi Tugas
1. Implementasi Cluster MongoDB
   - Menggunakan versi MongoDB: 4.2
   - Dapat menggunakan Vagrant/Docker
   - Cluster terdiri dari:
     - Config server: 2
     - Data/shard server: 3
     - Query router: 1
2. Menggunakan dataset
   - Menggunakan dataset berformat CSV atau JSON dengan ukuran > 1000 baris
   - Import ke dalam server MongoDB
3. Implementasi aplikasi CRUD
   - Menggunakan bahasa pemrograman yang support dengan connector MongoDB
   - Menggunakan Web/API/Scripting
   - Harus ada operasi CRUD
   - Untuk proses read, harus melibatkan juga agregasi
     - Minimal ada 2 contoh query agregasi

## Implementasi MongoDB Cluster
1. Terdapat beberapa server yang digunakan pada Tugas ini, dengan pembagian IP dan spesifikasinya sebagai berikut:
   - Server Config:
     - `mongo-config-1` :
       - OS: `ubuntu-18.04`
       - RAM: `512` MB
       - IP: `192.168.16.21`
     - `mongo-config-2` :
       - OS: `ubuntu-18.04`
       - RAM: `512` MB
       - IP: `192.168.16.22`
   - Query Router:
     - `mongo-query-router` :
       - OS: `ubuntu-18.04`
       - RAM: `512` MB
       - IP: `192.168.16.23`
   - Server Data/Shard:
     - `mongo-shard-1` :
       - OS: `ubuntu-18.04`
       - RAM: `512` MB
       - IP: `192.168.16.24`
     - `mongo-shard-2` :
       - OS: `ubuntu-18.04`
       - RAM: `512` MB
       - IP: `192.168.16.25`
     - `mongo-shard-3` :
       - OS: `ubuntu-18.04`
       - RAM: `512` MB
       - IP: `192.168.16.`
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

        Vagrant.configure("2") do |config|

          config.vm.define "mongo_config_1" do |mongo_config_1|
            mongo_config_1.vm.hostname = "mongo-config-1"
            mongo_config_1.vm.box = "bento/ubuntu-18.04"
            mongo_config_1.vm.network "private_network", ip: "192.168.16.21"
          mongo_config_1.vm.boot_timeout = 1200
            
            mongo_config_1.vm.provider "virtualbox" do |vb|
              vb.name = "mongo-config-1"
              vb.gui = false
              vb.memory = "512"
            end

            mongo_config_1.vm.provision "shell", path: "bash/mongo_config_1.sh", privileged: false
          end

          config.vm.define "mongo_config_2" do |mongo_config_2|
            mongo_config_2.vm.hostname = "mongo-config-2"
            mongo_config_2.vm.box = "bento/ubuntu-18.04"
            mongo_config_2.vm.network "private_network", ip: "192.168.16.22"
            mongo_config_2.vm.boot_timeout = 1200
          
            mongo_config_2.vm.provider "virtualbox" do |vb|
              vb.name = "mongo-config-2"
              vb.gui = false
              vb.memory = "512"
            end

            mongo_config_2.vm.provision "shell", path: "bash/mongo_config_2.sh", privileged: false
          end

          config.vm.define "mongo_query_router" do |mongo_query_router|
            mongo_query_router.vm.hostname = "mongo-query-router"
            mongo_query_router.vm.box = "bento/ubuntu-18.04"
            mongo_query_router.vm.network "private_network", ip: "192.168.16.23"
          mongo_query_router.vm.boot_timeout = 1200
            
            mongo_query_router.vm.provider "virtualbox" do |vb|
              vb.name = "mongo-query-router"
              vb.gui = false
              vb.memory = "512"
            end

            mongo_query_router.vm.provision "shell", path: "bash/mongo_router.sh", privileged: false
          end

          config.vm.define "mongo_shard_1" do |mongo_shard_1|
            mongo_shard_1.vm.hostname = "mongo-shard-1"
            mongo_shard_1.vm.box = "bento/ubuntu-18.04"
            mongo_shard_1.vm.network "private_network", ip: "192.168.16.24"
          mongo_shard_1.vm.boot_timeout = 1200
                
            mongo_shard_1.vm.provider "virtualbox" do |vb|
              vb.name = "mongo-shard-1"
              vb.gui = false
              vb.memory = "512"
            end

            mongo_shard_1.vm.provision "shell", path: "bash/mongo_shard_1.sh", privileged: false
          end

          config.vm.define "mongo_shard_2" do |mongo_shard_2|
            mongo_shard_2.vm.hostname = "mongo-shard-2"
            mongo_shard_2.vm.box = "bento/ubuntu-18.04"
            mongo_shard_2.vm.network "private_network", ip: "192.168.16.25"
          mongo_shard_2.vm.boot_timeout = 1200
            
            mongo_shard_2.vm.provider "virtualbox" do |vb|
              vb.name = "mongo-shard-2"
              vb.gui = false
              vb.memory = "512"
            end

            mongo_shard_2.vm.provision "shell", path: "bash/mongo_shard_2.sh", privileged: false
          end

          config.vm.define "mongo_shard_3" do |mongo_shard_3|
            mongo_shard_3.vm.hostname = "mongo-shard-3"
            mongo_shard_3.vm.box = "bento/ubuntu-18.04"
            mongo_shard_3.vm.network "private_network", ip: "192.168.16.26"
          mongo_shard_3.vm.boot_timeout = 1200
            
            mongo_shard_3.vm.provider "virtualbox" do |vb|
              vb.name = "mongo-shard-3"
              vb.gui = false
              vb.memory = "512"
            end

            mongo_shard_3.vm.provision "shell", path: "bash/mongo_shard_3.sh", privileged: false
          end

        end
      ```

3. Membuat Script Provision
   1. Script Provision untuk semua host : `allhosts.sh`
        ```bash
        # Add hostname
        sudo cp /vagrant/sources/hosts /etc/hosts

        # Copy APT sources list
        sudo cp /vagrant/sources/sources.list /etc/apt/
        sudo cp /vagrant/sources/mongodb-org-4.2.list /etc/apt/sources.list.d/

        # Add MongoDB repo key
        sudo apt-get install gnupg
        wget -qO - https://www.mongodb.org/static/pgp/server-4.2.asc | sudo apt-key add -

        # Update Repository
        sudo apt-get update
        # sudo apt-get upgrade -y

        # Install MongoDB
        sudo apt-get install -y mongodb-org

        # Start MongoDB
        sudo service mongod start
        ```
   2. Script Provision untuk `mongo-config-1`
        ```bash
        sudo bash /vagrant/bash/allhosts.sh

        # Override mongod config with current config
        sudo cp /vagrant/config/mongodcsvr1.conf /etc/mongod.conf

        # Restart the mongo service 
        sudo systemctl restart mongod
        ```
   3. Script Provision untuk `mongo-config-2`
        ```bash
        sudo bash /vagrant/bash/allhosts.sh

        # Override mongod config with current config
        sudo cp /vagrant/config/mongodcsvr2.conf /etc/mongod.conf

        # Restart the mongo service 
        sudo systemctl restart mongod

        ```
   4. Script Provision untuk `mongo-query-router`
        ```bash
        sudo bash /vagrant/bash/allhosts.sh

        # Override mongod config with current config
        sudo cp /vagrant/config/mongos.conf /etc/mongos.conf

        # Create new service file
        sudo touch /lib/systemd/system/mongos.service
        sudo cp /vagrant/service/mongos.service /lib/systemd/system/mongos.service

        # Stop current mongo service
        sudo systemctl stop mongod

        # Enable mongos.service
        sudo systemctl enable mongos.service
        sudo systemctl start mongos

        # Confirm mongos is running
        systemctl status mongos

        ```
   5. Script Provision untuk `mongo-shard-1`
        ```bash
        sudo bash /vagrant/provision/allhosts.sh

        # Override mongod config with current config
        sudo cp /vagrant/config/mongodshardsvr1.conf /etc/mongod.conf

        # Restart the mongo service 
        sudo systemctl restart mongod

        # weird
        sleep 5
        ```
   6. Script Provision untuk `mongo-shard-2`
        ```bash
        sudo bash /vagrant/bash/allhosts.sh

        # Override mongod config with current config
        sudo cp /vagrant/config/mongodshardsvr2.conf /etc/mongod.conf

        # Restart the mongo service 
        sudo systemctl restart mongod
        ```
   7. Script Provision untuk `mongo-shard-3`
        ```bash
        sudo bash /vagrant/bash/allhosts.sh

        # Override mongod config with current config
        sudo cp /vagrant/config/mongodshardsvr3.conf /etc/mongod.conf

        # Restart the mongo service 
        sudo systemctl restart mongod
        ```

4. Membuat File Konfigurasi
   1. File Konfigurasi `mongo-config-1` : `mongodcsvr1.conf`
        ```ini
        # mongod.conf

        # for documentation of all options, see:
        #   http://docs.mongodb.org/manual/reference/configuration-options/

        # where to write logging data.
        systemLog:
          destination: file
          logAppend: true
          path: /var/log/mongodb/mongod.log

        # Where and how to store data.
        storage:
          dbPath: /var/lib/mongodb
          journal:
            enabled: true
        #  engine:
        #  wiredTiger:

        # how the process runs
        processManagement:
          timeZoneInfo: /usr/share/zoneinfo

        # network interfaces
        net:
          port: 27019
          bindIp: 192.168.16.21

        #security:

        #operationProfiling:

        replication:
          replSetName: configReplSet

        sharding:
          clusterRole: "configsvr"
        
        ## Enterprise-Only Options

        #auditLog:

        #snmp:
        ```
   2. File Konfigurasi `mongo-config-2` : `mongodcsvr2.conf`
        ```ini
        # mongod.conf

        # for documentation of all options, see:
        #   http://docs.mongodb.org/manual/reference/configuration-options/

        # where to write logging data.
        systemLog:
          destination: file
          logAppend: true
          path: /var/log/mongodb/mongod.log

        # Where and how to store data.
        storage:
          dbPath: /var/lib/mongodb
          journal:
            enabled: true
        #  engine:
        #  wiredTiger:

        # how the process runs
        processManagement:
          timeZoneInfo: /usr/share/zoneinfo

        # network interfaces
        net:
          port: 27019
          bindIp: 192.168.16.22


        #security:
        #  keyFile: /opt/mongo/mongodb-keyfile

        #operationProfiling:

        replication:
          replSetName: configReplSet

        sharding:
          clusterRole: "configsvr"
        
        ## Enterprise-Only Options

        #auditLog:

        #snmp:
        
        ```
   3. File Konfigurasi `mongo-query-router` : `mongos.conf`
        ```ini
        # where to write logging data.
        systemLog:
          destination: file
          logAppend: true
          path: /var/log/mongodb/mongos.log

        # network interfaces
        net:
          port: 27017
          bindIp: 192.168.16.23

        sharding:
          configDB: configReplSet/mongo-config-1:27019,mongo-config-2:27019
        ```
   4. File Konfigurasi `mongo-shard-1` : `mongodshardsvr1.conf`
        ```ini
        # mongod.conf

        # for documentation of all options, see:
        #   http://docs.mongodb.org/manual/reference/configuration-options/

        # where to write logging data.
        systemLog:
          destination: file
          logAppend: true
          path: /var/log/mongodb/mongod.log

        # Where and how to store data.
        storage:
          dbPath: /var/lib/mongodb
          journal:
            enabled: true
        #  engine:
        #  wiredTiger:

        # how the process runs
        processManagement:
          timeZoneInfo: /usr/share/zoneinfo

        # network interfaces
        net:
          port: 27017
          bindIp: 192.168.16.24


        #security:

        #operationProfiling:

        #replication:

        sharding:
        clusterRole: "shardsvr"
        
        ## Enterprise-Only Options

        #auditLog:

        #snmp:
        ```
   5. File Konfigurasi `mongo-shard-2` : `mongodshardsvr2.conf`
        ```ini
        # mongod.conf

        # for documentation of all options, see:
        #   http://docs.mongodb.org/manual/reference/configuration-options/

        # where to write logging data.
        systemLog:
          destination: file
          logAppend: true
          path: /var/log/mongodb/mongod.log

        # Where and how to store data.
        storage:
          dbPath: /var/lib/mongodb
          journal:
            enabled: true
        #  engine:
        #  wiredTiger:

        # how the process runs
        processManagement:
          timeZoneInfo: /usr/share/zoneinfo

        # network interfaces
        net:
          port: 27017
          bindIp: 192.168.16.25


        #security:

        #operationProfiling:

        #replication:

        sharding:
          clusterRole: "shardsvr"
        
        ## Enterprise-Only Options

        #auditLog:

        #snmp:
        ```
   6. File Konfigurasi `mongo-shard-3` : `mongodshardsvr3.conf`
        ```ini
        # mongod.conf

        # for documentation of all options, see:
        #   http://docs.mongodb.org/manual/reference/configuration-options/

        # where to write logging data.
        systemLog:
          destination: file
          logAppend: true
          path: /var/log/mongodb/mongod.log

        # Where and how to store data.
        storage:
          dbPath: /var/lib/mongodb
          journal:
            enabled: true
        #  engine:
        #  wiredTiger:

        # how the process runs
        processManagement:
          timeZoneInfo: /usr/share/zoneinfo

        # network interfaces
        net:
          port: 27017
          bindIp: 192.168.16.26


        #security:

        #operationProfiling:

        #replication:

        sharding:
          clusterRole: "shardsvr"
        
        ## Enterprise-Only Options

        #auditLog:

        #snmp:
        ```
5. Membuat File Tambahan
   1. Membuat `/vagrant/sources/hosts`
        ```
        192.168.16.21 mongo-config-1
        192.168.16.22 mongo-config-2
        192.168.16.23 mongo-query-router
        192.168.16.24 mongo-shard-1
        192.168.16.25 mongo-shard-2
        192.168.16.26 mongo-shard-3
        ```
   2. Membuat file service `mongos.service`
        ```ini
        [Unit]
        Description=Mongo Cluster Router
        After=network.target

        [Service]
        User=mongodb
        Group=mongodb
        ExecStart=/usr/bin/mongos --config /etc/mongos.conf
        # file size
        LimitFSIZE=infinity
        # cpu time
        LimitCPU=infinity
        # virtual memory size
        LimitAS=infinity
        # open files
        LimitNOFILE=64000
        # processes/threads
        LimitNPROC=64000
        # total threads (user+kernel)
        TasksMax=infinity
        TasksAccounting=false

        [Install]
        WantedBy=multi-user.target
        ```


## Konfigurasi MongoDB Cluster
1. Konfigurasi Replica Set
    1. Masuk ke salah satu server config \
        server `vagrant-config-1`
        ```bash
        vagrant ssh mongo_config_1
        ```
        Masuk mongo
        ```
        mongo mongo-config-1:27019
        ```
    2. Init replica set \
        Ketikkan 
        ```
        rs.initiate( { _id: "configReplSet", configsvr: true, members: [ { _id: 0, host: "mongo-config-1:27019" }, { _id: 1, host: "mongo-config-2:27019" }] } )
        ```
    3. Cek hasil replica set \
        Ketikkan
        ```
        rs.status()
        ```
2. Membuat user administrative
    1. Masuk ke salah satu server config \
        Server `mongo-config-1`
        ```bash
        vagrant ssh mongo_config_1
        ```
        Masuk mongo
        ```
        mongo mongo-config-1:27019
        ```
    2. Connect ke database `admin` \
        Pada `mongo` shell ketikan
        ```
        use admin
        ```
    3. Membuat user
        ```
        db.createUser({user: "mongo-admin", pwd: "password", roles:[{role: "root", db: "admin"}]})
        ```
3. Menambahkan shard kedalam MongoDB Cluster
    1. Masuk kedalam salah satu server shard \
        Masuk server `vagrant-shard-1`
        ```bash
        vagrant ssh mongo_shard_1
        ```
    2. Connect ke MongoDB Query Router `mongo-query-router`
        ```bash
        mongo mongo-query-router:27017 -u mongo-admin -p --authenticationDatabase admin
        ```
    3. Menambahkan shard \
        Ketikkan
        ```bash
        sh.addShard( "mongo-shard-1:27017" )
        sh.addShard( "mongo-shard-2:27017" )
        sh.addShard( "mongo-shard-3:27017" )
        ```
4. Mengaktifkan sharding pada database dan koleksi
    1. Masuk kedalam salah satu server shard \
        Masuk kedalam server `mongo-shard-1`
        ```bash
        vagrant ssh mongo_shard_1
        ```
    2. Connect ke MongoDB Query Router `mongo-query-router`
        ```bash
        mongo mongo-query-router:27017 -u mongo-admin -p --authenticationDatabase admin
        ```
    3. Membuat database \
        Ketikkan
        ```bash
        use news
        sh.enableSharding("ufo")
        db.ufoCollection.ensureIndex( { _id : "hashed" } )
        sh.shardCollection( "ufo.ufoCollection", { "_id" : "hashed" } )
        ```

## Import Data dan Hasil
1. Mengimport data `dataset` kedalam MongoDB Cluster
    - Masuk ke router
    ```bash
    sudo vagrant ssh router
    ```
    - Import dataset
    ```bash
    mongoimport --host 192.168.16.23 --port 27017 --db ufo --collection ufoCollection --file /vagrant/dataset/complete.csv --type csv --headerline
    ```
2. Hasil import data
    - Masuk ke router
    ```bash
    sudo vagrant ssh router
    ```
    - Masuk ke MongoDB
    ```bash
    mongo router:27017 -u mongo-admin -p --authenticationDatabase admin
    ```
    - Cek sharding
    ```bash
    db.ufoCollection.getShardDistribution()
    ```
    ![shard_dist](https://user-images.githubusercontent.com/32932112/69059186-a0813700-0a47-11ea-99b1-047c04fd1ba3.PNG)



## API
Percobaan menggunakan REST API yang dibuat berdasarkan Flask (Python).
### Create
Endpoint untuk fungsi ini adalah `POST /ufo`, berikut hasilnya.
![post_ufo](https://user-images.githubusercontent.com/32932112/69059236-b7c02480-0a47-11ea-8eec-6879b4742b89.PNG)

### Read
Endpoint untuk fungsi ini adalah `GET /ufo`, berikut hasilnya.
![get_ufo](https://user-images.githubusercontent.com/32932112/69059263-c1e22300-0a47-11ea-9f59-f87181815b6d.PNG)

### Update
Endpoint untuk fungsi ini adalah `PUT /ufo/<id>`, berikut hasilnya.
![update_ufo](https://user-images.githubusercontent.com/32932112/69059270-c3abe680-0a47-11ea-9a0a-3aeb1699d2f0.PNG)

### Delete
Endpoint untuk fungsi ini adalah `DELETE /ufo/<id>`, berikut hasilnya.
![delete_ufo](https://user-images.githubusercontent.com/32932112/69059313-d6262000-0a47-11ea-957b-4255f9b07581.PNG)

### Aggregation
Endpoint untuk fungsi ini adalah `GET /ufo/count` dimana berfungsi untuk menghitung jumlah penampakan UFO berdasarkan bentuknya, berikut hasilnya.
![count_ufo](https://user-images.githubusercontent.com/32932112/69059339-e8a05980-0a47-11ea-99ff-9b13d4866c80.PNG)

### Aggregation 2
Endpoint untuk fungsi ini adalah `GET /ufo/max` dimana berfungsi menghitung maksimum waktu yang mana UFO terlihat dalam hitungan detik, berikut hasilnya.
![max_ufo](https://user-images.githubusercontent.com/32932112/69059383-ffdf4700-0a47-11ea-9585-b2e23ce35354.PNG)
