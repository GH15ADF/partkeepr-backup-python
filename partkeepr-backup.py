#!/usr/bin/python

import subprocess
import time
import logging
import os
import glob
import sys

# append the path to the main script to the system path so other modules can get pulled in when executing via cron
sys.path.append(os.path.split(os.path.realpath(__file__))[0])

start_time = time.time()

# Some critical but private settings are in the secrets.py file
try:
    from secrets import secrets
except ImportError:
    print('DB secrets are kept in secrets.py, please add them there!')
    raise

logging.basicConfig(level=logging.INFO, filename=secrets['log_location']+'partkeepr-backup.log',
                    format='%(asctime)s - %(levelname)s-%(message)s')

# check for option consistency
if secrets['local_backups_to_keep'] + secrets['remote_backups_to_keep'] <= 0:
    logging.error(
        'Inconsitent options - no remote copy and no local copy retained')
    exit(1)
logging.info('Backup started')
timestamp = time.strftime('%F_%H%M')
filename = timestamp + '_partkeepr-backup'
sql_filename = filename + '.sql'
# path to temporary SQL backup before zipping it up
sql_full_path = secrets['local_tmp_path'] + sql_filename


def run_command(tag, cmds):
    """Run a shell command on the local machine.
    Also writes command information and results to the log file
    :param str tag: text for the log message
    :param str[] cmds: list of command arguments
    Returns a command result code
    """
    result = subprocess.run(cmds)
    logging.debug('{} return code: {}'.format(tag, result.returncode))
    if result.returncode:
        logging.error('{} return code for {} - stderr: {} - stdout: {} - args: {}'.format(
            result.returncode, tag, result.stderr, result.stdout, result.args))
    return result.returncode


def copy_to_remote():
    """Copies the backup zip to a remote server.
    Also writes command information and results to the log file
    Returns a command result code
    """
    command_options = ['sudo', 'mount', '-t', 'cifs', secrets['remote_share'], '-o,rw,username=' +
                       secrets['mount_user'] + ',password=' + secrets['mount_password'], secrets['mount_point']]
    rc = run_command('mount', command_options)
    if rc:  # non-zero
        logging.warn(
            'remote mount step problem. Backup remote copy not complete. Exiting')
        return(6)

    # copy to the remote directory
    command_options = ['sudo', 'cp', zip_filename, secrets['mount_point']]
    rc = run_command('cp zip', command_options)
    if rc:  # non-zero
        logging.warn(
            'remote cp step problem. Backup remote copy not complete. Exiting')
        return(7)
    else:
        logging.info('Copied {} to {}'.format(
            zip_filename, secrets['mount_point']))

    prune_backup_files(secrets['mount_point'],
                       secrets['remote_backups_to_keep'])

    command_options = ['sudo', 'umount', secrets['mount_point']]
    rc = run_command('umount', command_options)
    if rc:  # non-zero
        logging.warn(
            'unmount step problem. Check mount point {}'.format(secrets['mount_point']))
        return(8)
    # all OK
    return(0)


def prune_backup_files(clean_up_path, keep_count):
    """Prunes old backup files to the maximum configured.
    Also writes command information and results to the log file
    :param str clean_up_path: path to the driectory to be cleaned up
    :param int keep_count: maximum number of files to keep
    Returns a command result code
    """
    summary_return_code = 0
    # find all the zip files in the path
    files = glob.glob(clean_up_path + '*.zip')
    if len(files) > 0:  # check to see if there are any to clean up
        # sort files on modified date
        files.sort(key=os.path.getctime, reverse=True)
        # init summary return code
        # remove files if more than allowed
        low_index = keep_count - 1
        high_index = len(files) - 1
        logging.debug('low_index: {} high_index: {}'.format(
            low_index, high_index))
        # if the low index (number to keep) is greater than the number of files
        # this FOR loop will exit immediately because there is nothing to do
        for i in range(low_index, high_index, 1):
            command_options = ['sudo', 'rm', files[i]]
            rc = run_command('rm old backups', command_options)
            if rc:  # non-zero
                logging.warn(
                    'Problem removing old backup {}'.format(files[i]))
                summary_return_code = 1
            else:
                logging.info('Removed {}'.format(files[i]))
    else:
        logging.debug('No files to clean up in {}'.format(clean_up_path))
    return(summary_return_code)


# =============================================
# Main code
# =============================================
# create the backup directory if needed
command_options = ['docker', 'exec', 'docker-partkeepr_database_1',
                   'mkdir', '-p', secrets['local_backup_path']]
rc = run_command('mkdir', command_options)
if rc:  # non-zero
    logging.error('exiting at mkdir step - nothing to clean up')
    exit(2)

# back up the database
command_options = ['docker', 'exec', 'docker-partkeepr_database_1', 'mysqldump', '--opt',
                   '--user=partkeepr', '--password=partkeepr', 'partkeepr',  '--result_file=' + sql_full_path]
rc = run_command('mysqldump', command_options)
if rc:  # non-zero
    logging.error('exiting at mysqldump step - nothing to clean up')
    exit(3)

# copy the back to the host tmp directory for zipping
command_options = ['docker', 'cp',
                   'docker-partkeepr_database_1:' + sql_full_path, secrets['local_tmp_path']]
rc = run_command('cp', command_options)
if rc:  # non-zero
    logging.error('exiting at cp step - nothing to clean up')
    exit(4)

# clean up the tmp directory in Docker container
command_options = ['docker', 'exec',
                   'docker-partkeepr_database_1', 'rm', sql_full_path]
rc = run_command('rm', command_options)
if rc:  # non-zero
    logging.warn(
        'rm step problem. Check container /tmp and clean up as needed')

# zip everything up
zip_filename = secrets['local_backup_path'] + filename + '.zip'
command_options = ['sudo', 'zip', '--recurse-paths', zip_filename,
                   secrets['local_tmp_path'] + sql_filename, secrets['partkeepr_data_path'], secrets['partkeepr_config_path']]
rc = run_command('zip', command_options)
if rc:  # non-zero
    logging.error(
        'zip step problem. Backup not complete. Exiting')
    exit(5)
else:  # zip successful
    # delete the temp copied sql file
    command_options = ['sudo', 'rm', secrets['local_tmp_path'] + sql_filename]
    rc = run_command('rm local SQL', command_options)
    if rc:  # non-zero
        logging.warn(
            'rm local SQL problem. check for {}'.format(secrets['local_tmp_path'] + sql_filename))

# check to see if the zip is to be copied to a remote
if secrets['remote_backups_to_keep'] > 0:
    copy_to_remote()
else:
    logging.info("skip copy to remote")

# clean up the backups locally
prune_backup_files(secrets['local_backup_path'],
                   secrets['local_backups_to_keep'])

elapsed_time = time.time() - start_time

logging.info('Done: {:.2f} seconds'.format(elapsed_time))
