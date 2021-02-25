# partkeepr-backup-python
A backup script for [PartKeepr](https://www.partkeepr.org/) inspired by [cabottech/PartKeepr-Backup](https://github.com/cabottech/PartKeepr-Backup) but implemented in Python3. The goal is to provide automated backup for a PartKeepr system that is running in Docker containers (like [mhubig/docker-partkeepr](https://github.com/mhubig/docker-partkeepr/blob/master/crontab)).

The configuration and private settings are in the secrets.py file which allows for:

* Configuration of how many local backups to keep
* Configuration of how many remote backups to keep
* Usernames and passwrod for access to the PartKeepr MariaDB and a remote file share
* Paths for various directories

