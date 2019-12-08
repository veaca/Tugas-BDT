### EAS Basis Data Terdistribusi
## TiDb Cluster
### Alvin Tanuwijaya - 05111640000021

## Arsitektur TiDb
1. Gambar Arsitektur
2. Penjelasan
Pada arsitektur yang digunakan, terdapat 6 server, yaitu:

|          |                     pd1                    |       pd2      |       pd3      |        tikv4       |        tikv5       |           tikv6              |
|:--------:|:---------------------------------------------:|:-----------------:|:-----------------:|:-------------------:|:-------------------:|---------------------|
| Plugin | PD, TiDB, node_export, Prometheus, Grafana | PD, node_export| PD, node_export| TiKV, node_export| TiKV, node_export| TiKV, node_export|
| OS       | CentOS 7                                      | CentOS 7          | CentOS 7          | CentOS 7            | CentOS 7            | CentOS 7            |
| RAM      | `512` MB                                      | `512` MB          | `512` MB          | `512` MB            | `512` MB            | `512` MB            |
| IP       | 192.168.16.21                                 | 192.168.16.22     | 192.168.16.23     | 192.168.16.24       | 192.168.16.25       | 192.168.16.26       |

### Implementasi pada Vagrant
1. Membuat Vagrantfile
Membuat vagrantfile dengan mengetikkan pada command prompt:
```bash
    vagrant init
```
2. Edit vagrantfile menjadi
```ruby
# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
    (1..3).each do |i|
      config.vm.define "pd#{i}" do |node|
        node.vm.hostname = "pd#{i}"

        # Gunakan CentOS 7 dari geerlingguy yang sudah dilengkapi VirtualBox Guest Addition
        node.vm.box = "geerlingguy/centos7"
        node.vm.box_version = "1.2.19"
        
        # Disable checking VirtualBox Guest Addition agar tidak compile ulang setiap restart
        node.vbguest.auto_update = false
        
        node.vm.network "private_network", ip: "192.168.199.#{20+i}"
        
        node.vm.provider "virtualbox" do |vb|
          vb.name = "pd#{i}"
          vb.gui = false
          vb.memory = "512"
        end
  
        node.vm.provision "shell", path: "provision/bootstrap.sh", privileged: false
      end
    end

    (1..3).each do |i|
      config.vm.define "tikv#{i}" do |node|
        node.vm.hostname = "tikv#{i}"

        # Gunakan CentOS 7 dari geerlingguy yang sudah dilengkapi VirtualBox Guest Addition
        node.vm.box = "geerlingguy/centos7"
        node.vm.box_version = "1.2.19"
        
        # Disable checking VirtualBox Guest Addition agar tidak compile ulang setiap restart
        node.vbguest.auto_update = false
        
        node.vm.network "private_network", ip: "192.168.199.#{23+i}"
        
        node.vm.provider "virtualbox" do |vb|
          vb.name = "tikv#{i}"
          vb.gui = false
          vb.memory = "512"
        end
  
        node.vm.provision "shell", path: "provision/bootstrap.sh", privileged: false
      end
    end
  end
```
3. Menginstall plugin vbguest dengan mengetikkan pada command prompt:
```bash
   vagrant plugin install vagrant-vbguest
```

4. Membuat script provision untuk dijalankan saat vagrant up:
```bash
# Referensi:
# https://pingcap.com/docs/stable/how-to/deploy/from-tarball/testing-environment/

# Update the repositories
# sudo yum update -y

# Copy open files limit configuration
sudo cp /vagrant/config/tidb.conf /etc/security/limits.d/

# Enable max open file
sudo sysctl -w fs.file-max=1000000

# Copy atau download TiDB binary dari http://download.pingcap.org/tidb-v3.0-linux-amd64.tar.gz
cp /vagrant/installer/tidb-v3.0-linux-amd64.tar.gz .

# Extract TiDB binary
tar -xzf tidb-v3.0-linux-amd64.tar.gz

# Install MariaDB to get MySQL client
sudo yum -y install mariadb

# Install Git
sudo yum -y install git

# Install nano text editor
sudo yum -y install nano

#Install node exporter
wget https://github.com/prometheus/node_exporter/releases/download/v0.15.2/node_exporter-0.15.2.linux-amd64.tar.gz

#extract node exporter
tar -xzf node_exporter-0.15.2.linux-amd64.tar.gz
```
5. Jalankan vagrant dengan mengetikkan :
```bash
    vagrant up
```
6. Konfigurasi TiDb:
- Pada pd1, masuk dengan `vagrant ssh pd1`, lalu ketikkan :
```bash
./bin/pd-server --name=pd1 \
                --data-dir=pd \
                --client-urls="http://192.168.16.21:2379" \
                --peer-urls="http://192.168.16.21:2380" \
                --initial-cluster="pd1=http://192.168.16.21:2380,pd2=http://192.168.16.22:2380,pd3=http://192.168.16.23:2380" \
                --log-file=pd.log &
```
- Pada pd2, masuk dengan `vagrant ssh pd2`, lalu ketikkan :
```bash
./bin/pd-server --name=pd2 \
                --data-dir=pd \
                --client-urls="http://192.168.16.22:2379" \
                --peer-urls="http://192.168.16.22:2380" \
                --initial-cluster="pd1=http://192.168.16.21:2380,pd2=http://192.168.16.22:2380,pd3=http://192.168.16.23:2380" \
                --log-file=pd.log &
```
- Pada pd3, masuk dengan `vagrant ssh pd3`, lalu ketikkan :
```bash
./bin/pd-server --name=pd3 \
                --data-dir=pd \
                --client-urls="http://192.168.16.23:2379" \
                --peer-urls="http://192.168.16.23:2380" \
                --initial-cluster="pd1=http://192.168.16.21:2380,pd2=http://192.168.16.22:2380,pd3=http://192.168.16.23:2380" \
                --log-file=pd.log &
```
- Pada tikv1, masuk dengan `vagrant ssh tikv1`, lalu ketikkan::
```bash
./bin/tikv-server --pd="192.168.16.21:2379,192.168.16.22:2379.192.168.16.23:2379" \
                  --addr="192.168.16.24:20160" \
                  --data-dir=tikv \
                  --log-file=tikv.log &
```
- Pada tikv2, masuk dengan `vagrant ssh tikv2`, lalu ketikkan::
```bash
./bin/tikv-server --pd="192.168.16.21:2379,192.168.16.22:2379.192.168.16.23:2379" \
                  --addr="192.168.16.25:20160" \
                  --data-dir=tikv \
                  --log-file=tikv.log &
```
- Pada tikv3, masuk dengan `vagrant ssh tikv3`, lalu ketikkan::
```bash
./bin/tikv-server --pd="192.168.16.21:2379,192.168.16.22:2379.192.168.16.23:2379" \
                  --addr="192.168.16.26:20160" \
                  --data-dir=tikv \
                  --log-file=tikv.log &
```
- Kembali pada pd1, masuk dengan `vagrant ssh pd1`, lalu ketikkan :
```bash
./bin/tidb-server --store=tikv \
                  --path="192.168.16.21:2379" \
                  --log-file=tidb.log &
```