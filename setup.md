# Multiscale Setup
- [Multiscale Client Setup](#multiscale-client-setup)
- [Multiscale Server Setup](#multiscale-server-setup)

# Multiscale Client Setup
## Obtain the Multiscale Client
Dependencies:
 - python2 or python3
 - girder-client

The multiscale client is located in the same repository as the multiscale server. You can obtain it via:

`git clone https://github.com/psavery/multiscale`

Then, `cd` into the `multiscale` directory, and run `pip install -e .` in order to install the client. You can then
run the client with the `multiscale-client` executable that should now be in your path.

The primary dependency for the multiscale client is the girder client v2.4.0. Currently, this version of the girder
client is only available by installing it from 
[its repository](https://github.com/girder/girder/tree/master/clients/python) with `pip install -e .`.

## Setup an API Key
In order to use the multiscale client, you need an api key for the server.

Using a web browser, open the web page that the server is on, log in, click your user name in the top right corner, and
then click "My account". Click on "API Keys"->"Create new key". Enter whatever you would like, but the key needs read
and write access to your private files. Then click "show" to see the key.

Before running the multiscale client, set an environment variable named `MULTISCALE_API_KEY`, and set its value to the
value of the key.

## Run the Multiscale Client
Before running the multiscale client, make sure your api key is set up properly
(see [Setup an API Key](#setup-an-api-key) above).
You may also wish to set an environment variable for the api url with the environment variable `MULTISCALE_API_URL`
(the alternative is to specify the api url with the `-u` flag every time you run the client).

The primary dependency for the multiscale client is the girder client. Make sure your python environment has access to
the girder client.

The client is called `multiscale-client`, and should be in your path after running `pip install -e .`
[multiscale repository](https://github.com/psavery/multiscale).

You can find sample input directories [here](https://github.com/psavery/multiscale/releases/tag/samples).

Simply unzip one of them and run `multiscale-client submit <command> <unzipped_sample>` for a test. It will upload the 
data onto the girder
server in a private folder in the root called 'multiscale\_data', and the server should begin the simulation. You can check
the status of the job with `multiscale-client list`, and you can check the log with `multiscale-client log <jobId>`. When the
status is `SUCCESS`, you can download the output with `multiscale-client download <jobId>` (you could also download the 
input if you used the `-i` flag after the `download` argument).

See `multiscale-client --help` for more info, or `multiscale-client <command> --help` for more info about a specific command.

# Multiscale Server Setup

The primary dependencies that are needed to get the multiscale server running are as follows:
- python2 or python3
- mongodb-server
- rabbitmq-server
- nodejs
- docker
- girder
- girder-worker

Note that you need to be able to run `docker` without `sudo`.

The necessary docker images are as follows:
- openchemistry/albany
- openchemistry/dream3d
- openchemistry/smtk

The following script provides most of the setup for installing girder, girder\_worker, and the multiscale plugin on
Ubuntu 16.04.

```bash
################
# Begin Script #
################

# Install system deps
sudo apt update
sudo apt install -y git python3-dev virtualenv gcc curl \
  libffi-dev libjpeg-dev libldap2-dev libsasl2-dev libssl-dev \
  make zlib1g-dev software-properties-common

# Install the latest nodejs
curl -sL https://deb.nodesource.com/setup_10.x | sudo bash -
sudo apt install -y nodejs
# Update npm
sudo npm install -g npm

# Install and start mongodb
sudo apt install -y mongodb-server
sudo service mongodb start  # may be unnecessary if ubuntu starts it for you
# Enable mongodb to run on startup with 'sudo systemctl enable mongodb-server'

# Install and start rabbitmq
sudo apt install -y rabbitmq-server
sudo service rabbitmq-server start  # may be unnecessary if ubuntu starts it for you
# Enable rabbitmq to run on startup with 'sudo systemctl enable rabbitmq-server'

# Install docker and pull the albany image
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
sudo apt update
sudo apt install -y docker-ce
sudo docker pull openchemistry/albany
sudo docker pull openchemistry/dream3d
sudo docker pull openchemistry/smtk

# Set up the multiscale server
mkdir multiscale_server
cd multiscale_server
virtualenv -p /usr/bin/python multiscale_env
source multiscale_env/bin/activate

git clone https://github.com/girder/girder
git clone https://github.com/girder/girder_worker
git clone https://github.com/psavery/multiscale

# Add our plugin to the girder plugins
ln -s $PWD/multiscale/girder/multiscale $PWD/girder/plugins/multiscale

# Install girder
pushd .
cd girder
pip install -e .
popd

# Install girder_worker
pushd .
cd girder_worker
pip install -e .
popd

# Prevent some strange click errors
export LC_ALL=C.UTF-8
export LANG=C.UTF-8

# Install web stuff for girder
pushd .
cd girder
girder-install web
popd

#################
# End of Script #
#################
```
Note that before starting the server, you need to be able to run `docker` without `sudo`.

## Set Up Girder Further via the Web Interface

Once this is all set up, you may start the girder server by activating the virtual environment
(`source /multiscale_server/multiscale_env/bin/activate`) and running `girder-server` (you can change the host ip and
port number with the `-H` and `-p` flags, respectively).

Connect to your girder server with your web browser. If you are running the server locally, then you may just need to go
to http://localhost:8080

Create an account. The first account is an administrator account.

Go to AdminConsole-\>Assetstores and add an asset store. You can just add one to the local file system if you would like.

Go to AdminConsole-\>Plugins and enable the "Multiscale Modeling" plugin. This should automatically enable the "Jobs"
and "Remove Worker" plugins.

You need to restart the girder server for these changes to take effect.

(Note: after enabling jobs, you may optionally run `girder-install web` again in order to build the web interface for
the jobs plugin, which is convenient for tracking and canceling jobs).

If you wish to start the girder-server as a background process, you may wish to set a log file in the girder
configuration. See the girder docs for more details.


## Start girder\_worker
You may also start the girder worker by activating the virtual environment
(`source /multiscale_server/multiscale_env/bin/activate`) and running `girder-worker`.

There are various settings you can change such as limiting the number of processes, time limits, log files, etc.

Both `girder-server` and `girder-worker` need to be running on the server in order to use the multiscale client.
