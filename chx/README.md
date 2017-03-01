# Remote access of the data on the CHX beamline of NSLS-II using databroker.

Access DataBroker data from outside the gateway:
---
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

- Run `python chxdb.py`, should produce something like:
```
/home/vagrant/miniconda2/envs/broker-tutorial/bin/python /home/vagrant/src/mrakitin/experiments/chx/chxdb.py
Scan ID: 1eff511d  Timestamp: 2017-02-28 22:20:19
Scan ID: 8f6a6004  Timestamp: 2017-02-28 22:34:54
Scan ID: 1f1422b4  Timestamp: 2017-02-28 23:06:50
Scan ID: 7949f1b0  Timestamp: 2017-02-28 22:47:22
Scan ID: daeb15e3  Timestamp: 2017-02-28 22:55:52
Scan ID: 6edfa33a  Timestamp: 2017-02-28 23:15:39
Scan ID: 74798cb6  Timestamp: 2017-02-28 23:31:17
Scan ID: dc2b5045  Timestamp: 2017-02-28 23:40:02
Scan ID: c4f95268  Timestamp: 2017-03-01 00:12:57
Scan ID: b2365717  Timestamp: 2017-03-01 00:25:05
Scan ID: ac99ddd0  Timestamp: 2017-02-28 23:52:18
Scan ID: b808a890  Timestamp: 2017-03-01 00:01:28
Scan ID: e23fb7a1  Timestamp: 2017-03-01 00:37:49
Scan ID: afc6da9e  Timestamp: 2017-03-01 00:41:12
Scan ID: e71b8b5f  Timestamp: 2017-03-01 00:45:35

Process finished with exit code 0
```
