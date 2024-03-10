from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import google.oauth2.id_token
from google.auth.transport import requests
from google.cloud import firestore
import starlette.status as status

app=FastAPI()
EV1 = {
    'year': 2000,
    'cost': 4000.0,
    'power': 12.0,
    'manufacturer': 'Suzuki',
    'battery_size': 65.0,
    'wltp_range': 400,
    'name': 'Mehran New',
    'reviews': [
        {'rating': 8, 'text': 'Lorem ipsum dolor sit amet,Lorem ipsum dolor sit amet','submission_date': '2021-01-02'},
         {'rating': 5, 'text': 'Lorem ipsum dolor sit amet,Lorem ipsum dolor sit amet','submission_date': '2021-01-05'},
         {'rating': 3, 'text': 'Lorem ipsum dolor sit amet,Lorem ipsum dolor sit amet','submission_date': '2021-01-09'},
    ]
}



EV2={'year': 2007, 'cost': 1000, 'power': 400, 'manufacturer': 'Suzuki', 'battery_size': 65, 'wltp_range': 100, 'name': 'Mehran'}
firebase_request_adapter=requests.Request()
firestore_db=firestore.Client()

print(type(EV1),type(EV2))
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
    

@app.get("/add-ev",response_class=HTMLResponse)
async def root(request:Request):
    id_token=request.cookies.get("token")
    error_message="no error"
    user_token=validateFirebaseToken(id_token)
    
    if not user_token:
        return templates.TemplateResponse('home.html',{'request':request,'error_info':"You are not logged in"})
    return templates.TemplateResponse('addEv.html',{'request':request,'name':'asad'})
    
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

    
    ev_collection = firestore_db.collection('ev')
    existing_ev_query = ev_collection.where('manufacturer', '==', manufacturer) \
                                     .where('name', '==', name) \
                                     .where('year', '==', year) \
                                     .get()

    if existing_ev_query:
       return RedirectResponse(url='/add-ev?error=EV already exists')

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

@app.get("/search-ev",response_class=HTMLResponse)
async def login(request:Request):
    return templates.TemplateResponse('searchEv.html',{'request':request,'ev':{}})

@app.post("/search-ev")
async def search_evs(request: Request):
    form=await request.form()
    error_msg=""
    attribute = form["attribute"]
    value = form["value"]
    min_value = form["min_value"]
    max_value = form["max_value"]
    query = firestore_db.collection('ev')
    print(attribute,value,min_value,max_value)
    if value:
        query = query.where(attribute, '==', value)
        print("if")

    elif min_value is not None and max_value is not None:
        query = query.where(attribute, '>=', min_value).where(attribute, '<=', max_value)
        print("elif")
    else:
        query = query.stream()
        print("else")
    results = query.stream()
    evs = [doc.to_dict() for doc in results]
    print("Results",evs)
    if not evs:
        error_msg="no EV found"
    return templates.TemplateResponse('searchEv.html',{'request':request,'evs':evs,'error_msg':error_msg})
    
@app.get("/view/{ev_name}")
async def get_ev_by_name_and_reviews(request:Request,ev_name: str):
    try:
        ev_query = firestore_db.collection('ev').where('name', '==', ev_name).stream()
        ev_details = None
        ev_doc_id = None
        for doc in ev_query:
            ev_details = doc.to_dict()
            ev_doc_id = doc.id
            break  
        if not ev_details:
            raise HTTPException(status_code=404, detail="EV not found")
        reviews_query = firestore_db.collection('ev').document(ev_doc_id).collection('reviews').order_by('submitted_at',
                                                                                                         direction=firestore.Query.DESCENDING).stream()
        reviews = [review.to_dict() for review in reviews_query]
        ev_details['reviews'] = reviews
        average_rating = sum(int(review['rating']) for review in reviews) / len(reviews)
        
        return templates.TemplateResponse('evInfo.html', {'request': request, 'ev': ev_details, 'reviews': reviews, 'average_rating': average_rating})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
  
@app.get("/edit-ev/{ev_name}",response_class=HTMLResponse)
async def root(request:Request,ev_name:str):
    
    id_token=request.cookies.get("token")
    user_token=validateFirebaseToken(id_token)
    if not user_token:
        return templates.TemplateResponse('home.html',{'request':request,'name':'','user_token':None,'error_info':"You are not logged in"})

    try:
        ev_query = firestore_db.collection('ev').where('name', '==', ev_name).stream()
        ev_details = None
        for doc in ev_query:
            ev_details = doc.to_dict()
        if not ev_details:
            raise HTTPException(status_code=404, detail="EV not found")
        
        return templates.TemplateResponse('editEv.html',{'request':request,'ev':ev_details})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    
    # evs_query = firestore_db.collection('ev').where('name', '==', value=name).stream()
    # ev = evs_query.to_dict()
    # return templates.TemplateResponse('editEv.html',{'request':request,'ev':ev})

@app.post("/update-ev/{ev_name}",response_class=RedirectResponse)
async def root(request:Request,ev_name:str):
    id_token = request.cookies.get("token")
    user_token = validateFirebaseToken(id_token)
    if not user_token:
       return RedirectResponse('/')
    
    form=await request.form()
    name = form['name']
    manufacturer = form['manufacturer']
    year = int(form['year'])  
    battery_size = float(form['battery_size'])  
    wltp_range = int(form['wltp_range'])  
    cost = float(form['cost'])  
    power = float(form['power']) 

    updates = await request.form()
     # Add new EV to the database
    updates = {
        'name': name,
        'manufacturer': manufacturer,
        'year': year,
        'battery_size': battery_size,
        'wltp_range': wltp_range,
        'cost': cost,
        'power': power
    }
    ev_query = firestore_db.collection('ev').where('name', '==', ev_name).get()
    ev_docs = list(ev_query)
    if len(ev_docs) == 0:
        raise HTTPException(status_code=404, detail=f"EV named '{ev_name}' not found")
    ev_doc_ref = ev_docs[0].reference
    try:
        ev_doc_ref.update(updates)
        return RedirectResponse(url='/', status_code=status.HTTP_303_SEE_OTHER)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update EV: {str(e)}")
    
@app.get("/delete-ev/{ev_name}",response_class=HTMLResponse)
async def delete_ev_by_name(request:Request,ev_name: str):
    id_token = request.cookies.get("token")
    user_token = validateFirebaseToken(id_token)
    if not user_token:
       return RedirectResponse('/')
    try:
        docs_to_delete = firestore_db.collection('ev').where('name', '==', ev_name).stream()
        for doc in docs_to_delete:
            doc.reference.delete()
        return RedirectResponse(url='/', status_code=status.HTTP_303_SEE_OTHER)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/compare-ev-form",response_class=HTMLResponse)
async def login(request:Request):
    evs_query = firestore_db.collection('ev').stream()
    evs = [doc.to_dict() for doc in evs_query]
    
    return templates.TemplateResponse('compareEvForm.html',{'request': request,
        # 'user_info': user_info,
        'evs_query': evs_query,
        'evs':evs})

@app.post("/compare-evs",response_class=HTMLResponse)
async def login(request:Request):
    form=await request.form()
    ev1_id = form['ev1']
    ev2_id = form['ev2']
    evs_data = {}
    for ev_name in [ev1_id, ev2_id]:
        ev_query = firestore_db.collection('ev').where('name', '==', ev_name).limit(1).stream()
        ev_document = list(ev_query)
        if not ev_document:
            raise HTTPException(status_code=404, detail=f"EV named {ev_name} not found")
        ev_data = ev_document[0].to_dict()
        evs_data[ev_name] = ev_data
    
    
    return templates.TemplateResponse('compareEv.html',{'request':request,'ev1':evs_data[ev1_id],'ev2':evs_data[ev2_id]})

    # try:
    #     ev_query = firestore_db.collection('ev').where('name', '==', ev1_id).stream()
    #     ev_details = None
    #     for doc in ev_query:
    #         ev_details = doc.to_dict()
    #     if not ev_details:
    #         raise HTTPException(status_code=404, detail="EV not found")
        
    #      ev_query = firestore_db.collection('ev').where('name', '==', ev1_id).stream()
    #     ev_details = None
    #     for doc in ev_query:
    #         ev_details = doc.to_dict()
    #     if not ev_details:
    #         raise HTTPException(status_code=404, detail="EV not found")

    #     return templates.TemplateResponse('editEv.html',{'request':request,'ev':ev_details})
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    return templates.TemplateResponse('compareEv.html',{'request':request,'ev1':EV1,'ev2':EV2})
    
@app.post("/submit-review/{ev_name}",response_class=RedirectResponse)
async def login(request:Request,ev_name:str):
    review_data = await request.form()
    review_text = review_data["review"]
    rating = int(review_data["rating"])
    print(rating,review_text)
    if not review_text:
        raise HTTPException(status_code=400, detail="Invalid review or rating")
    ev_query = firestore_db.collection('ev').where('name', '==', ev_name).limit(1).get()
    ev_docs = list(ev_query)
    if len(ev_docs) == 0:
        raise HTTPException(status_code=404, detail=f"EV named '{ev_name}' not found")
    ev_doc_ref = ev_docs[0].reference
    review_doc_ref = ev_doc_ref.collection('reviews').add({
        "review": review_text,
        "rating": rating,
        "submitted_at": firestore.SERVER_TIMESTAMP

    })
    # return {"message": "Review submitted successfully", "review_id": review_doc_ref[1].id}
    return RedirectResponse(url='/', status_code=status.HTTP_303_SEE_OTHER)


# @app.get("/ev-info/{name}", response_class=HTMLResponse)
# async def ev_info(request: Request, name: str):
#     if 'reviews' in EV1:
#         reviews = EV1['reviews']
#         for i in range(len(reviews)):
#             for j in range(i + 1, len(reviews)):
#                 if reviews[i]['submission_date'] < reviews[j]['submission_date']:
#                     # Swap the reviews
#                     reviews[i], reviews[j] = reviews[j], reviews[i]
#     else:
#         reviews = []

#     # Calculate the average rating
#     if reviews:
#         average_rating = sum(review['rating'] for review in reviews) / len(reviews)
#     else:
#         average_rating = "No reviews yet"

#     return templates.TemplateResponse('evInfo.html', {'request': request, 'ev': EV1, 'reviews': reviews, 'average_rating': average_rating})


   