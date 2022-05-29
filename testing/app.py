import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime
import mysql.connector
from mysql.connector import Error
from mysql.connector import errorcode
from flask import Flask, render_template,request,redirect,url_for
from werkzeug.utils import secure_filename

UPLOAD_FOLDER='uploads'
ALLOWED_EXTENSIONS=set(['jpg','png','jpeg'])
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] =UPLOAD_FOLDER


@app.route('/')
def identity():
  return render_template('identity.html')


@app.route('/directing')

def directing():
 return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Invalid Credentials. Please try again.'
        else:
            return redirect(url_for('upload_file'))
    return render_template('login.html', error=error)



@app.route('/uploadfile',methods=['GET','POST'])
def upload_file():
      if request.method=='POST':
          file=request.files['file']
           
          file.save(os.path.join(app.config['UPLOAD_FOLDER'],secure_filename(file.filename)))
          return render_template('admin.html',msg="File has been uploaded successfully")
      return render_template('admin.html',msg="Please choose file")
  

path='uploads'
images=[]
imgLabel=[]
mylst=os.listdir(path)
   

for cl in mylst:
    curimg=cv2.imread(f'{path}\\{cl}')
    images.append(curimg)
    imgLabel.append(os.path.splitext(cl)[0])
      

def findEncodings(images):
     encodLst=[]
     for img in images:
         img=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
         encode=face_recognition.face_encodings(img)[0]
         encodLst.append(encode)
     return encodLst

    
encodlstKnowFaces=findEncodings(images)

           
def markAttendance2(name,inTime,inDate):
     
            
     connection=mysql.connector.connect(host="localhost", database="markingattendance", user="root",passwd="Vaish12/08")
     mysql_insert_query="INSERT INTO emp_attendance(emp_name,in_time,in_date) VALUES (%s,%s,%s)"  
     mycursor=connection.cursor()
     val=(name,inTime,inDate)
     mycursor.execute(mysql_insert_query,val)
     connection.commit();
     mycursor.execute("SELECT * FROM emp_attendance")
     myresult=mycursor.fetchall()
     for x in myresult:
       print(x)
     mycursor.close();

@app.route('/test')
def test():
 webcam=cv2.VideoCapture(0)
 nm="a"
 
 while True:
    success, img=webcam.read()
    imgS=cv2.resize(img,(0,0),None,0.25,0.25)
    imgS=cv2.cvtColor(imgS,cv2.COLOR_BGR2RGB)

    faceCurFrm= face_recognition.face_locations(imgS)
    encodeCurFrm=face_recognition.face_encodings(imgS,faceCurFrm)

    for encodFace, faseLocation in zip(encodeCurFrm,faceCurFrm):
        maches=face_recognition.compare_faces(encodlstKnowFaces,encodFace)
        faceDis=face_recognition.face_distance(encodlstKnowFaces,encodFace)
        
        machesIndex=np.argmin(faceDis)

        if maches[machesIndex]:
            name = imgLabel[machesIndex].upper()
            # print(name)
            y1,x2,y2,x1=faseLocation
            y1,x2,y2,x1 = y1*4,x2*4,y2*4,x1*4
            cv2.rectangle(img,(x1,y1),(x2,y2),(0,255,0),3)
            cv2.rectangle(img,(x1,y2-35),(x2,y2),(0,255,0),cv2.FILLED)
            cv2.putText(img,name,(x1+6,y2-6),cv2.FONT_HERSHEY_COMPLEX ,1,(255,255,255),2)
            
            crTime=datetime.now().time()
            crDate=datetime.now().date()
            if name!=nm:
                markAttendance2(name,str(crTime),str(crDate))
                nm=name
            
           
    
    
    cv2.imshow('Frame',img)
    if cv2.waitKey(1) & 0xFF == ord('q'): 
        break

 webcam.release()
 cv2.destroyAllWindows()
 return render_template('index.html')
if __name__ == "__main__":
        app.run(debug=True)
