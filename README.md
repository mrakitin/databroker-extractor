# databroker-extractor - tools and utilities for experiments

Used to obtain data from beamline databroker servers and perform initial analysis
(e.g., calculation of the FWHM of the undulator harmonics).

### Installation instructions:

Install miniconda from https://conda.io/miniconda.html. Then create the environment for databroker:
```bash
conda create --name databroker python=3.6 numpy scipy matplotlib
activate databroker
pip install -r https://raw.githubusercontent.com/mrakitin/databroker-extractor/master/requirements.txt
pip install git+https://github.com/mrakitin/databroker-extractor
```

### Remote access of the data on the CHX beamline of NSLS-II using databroker.

Access DataBroker data from outside the gateway:
- Prepare SSH config file:
```bash
$ cat ~/.ssh/config
Host chx-srv1
    User mrakitin
    Hostname xf11id-srv1
    LocalForward 27018 localhost:27017
    ProxyCommand ssh mrakitin@box64-3.nsls2.bnl.gov nc %h %p 2> /dev/null
```

- Create `/XF11ID/data/` dir on a local machine and make a current user/group to own the dir.

- Configure datastore/filestore:
```bash
$ cat ~/.config/metadatastore/connection.yml
database: datastore
port: 27018
host: localhost
timezone: US/Eastern
```

```bash
$ cat ~/.config/filestore/connection.yml
host: localhost
port: 27018
database: filestore
```

- Make a tunnel to go through a firewall:
```bash
ssh -fN -o ExitOnForwardFailure=yes chx-srv1 2>/dev/null && sshfs mrakitin@chx-srv1:/XF11ID/data /XF11ID/data/
```

- Use conda environment for the databroker tutorial - https://github.com/NSLS-II/broker-tutorial.

- Run the script to collect data:
```bash
$ databroker-extractor -b chx -s 19002 19003  # saves data and plots for the scans 19002 and 19003
```
```bash
$ databroker-extractor -b chx -p 19002 19003  # plots data for the scans 19002 and 19003
```
