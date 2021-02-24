secrets = {
    #==========================================================
    # Options
    #==========================================================
    'local_backups_to_keep' : 5,
    'remote_backups_to_keep' : 10,
    'log_location' : '/home/your-user/partkeepr_backups/',
    #==========================================================
    # Database connection properties
    #==========================================================
    'database_host' : 'localhost',
    'database_name' : 'partkeepr',
    'database_user' : 'partkeepr',
    'database_pass' : 'partkeepr',
    #==========================================================
    # Backup storage location
    #==========================================================
    'local_backup_path' : '/home/your-user/partkeepr_backups/',
    'local_tmp_path' : '/tmp/',
    #==========================================================
    # PartKeepr web paths
    #==========================================================
    'partkeepr_data_path' : '/var/lib/docker/volumes/docker-partkeepr_partkeepr-data/_data/',
    'partkeepr_config_path' : '/var/lib/docker/volumes/docker-partkeepr_partkeepr-conf/_data/',
    #==========================================================
    # remote mount info
    #==========================================================
    'remote_share' : '//192.168.1.1/partkeepr-backup', # the remote file share UNC
    'mount_user' : 'partkeepr-bak', # user with read-write access to the file share
    'mount_password' : 'user share password', # nice complex password for the share user
    'mount_point' : '/mnt/partkeeper-backup/' # some mount point for the file share
    }
