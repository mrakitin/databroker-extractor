@echo on

plink.exe -v -N -L 27018:localhost:27017 -L 2200:localhost:22 -L 8012:localhost:8000 mrakitin@xf11id-srv1

pause
