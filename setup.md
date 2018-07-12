The following script provides most of the setup for installing girder, girder\_worker, and the multiscale plugin on Ubuntu 16.04.

```
################
# Begin Script #
################

# Install system deps
sudo apt update
sudo apt install -y git python3-dev virtualenv gcc curl libffi-dev libjpeg-dev libldap2-dev libsasl2-dev libssl-dev make zlib1g-dev software-properties-common

# Install the latest nodejs
curl -sL https://deb.nodesource.com/setup\_10.x | sudo bash -
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
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb\_release -cs) stable"
sudo apt update
sudo apt install -y docker-ce
sudo docker pull openchemistry/albany

# Set up the multiscale server
mkdir multiscale\_server
cd multiscale\_server
virtualenv -p /usr/bin/python3 multiscale\_env
source multiscale\_env/bin/activate

git clone https://github.com/girder/girder
git clone https://github.com/girder/girder\_worker
git clone https://github.com/psavery/multiscale

# Add our plugin to the girder plugins
ln -s $PWD/multiscale/girder/multiscale $PWD/girder/plugins/multiscale

# Install girder
pushd .
cd girder
pip install -e .
popd

# Install girder\_worker
pushd .
cd girder\_worker
pip install -e .
popd

# Prevent some strange click errors
export LC\_ALL=C.UTF-8
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

##### Set up girder further via the web interface #####

Once this is all set up, you may start the girder server by activating the virtual environment (source /multiscale\_server/multiscale\_env/bin/activate) and running 'girder-server' (you can change the host ip and port number with the -H and -p flags, respectively).

Connect to your girder server with your web browser. If you are running the server locally, then you may just need to go to http://localhost:8080

Create an account. The first account is an administrator account.

Go to AdminConsole-\>Assetstores and add an asset store. You can just add one to the local file system if you would like.

Go to AdminConsole-\>Plugins and enable the "Multiscale Modeling" plugin. This should automatically enable the "Jobs" and "Remove Worker" plugins.

You need to restart the girder server for these changes to take effect.

(Note: after enabling jobs, you may optionally run 'girder-install web' again in order to build the web interface for the jobs plugin, which is convenient for tracking and canceling jobs).

If you wish to start the girder-server as a background process, you may wish to set a log file in the girder configuration. See the girder docs for more details.


##### Set up api key #####
In order to use the multiscale client, you need an api key for this server.

Open the girder web page in your browser, click on your user name in the top right corner, and then click "My account". Click on "API Keys"->"Create new key". Enter whatever you would like, but the key needs read and write access to your private files. Then click "show" to see the key.

Before running the multiscale client, set an environment variable named MULTISCALE\_API\_KEY, and set its value to the value of the key.


##### Start girder\_worker #####
You may also start the girder worker by activating the virtual environment (source /multiscale\_server/multiscale\_env/bin/activate) and running 'girder-worker'.

There are various settings you can change such as limiting the number of processes, time limits, log files, etc.


##### Run multiscale client #####
Make sure your api key is set up properly (see "Set up api key" above).

The primary dependency is the girder client. Make sure your python environment has access to the girder client (it will if you use the virtual environment set up above).

The client is called "multiscale.py", and it is located in the "client" directory of https://github.com/psavery/multiscale

You can get a sample albany input directory from here:  https://github.com/psavery/multiscale/releases/tag/albany\_sample1

Simply unzip it and run 'multiscale.py submit albany albany\_sample1' for a test. It will place the data on the girder server in a private folder in the root called 'multiscale\_data'.

See multiscale.py --help for more info, or multiscale.py \<command\> --help for more info about a specific command.
