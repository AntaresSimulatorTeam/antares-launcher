# Integration data directory

> ATTENTION:
>
> The `data` directory is intended to store your configuration for integration testing with a SLURM server.
> It should contain the application configuration file `configuration.yaml` and the SSH configuration file
> `ssh_config.json`. The files in this directory should never be versioned in Git (except `README.md`).

## Application Configuration

To test the `Antares_Launcher` command-line application, you need to create a `configuration.yaml` configuration file
that defines input/output directories, SSH configuration, and simulation parameters.

Example of application configuration file:

```yaml
LOG_DIR : "~/Projects/antares-launcher/data/LOGS"
JSON_DIR : "~/Projects/antares-launcher/data/LOGS"
STUDIES_IN_DIR : "~/Projects/antares-launcher/data/STUDIES-IN"
FINISHED_DIR : "~/Projects/antares-launcher/data/FINISHED"
DEFAULT_TIME_LIMIT : 172800
DEFAULT_N_CPU : 12
DEFAULT_WAIT_TIME : 900
DB_PRIMARY_KEY : "name"
DEFAULT_SSH_CONFIGFILE_NAME: "ssh_config.json"
SSH_CONFIG_FILE_IS_REQUIRED : False
SLURM_SCRIPT_PATH : "/opt/antares/launchAntares.sh"

ANTARES_VERSIONS_ON_REMOTE_SERVER :
  - "610"
  - "700"
  - "710"
  - "720"
  - "800"
  - "810"
  - "820"
  - "830"
  - "840"
```

Below is a description of the parameters:

- `LOG_DIR`: 
- `JSON_DIR`: 
- `STUDIES_IN_DIR`: 
- `FINISHED_DIR`: 
- `DEFAULT_TIME_LIMIT`: 
- `DEFAULT_N_CPU`: 
- `DEFAULT_WAIT_TIME`: 
- `DB_PRIMARY_KEY`: 
- `DEFAULT_SSH_CONFIGFILE_NAME`: name of the SSH configuration file, it should be "ssh_config.json".
- `SSH_CONFIG_FILE_IS_REQUIRED`: 
- `SLURM_SCRIPT_PATH`: 
- `ANTARES_VERSIONS_ON_REMOTE_SERVER`: 

## SSH Configuration

The SSH configuration allows you to specify the connection parameters to the SLURM server.
You can use either a login/password or a private SSH key to establish the connection.

The configuration should be stored in the `ssh_config.json` file.

There are two ways to establish an SSH connection: using a login/password or using a private/public SSH key pair. The
two ways are explained bellow:

### Connect with login/password

When you use a login/password, you need to provide your username and password to authenticate with the remote server.

> This method is less secure than using an SSH key pair, because if your password is compromised, an attacker can gain
> access to the remote server.

To connect to the SLURM server using an SSH login/password, you can use the following configuration file:

```json
{
  "hostname": "slurm-server",
  "port": 22,
  "username": "user",
  "password": "********"
}
```

### Set up an SSH key pair

> Using an SSH key pair is generally considered to be more secure and convenient than using a login/password, especially
> if you need to connect to the remote server frequently or automate your SSH connections. However, it does require some
> additional setup to generate and manage the keys.

To create an SSH key pair and add the public key to a remote server, you can follow these instructions:

To create an SSH key pair, you can use the `ssh-keygen` command in the terminal.
By default, this command creates a 2048-bit RSA key pair, consisting of a private key and a public key.
You can run the command without any arguments to accept the default settings.

```bash
ssh-keygen
```

Once you have generated your key pair, you can use the `ssh-copyid` command to copy the public key to the remote server.
The `ssh-copyid` command automatically adds the public key to the `authorized_keys` file on the server, which allows you
to authenticate with the server using your private key.

```bash
ssh-copyid user@slurm-server
```

Replace `user` with your username on the remote server, and `slurm-server` with the hostname or IP address of the remote
server. You will be prompted for your password on the remote server, and then the public key will be copied over to
the `authorized_keys` file.

After you have copied your public key to the remote server, you should be able to authenticate with the server using
your private key without having to enter your password.

```json
{
  "hostname": "slurm-server",
  "port": 22,
  "username": "user",
  "private_key_file": "~/.ssh/id_rsa",
  "key_password": "********"
}
```

The name of the file that stores the private key in an SSH key pair is typically `id_rsa`. This file is usually located in the `~/.ssh` directory in your home directory on Linux and macOS systems. The corresponding public key file is usually named `id_rsa.pub`.

## Testing study examples

> TODO

