CREATE USER 'monitor'@'%' IDENTIFIED BY 'monitorpassword';
GRANT SELECT on sys.* to 'monitor'@'%';
FLUSH PRIVILEGES;

CREATE USER 'hanjayauser'@'%' IDENTIFIED BY 'hanjayapassword';
GRANT ALL PRIVILEGES on hanjaya.* to 'hanjayauser'@'%';
FLUSH PRIVILEGES;