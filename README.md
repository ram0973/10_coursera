# Task [№10](https://devman.org/challenges/10/) from [devman](https://devman.org)
## Requirements
```
Python 3.5.2+
requests
lxml
openpyxl
babel
tqdm
```
## Setup
```    
git clone https://github.com/ram0973/10_coursera.git
cd 10_coursera
pip3 install -r requirements.txt
```
## Description
The user enters an optional argument count - the number of courses to display.
And one mandatory - outfile - the file name with the result
The script loads the urls of courses, courses received urls randomly shuffled,
Next, the script retrieves data from
[Api](https://building.coursera.org/app-platform/catalog/)
The obtained data saves in file.
## Usage
``` 
python3 coursera.py --o result.xlsx
```
## License
[MIT](http://opensource.org/licenses/MIT)