import requests

def getJoke() :
    response = requests.get(
        'https://www.blagues-api.fr/api/random',
        headers={'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiODU1MDY4NTM3ODQ4OTg3NzEwIiwibGltaXQiOjEwMCwia2V5IjoiOGdhRkdpc3F4bDd0dFRINnNFeDh2U3hMbld0MEFtcDF1Q3hqVVZKWjZIejJBb0tJSDEiLCJjcmVhdGVkX2F0IjoiMjAyMS0wNi0xN1QxMzowMDoxNiswMDowMCIsImlhdCI6MTYyMzkzNDgxNn0.W3NvcWugudGinAtApPNDz1o_11Ecw4pby59TYpWgPts'}
    )
    r = response.json()
    joke = r["joke"]
    answer = r["answer"]
    return {"joke": joke, "answer": answer}