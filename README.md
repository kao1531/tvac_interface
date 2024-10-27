# tvac_interface
Required packages: 
```
pip install dash
pip install pandas
```
To run the application: 
Make sure that the script is executable:
```
chmod +x run_tvac.sh
```
Execute the script to run the application:
```
./run_tvac.sh
```
The interface can then be accessed at http://127.0.0.1:8050/

To run on Raspberry Pi: 

Create a new virtual environment:
```
python3 -m venv tvac
```
Activate the virtual environment:
```
source tvac/bin/activate
```
Once the virtual environment has been activated, the required packages above can be downloaded and the application can be run.
