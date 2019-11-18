sudo bash /vagrant/bash/allhosts.sh

# Override mongod config with current config
sudo cp /vagrant/config/mongodcsvr2.conf /etc/mongod.conf

# Restart the mongo service 
sudo systemctl restart mongod