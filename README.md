# Tugas ETS BDT

1. Desain Infrastruktur
    * Desain Infrastruktur Basis Data Terdistribusi
        - Gambar Infrastruktur<br>
            ![InfrastructureDB](https://user-images.githubusercontent.com/32932112/66381717-0bb90180-e9e4-11e9-8a33-a714ec253af0.jpg)
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
2. Implementasi Infrastruktur Basis Data Terdistribusi
	- Memperbarui `Vagrantfile` menjadi seperti berikut: 
	```ruby
		# -*- mode: ruby -*-
		# vi: set ft=ruby :

		# All Vagrant configuration is done below. The "2" in Vagrant.configure
		# configures the configuration version (we support older styles for
		# backwards compatibility). Please don't change it unless you know what
		# you're doing.

		Vagrant.configure("2") do |config|
		  
		  # MySQL Cluster dengan 3 node
		  (1..3).each do |i|
			config.vm.define "db#{i}" do |node|
			  node.vm.hostname = "db#{i}"
			  node.vm.box = "bento/ubuntu-16.04"
			  node.vm.network "private_network", ip: "192.168.16.#{i+21}"
			  node.vm.boot_timeout = 1200

			  # Opsional. Edit sesuai dengan nama network adapter di komputer
			  #node.vm.network "public_network", bridge: "Qualcomm Atheros QCA9377 Wireless Network Adapter"
			  
			  node.vm.provider "virtualbox" do |vb|
				vb.name = "db#{i}"
				vb.gui = false
				vb.memory = "512"
			  end
			  
			  node.vm.provision "shell", path: "bash/deployMySQL1#{i}.sh", privileged: false
			end
		  end

		  config.vm.define "proxy" do |proxy|
			proxy.vm.hostname = "proxy"
			proxy.vm.box = "bento/ubuntu-16.04"
			proxy.vm.network "private_network", ip: "192.168.16.21"
			#proxy.vm.network "public_network",  bridge: "Qualcomm Atheros QCA9377 Wireless Network Adapter"
			
			proxy.vm.provider "virtualbox" do |vb|
			  vb.name = "proxy"
			  vb.gui = false
			  vb.memory = "512"
			end

			proxy.vm.provision "shell", path: "bash/deployProxySQL.sh", privileged: false
		  end

		end
		```
		Penjelasan dari kode diatas : \
		`Vagrantfile` akan membuat 1 Load Balancer dengan IP 192.168.16.21 dan 3 MySQL Server dengan IP 192.168.16.22, 192.168.16.23, 192.168.16.24 dengan memori `512MB`
		
	- Dilanjutkan dengan membuat Provision Script
		- Script Provision untuk `db1` 
			```bash
				# Changing the APT sources.list to kambing.ui.ac.id
				sudo cp '/vagrant/config/sources.list' '/etc/apt/sources.list'

				# Updating the repo with the new sources
				sudo apt-get update -y

				# Install required library
				sudo apt-get install libaio1
				sudo apt-get install libmecab2

				# Get MySQL binaries
				curl -OL https://dev.mysql.com/get/Downloads/MySQL-5.7/mysql-common_5.7.23-1ubuntu16.04_amd64.deb
				curl -OL https://dev.mysql.com/get/Downloads/MySQL-5.7/mysql-community-client_5.7.23-1ubuntu16.04_amd64.deb
				curl -OL https://dev.mysql.com/get/Downloads/MySQL-5.7/mysql-client_5.7.23-1ubuntu16.04_amd64.deb
				curl -OL https://dev.mysql.com/get/Downloads/MySQL-5.7/mysql-community-server_5.7.23-1ubuntu16.04_amd64.deb

				# Setting input for installation
				sudo debconf-set-selections <<< 'mysql-community-server mysql-community-server/root-pass password admin'
				sudo debconf-set-selections <<< 'mysql-community-server mysql-community-server/re-root-pass password admin'

				# Install MySQL Community Server
				sudo dpkg -i mysql-common_5.7.23-1ubuntu16.04_amd64.deb
				sudo dpkg -i mysql-community-client_5.7.23-1ubuntu16.04_amd64.deb
				sudo dpkg -i mysql-client_5.7.23-1ubuntu16.04_amd64.deb
				sudo dpkg -i mysql-community-server_5.7.23-1ubuntu16.04_amd64.deb

				# Allow port on firewall
				sudo ufw allow 33061
				sudo ufw allow 3306

				# Copy MySQL configurations
				sudo cp /vagrant/config/my11.cnf /etc/mysql/my.cnf

				# Restart MySQL services
				sudo service mysql restart

				# Cluster bootstrapping
				sudo mysql -u root -padmin < /vagrant/sql/cluster_bootstrap.sql
				sudo mysql -u root -padmin < /vagrant/sql/addition_to_sys.sql
				sudo mysql -u root -padmin < /vagrant/sql/create_proxysql_user.sql
			```
			Dengan penjelasan sebagai berikut:
			1. Mengganti source.list ke `kambing.ui.ac.id`
			2. Menginstall dependecy untuk MySQL Server.
			3. Mendowload MySQL Community Server.
			4. Mengizinkan port 33061 dan 3306.
			5. Mengubah konfigurasi MySQL menjadi `/vagrant/config/my11.cnf`
			6. Restart MySQL Server.
			7. Membuat user MySQL, dan menginstall keperluan dan script untuk group replication.
		
		- Script Provision untuk `db2`
			```bash
				# Changing the APT sources.list to kambing.ui.ac.id
				sudo cp '/vagrant/config/sources.list' '/etc/apt/sources.list'

				# Updating the repo with the new sources
				sudo apt-get update -y

				# Install required library
				sudo apt-get install libaio1
				sudo apt-get install libmecab2

				# Get MySQL binaries
				curl -OL https://dev.mysql.com/get/Downloads/MySQL-5.7/mysql-common_5.7.23-1ubuntu16.04_amd64.deb
				curl -OL https://dev.mysql.com/get/Downloads/MySQL-5.7/mysql-community-client_5.7.23-1ubuntu16.04_amd64.deb
				curl -OL https://dev.mysql.com/get/Downloads/MySQL-5.7/mysql-client_5.7.23-1ubuntu16.04_amd64.deb
				curl -OL https://dev.mysql.com/get/Downloads/MySQL-5.7/mysql-community-server_5.7.23-1ubuntu16.04_amd64.deb

				# Setting input for installation
				sudo debconf-set-selections <<< 'mysql-community-server mysql-community-server/root-pass password admin'
				sudo debconf-set-selections <<< 'mysql-community-server mysql-community-server/re-root-pass password admin'

				# Install MySQL Community Server
				sudo dpkg -i mysql-common_5.7.23-1ubuntu16.04_amd64.deb
				sudo dpkg -i mysql-community-client_5.7.23-1ubuntu16.04_amd64.deb
				sudo dpkg -i mysql-client_5.7.23-1ubuntu16.04_amd64.deb
				sudo dpkg -i mysql-community-server_5.7.23-1ubuntu16.04_amd64.deb

				# Allow port on firewall
				sudo ufw allow 33061
				sudo ufw allow 3306

				# Copy MySQL configurations
				sudo cp /vagrant/config/my12.cnf /etc/mysql/my.cnf

				# Restart MySQL services
				sudo service mysql restart

				# Cluster bootstrapping
				sudo mysql -u root -padmin < /vagrant/sql/cluster_member.sql
			```
			Dengan penjelasan sebagai berikut:
			1. Mengganti source.list ke `kambing.ui.ac.id`
			2. Menginstall dependecy untuk MySQL Server.
			3. Mendowload MySQL Community Server.
			4. Mengizinkan port 33061 dan 3306.
			5. Mengubah konfigurasi MySQL menjadi `/vagrant/config/my12.cnf`
			6. Restart MySQL Server.
			7. Membuat user MySQL untuk member cluster.
		
		- Script Provision untuk `db3`
			```bash
				# Changing the APT sources.list to kambing.ui.ac.id
				sudo cp '/vagrant/config/sources.list' '/etc/apt/sources.list'

				# Updating the repo with the new sources
				sudo apt-get update -y

				# Install required library
				sudo apt-get install libaio1
				sudo apt-get install libmecab2

				# Get MySQL binaries
				curl -OL https://dev.mysql.com/get/Downloads/MySQL-5.7/mysql-common_5.7.23-1ubuntu16.04_amd64.deb
				curl -OL https://dev.mysql.com/get/Downloads/MySQL-5.7/mysql-community-client_5.7.23-1ubuntu16.04_amd64.deb
				curl -OL https://dev.mysql.com/get/Downloads/MySQL-5.7/mysql-client_5.7.23-1ubuntu16.04_amd64.deb
				curl -OL https://dev.mysql.com/get/Downloads/MySQL-5.7/mysql-community-server_5.7.23-1ubuntu16.04_amd64.deb

				# Setting input for installation
				sudo debconf-set-selections <<< 'mysql-community-server mysql-community-server/root-pass password admin'
				sudo debconf-set-selections <<< 'mysql-community-server mysql-community-server/re-root-pass password admin'

				# Install MySQL Community Server
				sudo dpkg -i mysql-common_5.7.23-1ubuntu16.04_amd64.deb
				sudo dpkg -i mysql-community-client_5.7.23-1ubuntu16.04_amd64.deb
				sudo dpkg -i mysql-client_5.7.23-1ubuntu16.04_amd64.deb
				sudo dpkg -i mysql-community-server_5.7.23-1ubuntu16.04_amd64.deb

				# Allow port on firewall
				sudo ufw allow 33061
				sudo ufw allow 3306

				# Copy MySQL configurations
				sudo cp /vagrant/config/my13.cnf /etc/mysql/my.cnf

				# Restart MySQL services
				sudo service mysql restart

				# Cluster bootstrapping
				sudo mysql -u root -padmin < /vagrant/sql/cluster_member.sql
			```
			Dengan penjelasan sebagai berikut:
			1. Mengganti source.list ke `kambing.ui.ac.id`
			2. Menginstall dependecy untuk MySQL Server.
			3. Mendowload MySQL Community Server.
			4. Mengizinkan port 33061 dan 3306.
			5. Mengubah konfigurasi MySQL menjadi `/vagrant/config/my13.cnf`
			6. Restart MySQL Server.
			7. Membuat user MySQL untuk member cluster.
		
		- Script Provision untuk `proxy`
			```bash 
				# Changing the APT sources.list to kambing.ui.ac.id
				sudo cp '/vagrant/config/sources.list' '/etc/apt/sources.list'

				# Updating the repo with the new sources
				sudo apt-get update -y

				cd /tmp
				curl -OL https://github.com/sysown/proxysql/releases/download/v1.4.4/proxysql_1.4.4-ubuntu16_amd64.deb
				curl -OL https://dev.mysql.com/get/Downloads/MySQL-5.7/mysql-common_5.7.23-1ubuntu16.04_amd64.deb
				curl -OL https://dev.mysql.com/get/Downloads/MySQL-5.7/mysql-community-client_5.7.23-1ubuntu16.04_amd64.deb
				curl -OL https://dev.mysql.com/get/Downloads/MySQL-5.7/mysql-client_5.7.23-1ubuntu16.04_amd64.deb

				sudo apt-get install libaio1
				sudo apt-get install libmecab2

				sudo dpkg -i proxysql_1.4.4-ubuntu16_amd64.deb
				sudo dpkg -i mysql-common_5.7.23-1ubuntu16.04_amd64.deb
				sudo dpkg -i mysql-community-client_5.7.23-1ubuntu16.04_amd64.deb
				sudo dpkg -i mysql-client_5.7.23-1ubuntu16.04_amd64.deb

				sudo ufw allow 33061
				sudo ufw allow 3306

				sudo systemctl start proxysql
				#mysql -u admin -padmin -h 127.0.0.1 -P 6032 < /vagrant/proxysql.sql
			```
			Dengan penjelasan sebagai berikut:
			1. Mengganti source.list ke `kambing.ui.ac.id`
			2. Menginstall dependecy untuk MySQL Server.
			3. Mendowload MySQL Community Server.
			4. Mengizinkan port 33061 dan 3306.
			5. Mengubah konfigurasi MySQL menjadi `/vagrant/config/my13.cnf`
			6. Restart MySQL Server.
			7. Mendaftarkan user dan host yang tergabung dalam grup database ke ProxySQL.
	- Membuat Konfigurasi SQL
		- File konfigurasi untuk `db1`
			```ini
				#
				# The MySQL database server configuration file.
				#
				# You can copy this to one of:
				# - "/etc/mysql/my.cnf" to set global options,
				# - "~/.my.cnf" to set user-specific options.
				# 
				# One can use all long options that the program supports.
				# Run program with --help to get a list of available options and with
				# --print-defaults to see which it would actually understand and use.
				#
				# For explanations see
				# http://dev.mysql.com/doc/mysql/en/server-system-variables.html

				#
				# * IMPORTANT: Additional settings that can override those from this file!
				#   The files must end with '.cnf', otherwise they'll be ignored.
				#

				!includedir /etc/mysql/conf.d/
				!includedir /etc/mysql/mysql.conf.d/

				[mysqld]

				# General replication settings
				gtid_mode = ON
				enforce_gtid_consistency = ON
				master_info_repository = TABLE
				relay_log_info_repository = TABLE
				binlog_checksum = NONE
				log_slave_updates = ON
				log_bin = binlog
				binlog_format = ROW
				transaction_write_set_extraction = XXHASH64
				loose-group_replication_bootstrap_group = OFF
				loose-group_replication_start_on_boot = ON
				loose-group_replication_ssl_mode = REQUIRED
				loose-group_replication_recovery_use_ssl = 1

				# Shared replication group configuration
				loose-group_replication_group_name = "8f22f846-9922-4139-b2b7-097d185a93cb"
				loose-group_replication_ip_whitelist = "192.168.16.22, 192.168.16.23, 192.168.16.24"
				loose-group_replication_group_seeds = "192.168.16.22:33061, 192.168.16.23:33061, 192.168.16.24:33061"

				# Single or Multi-primary mode? Uncomment these two lines
				# for multi-primary mode, where any host can accept writes
				loose-group_replication_single_primary_mode = OFF
				loose-group_replication_enforce_update_everywhere_checks = ON

				# Host specific replication configuration
				server_id = 1
				bind-address = "192.168.16.22"
				report_host = "192.168.16.22"
				loose-group_replication_local_address = "192.168.16.22:33061"
			```
			Dengan penjelasan sebagai berikut:
			1. Mengubah `gtid` menjadi `ON`
			2. Menambahkan universal unique ID (UUID) pada `loose-group_replication_group_name` .
		    3. Menambahkan list IP pada group replication pada `loose-group_replication_ip_whitelist` 
		    4. Menambahkan list IP dan port pada group replication pada `loose-group_replication_group_seeds` 
		    5. Mengubah variable `loose-group_replication_single_primary_mode` menjadi `OFF`
		    6. Mengubah variable `loose-group_replication_enforce_update_everywhere_checks` menjadi `ON`
		    7. Menambahkan `server_id` = 1, `bind-address`, `report_host`, `loose-group_replication_local_address` IP dan port host tersebut.
			
		- File konfigurasi untuk `db2`
			```ini
				#
				# The MySQL database server configuration file.
				#
				# You can copy this to one of:
				# - "/etc/mysql/my.cnf" to set global options,
				# - "~/.my.cnf" to set user-specific options.
				# 
				# One can use all long options that the program supports.
				# Run program with --help to get a list of available options and with
				# --print-defaults to see which it would actually understand and use.
				#
				# For explanations see
				# http://dev.mysql.com/doc/mysql/en/server-system-variables.html

				#
				# * IMPORTANT: Additional settings that can override those from this file!
				#   The files must end with '.cnf', otherwise they'll be ignored.
				#

				!includedir /etc/mysql/conf.d/
				!includedir /etc/mysql/mysql.conf.d/

				[mysqld]

				# General replication settings
				gtid_mode = ON
				enforce_gtid_consistency = ON
				master_info_repository = TABLE
				relay_log_info_repository = TABLE
				binlog_checksum = NONE
				log_slave_updates = ON
				log_bin = binlog
				binlog_format = ROW
				transaction_write_set_extraction = XXHASH64
				loose-group_replication_bootstrap_group = OFF
				loose-group_replication_start_on_boot = ON
				loose-group_replication_ssl_mode = REQUIRED
				loose-group_replication_recovery_use_ssl = 1

				# Shared replication group configuration
				loose-group_replication_group_name = "8f22f846-9922-4139-b2b7-097d185a93cb"
				loose-group_replication_ip_whitelist = "192.168.16.22, 192.168.16.23, 192.168.16.24"
				loose-group_replication_group_seeds = "192.168.16.22:33061, 192.168.16.23:33061, 192.168.16.24:33061"

				# Single or Multi-primary mode? Uncomment these two lines
				# for multi-primary mode, where any host can accept writes
				loose-group_replication_single_primary_mode = OFF
				loose-group_replication_enforce_update_everywhere_checks = ON

				# Host specific replication configuration
				server_id = 2
				bind-address = "192.168.16.23"
				report_host = "192.168.16.23"
				loose-group_replication_local_address = "192.168.16.23:33061"
			```
			Dengan penjelasan sebagai berikut:
			1. Mengubah `gtid` menjadi `ON`
			2. Menambahkan universal unique ID (UUID) pada `loose-group_replication_group_name` .
		    3. Menambahkan list IP pada group replication pada `loose-group_replication_ip_whitelist` 
		    4. Menambahkan list IP dan port pada group replication pada `loose-group_replication_group_seeds` 
		    5. Mengubah variable `loose-group_replication_single_primary_mode` menjadi `OFF`
		    6. Mengubah variable `loose-group_replication_enforce_update_everywhere_checks` menjadi `ON`
		    7. Menambahkan `server_id` = 2, `bind-address`, `report_host`, `loose-group_replication_local_address` IP dan port host tersebut.
			
		- File konfigurasi untuk `db3`
			```ini
				#
				# The MySQL database server configuration file.
				#
				# You can copy this to one of:
				# - "/etc/mysql/my.cnf" to set global options,
				# - "~/.my.cnf" to set user-specific options.
				# 
				# One can use all long options that the program supports.
				# Run program with --help to get a list of available options and with
				# --print-defaults to see which it would actually understand and use.
				#
				# For explanations see
				# http://dev.mysql.com/doc/mysql/en/server-system-variables.html

				#
				# * IMPORTANT: Additional settings that can override those from this file!
				#   The files must end with '.cnf', otherwise they'll be ignored.
				#

				!includedir /etc/mysql/conf.d/
				!includedir /etc/mysql/mysql.conf.d/

				[mysqld]

				# General replication settings
				gtid_mode = ON
				enforce_gtid_consistency = ON
				master_info_repository = TABLE
				relay_log_info_repository = TABLE
				binlog_checksum = NONE
				log_slave_updates = ON
				log_bin = binlog
				binlog_format = ROW
				transaction_write_set_extraction = XXHASH64
				loose-group_replication_bootstrap_group = OFF
				loose-group_replication_start_on_boot = ON
				loose-group_replication_ssl_mode = REQUIRED
				loose-group_replication_recovery_use_ssl = 1

				# Shared replication group configuration
				loose-group_replication_group_name = "8f22f846-9922-4139-b2b7-097d185a93cb"
				loose-group_replication_ip_whitelist = "192.168.16.22, 192.168.16.23, 192.168.16.24"
				loose-group_replication_group_seeds = "192.168.16.22:33061, 192.168.16.23:33061, 192.168.16.24:33061"

				# Single or Multi-primary mode? Uncomment these two lines
				# for multi-primary mode, where any host can accept writes
				loose-group_replication_single_primary_mode = OFF
				loose-group_replication_enforce_update_everywhere_checks = ON

				# Host specific replication configuration
				server_id = 3
				bind-address = "192.168.16.24"
				report_host = "192.168.16.24"
				loose-group_replication_local_address = "192.168.16.24:33061"
			```
			Dengan penjelasan sebagai berikut:
			1. Mengubah `gtid` menjadi `ON`
			2. Menambahkan universal unique ID (UUID) pada `loose-group_replication_group_name` .
		    3. Menambahkan list IP pada group replication pada `loose-group_replication_ip_whitelist` 
		    4. Menambahkan list IP dan port pada group replication pada `loose-group_replication_group_seeds` 
		    5. Mengubah variable `loose-group_replication_single_primary_mode` menjadi `OFF`
		    6. Mengubah variable `loose-group_replication_enforce_update_everywhere_checks` menjadi `ON`
		    7. Menambahkan `server_id` = 3, `bind-address`, `report_host`, `loose-group_replication_local_address` IP dan port host tersebut.
	
	- Membuat File SQL Lainnya
		- File `addition_to_sys.sql`
			```sql
				USE sys;

				DELIMITER $$

				CREATE FUNCTION IFZERO(a INT, b INT)
				RETURNS INT
				DETERMINISTIC
				RETURN IF(a = 0, b, a)$$

				CREATE FUNCTION LOCATE2(needle TEXT(10000), haystack TEXT(10000), offset INT)
				RETURNS INT
				DETERMINISTIC
				RETURN IFZERO(LOCATE(needle, haystack, offset), LENGTH(haystack) + 1)$$

				CREATE FUNCTION GTID_NORMALIZE(g TEXT(10000))
				RETURNS TEXT(10000)
				DETERMINISTIC
				RETURN GTID_SUBTRACT(g, '')$$

				CREATE FUNCTION GTID_COUNT(gtid_set TEXT(10000))
				RETURNS INT
				DETERMINISTIC
				BEGIN
				  DECLARE result BIGINT DEFAULT 0;
				  DECLARE colon_pos INT;
				  DECLARE next_dash_pos INT;
				  DECLARE next_colon_pos INT;
				  DECLARE next_comma_pos INT;
				  SET gtid_set = GTID_NORMALIZE(gtid_set);
				  SET colon_pos = LOCATE2(':', gtid_set, 1);
				  WHILE colon_pos != LENGTH(gtid_set) + 1 DO
					 SET next_dash_pos = LOCATE2('-', gtid_set, colon_pos + 1);
					 SET next_colon_pos = LOCATE2(':', gtid_set, colon_pos + 1);
					 SET next_comma_pos = LOCATE2(',', gtid_set, colon_pos + 1);
					 IF next_dash_pos < next_colon_pos AND next_dash_pos < next_comma_pos THEN
					   SET result = result +
						 SUBSTR(gtid_set, next_dash_pos + 1,
								LEAST(next_colon_pos, next_comma_pos) - (next_dash_pos + 1)) -
						 SUBSTR(gtid_set, colon_pos + 1, next_dash_pos - (colon_pos + 1)) + 1;
					 ELSE
					   SET result = result + 1;
					 END IF;
					 SET colon_pos = next_colon_pos;
				  END WHILE;
				  RETURN result;
				END$$

				CREATE FUNCTION gr_applier_queue_length()
				RETURNS INT
				DETERMINISTIC
				BEGIN
				  RETURN (SELECT sys.gtid_count( GTID_SUBTRACT( (SELECT
				Received_transaction_set FROM performance_schema.replication_connection_status
				WHERE Channel_name = 'group_replication_applier' ), (SELECT
				@@global.GTID_EXECUTED) )));
				END$$

				CREATE FUNCTION gr_member_in_primary_partition()
				RETURNS VARCHAR(3)
				DETERMINISTIC
				BEGIN
				  RETURN (SELECT IF( MEMBER_STATE='ONLINE' AND ((SELECT COUNT(*) FROM
				performance_schema.replication_group_members WHERE MEMBER_STATE != 'ONLINE') >=
				((SELECT COUNT(*) FROM performance_schema.replication_group_members)/2) = 0),
				'YES', 'NO' ) FROM performance_schema.replication_group_members JOIN
				performance_schema.replication_group_member_stats USING(member_id));
				END$$

				CREATE VIEW gr_member_routing_candidate_status AS SELECT
				sys.gr_member_in_primary_partition() as viable_candidate,
				IF( (SELECT (SELECT GROUP_CONCAT(variable_value) FROM
				performance_schema.global_variables WHERE variable_name IN ('read_only',
				'super_read_only')) != 'OFF,OFF'), 'YES', 'NO') as read_only,
				sys.gr_applier_queue_length() as transactions_behind, Count_Transactions_in_queue as 'transactions_to_cert' from performance_schema.replication_group_member_stats;$$

				DELIMITER ;
			```
		- File `cluster_bootstrap.sql`
			```sql
				SET SQL_LOG_BIN=0;
				CREATE USER 'repl'@'%' IDENTIFIED BY 'password' REQUIRE SSL;
				GRANT REPLICATION SLAVE ON *.* TO 'repl'@'%';
				FLUSH PRIVILEGES;
				SET SQL_LOG_BIN=1;
				CHANGE MASTER TO MASTER_USER='repl', MASTER_PASSWORD='password' FOR CHANNEL 'group_replication_recovery';
				INSTALL PLUGIN group_replication SONAME 'group_replication.so';

				SET GLOBAL group_replication_bootstrap_group=ON;
				START GROUP_REPLICATION;
				SET GLOBAL group_replication_bootstrap_group=OFF;

				CREATE DATABASE hanjaya;
			```
		- File `cluster_member`
			```sql
				SET SQL_LOG_BIN=0;
				CREATE USER 'repl'@'%' IDENTIFIED BY 'password' REQUIRE SSL;
				GRANT REPLICATION SLAVE ON *.* TO 'repl'@'%';
				FLUSH PRIVILEGES;
				SET SQL_LOG_BIN=1;
				CHANGE MASTER TO MASTER_USER='repl', MASTER_PASSWORD='password' FOR CHANNEL 'group_replication_recovery';
				INSTALL PLUGIN group_replication SONAME 'group_replication.so';
			```
		- File `create_proxysql_user.sql`
			```sql
				CREATE USER 'monitor'@'%' IDENTIFIED BY 'monitorpassword';
				GRANT SELECT on sys.* to 'monitor'@'%';
				FLUSH PRIVILEGES;

				CREATE USER 'hanjayauser'@'%' IDENTIFIED BY 'hanjayapassword';
				GRANT ALL PRIVILEGES on hanjaya.* to 'hanjayauser'@'%';
				FLUSH PRIVILEGES;
			```
		- File `proxysql.sql`
			```sql
				UPDATE global_variables SET variable_value='admin:password' WHERE variable_name='admin-admin_credentials';
				LOAD ADMIN VARIABLES TO RUNTIME;
				SAVE ADMIN VARIABLES TO DISK;

				UPDATE global_variables SET variable_value='monitor' WHERE variable_name='mysql-monitor_username';
				LOAD MYSQL VARIABLES TO RUNTIME;
				SAVE MYSQL VARIABLES TO DISK;

				INSERT INTO mysql_group_replication_hostgroups (writer_hostgroup, backup_writer_hostgroup, reader_hostgroup, offline_hostgroup, active, max_writers, writer_is_also_reader, max_transactions_behind) VALUES (2, 4, 3, 1, 1, 3, 1, 100);

				INSERT INTO mysql_servers(hostgroup_id, hostname, port) VALUES (2, '192.168.16.22', 3306);
				INSERT INTO mysql_servers(hostgroup_id, hostname, port) VALUES (2, '192.168.16.23', 3306);
				INSERT INTO mysql_servers(hostgroup_id, hostname, port) VALUES (2, '192.168.16.24', 3306);

				LOAD MYSQL SERVERS TO RUNTIME;
				SAVE MYSQL SERVERS TO DISK;

				INSERT INTO mysql_users(username, password, default_hostgroup) VALUES ('hanjayauser', 'hanjayapassword', 2);
				LOAD MYSQL USERS TO RUNTIME;
				SAVE MYSQL USERS TO DISK;
			```
	- Menjalankan Vagrant
		1. run Vagrant
			```bash
			vagrant up
			```
		2. Tunggu hingga seluruh download dan provision selesai. Setelah selesai cek status dengan :
			```bash
			vagrant status
			```
		3. Masuk ke ssh proxy, dengan mengetikkan:
			```
			vagrant ssh proxy
			```
		4. Masukkan proxysql.sql sebagai provision pada proxy :
			```
			mysql -u admin -p -h 127.0.0.1 -P 6032 < /vagrant/sql/proxysql.sql
			```
3. Implementasi Pada Aplikasi (Web)
	- Instal Hanjaya
		- Copy file Hanjaya dari git dengan 
			```bash
				git clone https://github.com/veaca/hanjaya.git
				cd hanjaya
				composer install
			```
		- Buat file .env untuk konfigurasi koneksi database dengan kode :
			```ini
				DB_CONNECTION=mysql
				DB_HOST=192.168.16.21
				DB_PORT=6033
				DB_DATABASE=hanjaya
				DB_USERNAME=hanjayauser
				DB_PASSWORD=hanjayapassword
			```
		- Setelah .env selesai lanjutkan pada bash dengan :
			```bash
				php artisan key:generate
			```
		- Migrate dan Seed Database (Laravel)
			```bash
				php artisan migrate
				php artisan storage:link
				php artisan db:seed
			```
		- Jalankan Aplikasi
			```bash
				php artisan serve
			```
4. Simulasi Fail-Over
	- Matikan salah satu MySQL Server
		Dapat memilih server untuk dimatikan, sebagai contoh db2`
		```bash
			vagrant ssh db2`
		```
		Matikan MySQL
		```bash
			sudo systemctl stop mysql
		```
		Cek Status
		```bash
			sudo systemctl status mysql
		```
	- Cek status server pada ProxySQL
		ssh pada proxy
		```bash
			vagrant ssh proxy
			mysql -u admin -p -h 127.0.0.1 -P 6032 --prompt='ProxySQLAdmin> '
		```
		Kemudian
		```sql
			SELECT hostgroup_id, hostname, status FROM runtime_mysql_servers;
		```
	- Lakukan penambahan data baru pada database melalui aplikasi
	
	- Cek apakah data tersebut sudah direplikasi pada saat db2 dinyalakan
		- Menyalakan kembali db2
		```bash
			vagrant ssh db2`
		```
		Jalankan MySQL
		```bash
			sudo systemctl start mysql
		```
		Cek Status
		```bash
			sudo systemctl status mysql
		```
		- Cek status server pada ProxySQL
		ssh pada proxy
		```bash
			vagrant ssh proxy
			mysql -u admin -p -h 127.0.0.1 -P 6032 --prompt='ProxySQLAdmin> '
		```
		Kemudian
		```sql
			SELECT hostgroup_id, hostname, status FROM runtime_mysql_servers;
		```
		- Verifikasi hasil replikasi
		Lakukan query untuk melihat hasil data pada table yang sebelumnya telah ditambahkan data baru
		```sql
			use hanjaya;
			select * from customers;
		```
		
		
		