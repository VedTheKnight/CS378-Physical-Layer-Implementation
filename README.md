# Instructions to run the code
- The submission folder can be obtained by unzipping the tar file `22b0413_22b1032_22b1054_22b1818.tar.gz`
- Run the files `sender.py` and `receiver.py` in two different machines. Always make sure to start the
reciever file before the sender file.
- The input format is the bitstring to be transmitted followed by the indices where error needs to be introduced.
- The command to run the files are `python3 sender.py < input.txt` and `python3 receiver.py` for a linux system and `Get-Content input.txt | python sender.py` and `python3 receiver.py` for windows.