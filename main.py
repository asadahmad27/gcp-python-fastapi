from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import google.oauth2.id_token
from google.auth.transport import requests
from google.cloud import firestore
import starlette.status as status

app=FastAPI()
firebase_request_adapter=requests.Request()
firestore_db=firestore.Client()
app.mount('/static',StaticFiles(directory='static'),name='static')
templates=Jinja2Templates(directory="templates")

def getUser(user_token):
    user=firestore_db.collection('users').document(user_token['user_id'])
    print(user,"user")
    if not user.get().exists:
        user={
            'name':"N/A",
            'age':0
        }
        user=firestore_db.collection('users').document(user_token['user_id']).set(user)
        
    return user

def validateFirebaseToken(id_token):
    if not id_token:
        return None

    user_token= None
    try:
        user_token=google.oauth2.id_token.verify_firebase_token(id_token,firebase_request_adapter)
    except ValueError as err:
        print(str(err))
    
    return user_token

@app.get("/",response_class=HTMLResponse)
async def root(request:Request):
    # id_token=request.cookies.get("token")
    # error_message="no error"
    # user_token=validateFirebaseToken(id_token)
    # user=None
    
    # if not user_token:
    #     return templates.TemplateResponse('home.html',{'request':request,'name':'','user_token':None,'error_info':"User not found"})
    # user=getUser(user_token)
    # return templates.TemplateResponse('home.html',{'request':request,'name':'asad','user_token':user_token,'user_info':user.get()})
    # id_token = request.cookies.get("token")
    # user_token = validateFirebaseToken(id_token)
    # user_info = None
    # if user_token:
    #     user_info = getUser(user_token).get()
    
    # Fetch all EVs from Firestore
    evs_query = firestore_db.collection('ev').stream()
    evs = [doc.to_dict() for doc in evs_query]
    print(evs,"Evs",evs_query)
    # Pass the EVs to the template
    return templates.TemplateResponse('home.html', {
        'request': request,
        # 'user_info': user_info,
        'evs_query': evs_query,
        'evs':evs
    })

@app.get("/add-ev",response_class=HTMLResponse)
async def root(request:Request):
    # id_token=request.cookies.get("token")
    # error_message="no error"
    # user_token=validateFirebaseToken(id_token)
    # user=None
    # if not user_token:
    #     return templates.TemplateResponse('home.html',{'request':request,'name':'','user_token':None,'error_info':"User not found"})
    # user=getUser(user_token)
    return templates.TemplateResponse('addEv.html',{'request':request,'name':'asad'})
    


@app.get("/edit-ev/{id}",response_class=HTMLResponse)
async def root(request:Request):
    # id_token=request.cookies.get("token")
    # error_message="no error"
    # user_token=validateFirebaseToken(id_token)
    # user=None
    # if not user_token:
    #     return templates.TemplateResponse('home.html',{'request':request,'name':'','user_token':None,'error_info':"User not found"})
    # user=getUser(user_token)
    return templates.TemplateResponse('editEv.html',{'request':request,'name':'asad'})
    

@app.post("/add-ev", response_class=RedirectResponse)
async def save_ev_page(request: Request):
    id_token = request.cookies.get("token")
    user_token = validateFirebaseToken(id_token)
    if not user_token:
            return RedirectResponse('/')
    user = getUser(user_token)
    form=await request.form()
    name = form['name']
    manufacturer = form['manufacturer']
    year = int(form['year'])  
    battery_size = float(form['battery_size'])  
    wltp_range = int(form['wltp_range'])  
    cost = float(form['cost'])  
    power = float(form['power']) 

    # Check if an EV with the same manufacturer, name, and year already exists
    ev_collection = firestore_db.collection('ev')
    # existing_ev_query = ev_collection.where('manufacturer', '==', manufacturer) \
    #                                  .where('name', '==', name) \
    #                                  .where('year', '==', year) \
    #                                  .get()

    # if existing_ev_query:
    #     # EV already exists, handle accordingly
    #     # For simplicity, redirecting to home with an error message (you might want to use Flash messages or another method to display errors)
    #     # You could also return to the add-ev page with an error message
    #     return RedirectResponse(url='/add-ev?error=EV already exists')

    # Add new EV to the database
    new_ev = {
        'name': name,
        'manufacturer': manufacturer,
        'year': year,
        'battery_size': battery_size,
        'wltp_range': wltp_range,
        'cost': cost,
        'power': power
    }
    ev_collection.add(new_ev)

    # Redirect to home or a success page after saving
    return RedirectResponse(url='/', status_code=status.HTTP_303_SEE_OTHER)

    # return templates.TemplateResponse('home.html', {'request': request, 'user_info': user.get(),'user_token':user_token})


@app.get("/login",response_class=HTMLResponse)
async def login(request:Request):
    id_token=request.cookies.get("token")
    error_message="no error"
    user_token=None
    if id_token:
        try:
            user_token=google.oauth2.id_token.verify_firebase_token(id_token,firebase_request_adapter)
        except ValueError as err:
            print(str(err))

    return templates.TemplateResponse('login.html',{'request':request,'name':'asad','user_token':user_token})
    

@app.get("/ev-info/{id}",response_class=HTMLResponse)
async def login(request:Request):
    return templates.TemplateResponse('evInfo.html',{'request':request,'ev':{}})
    
@app.get("/search-ev",response_class=HTMLResponse)
async def login(request:Request):
    return templates.TemplateResponse('searchEv.html',{'request':request,'ev':{}})

@app.get("/compare-ev-form",response_class=HTMLResponse)
async def login(request:Request):
    return templates.TemplateResponse('compareEvForm.html',{'request':request,'evs':{}})
    
@app.get("/compare-ev",response_class=HTMLResponse)
async def login(request:Request):
    return templates.TemplateResponse('compareEv.html',{'request':request,'ev1':{},'ev2':{}})
    
@app.post("/search-ev",response_class=HTMLResponse)
async def login(request:Request):
    return templates.TemplateResponse('searchEv.html',{'request':request,'ev':{}})
    