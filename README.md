## To run the server
**Before run, install the libraries in the app.py file
then run: python app.py**

**python version: 3.10.11**

If nothing is displayed, change this number: `num`to 0, 1, 2, ... , etc:

     app.py
      24 | cap  =  cv2.VideoCapture(num)


## To run the front
Add this in `package.json`:
     "private": true,
     ###"proxy": "http://127.0.0.1:5000",
     "dependencies": {

In the project directory `front`, you can run:

### `npm start`