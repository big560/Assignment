# Assignment
# IBM

## Step 1:

Open cmd

```
git clone https://github.com/big560/Assignment.git
cd IBM
```
## Step 2
```
pip install virtualenv
python -m venv venv
```

If Windows OS
```
.\venv\Scrips\activate
pip install -r requirements.txt

uvicorn main:app --reload
```

If Linux Os
```
source venv/bin/activate
pip install -r requirements.txt

uvicorn main:app --reload
```
