from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello World!"}


@app.get("/posts")
def get_posts():
    return {"data": "This is my first post."}

@app.post("/createposts")
def create_posts():
    return {"message": "succefully created posts"}