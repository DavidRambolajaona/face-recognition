#import requests
from requests_html import HTMLSession
import numpy as np
import face_recognition
import pickle 
#from bs4 import BeautifulSoup
import re
import io
import os
import shutil
import random
import datetime
import requests

class Facebook() :

    URL_FB_MOBILE = "https://m.facebook.com"
    URL_FB = "https://facebook.com"

    # Box result of searching people by name, div class
    CLASS_BOX_SEARCH_PEOPLE = "j83agx80 l9j0dhe7 k4urcfbm"

    def __init__(self) :
        #self.session = requests.Session()
        self.session = HTMLSession()
        self.user_id = None
        self.session_file = "session.pkl"

    def req(self, url, method = "get", data = {}, render = False) :
        if method == "get" :
            r = self.session.get(url)
        else :
            r = self.session.post(url, data)
        if render :
            r.html.render()
        return r

    def save_session(self) :
        with open('session.pkl', 'wb') as f: 
            pickle.dump(self.session, f) 

    def login(self, email, pwd, max_attempt = 5, current_attempt = 1, use_session=True) :
        if use_session and os.path.isfile(self.session_file) :
            if current_attempt == 1 :
                print("Logging with session...")
            with open(self.session_file, 'rb') as f: 
                self.session = pickle.load(f) 
                self.user_id = self.session.cookies["c_user"]
                print("Logging by session is a success ! :D")
                return True
        else : 
            if use_session and current_attempt == 1 :
                print("Session file doesn't exist")
            print("Logging with requests...")
            print("Email : ", email)
            data = {}
            # Retrieving login page input values
            res = self.req(self.URL_FB_MOBILE)
            for input in res.html.find("input") :
                if "name" in input.attrs.keys() :
                    if "value" in input.attrs.keys() :
                        v = input.attrs["value"]
                    else :
                        v = ""
                    data[input.attrs["name"]] = v
            data["email"] = email
            data["pass"] = pwd
            data["login"] = "Log In"
            action_url = res.html.find("form")[0].attrs["action"]
            
            # Logging
            res = self.req(self.URL_FB_MOBILE + action_url, "post", data)
            if 'c_user' in self.session.cookies.keys() :
                self.user_id = self.session.cookies["c_user"]
                self.save_session()
                print("Logged after ", current_attempt, " attempts :D ! ID : ", self.user_id)
                return True
            elif current_attempt < max_attempt :
                curr = current_attempt + 1
                self.login(email, pwd, current_attempt = curr, use_session=use_session)
            else :
                print("Not logged :( despite ", current_attempt, " attempts")
                return False

    def search_user_by_name(self, user_name, max = 5) :
        # !!! Abandonned
        users_found = []
        formatted = user_name.replace(" ", "%20")
        print(formatted)
        res = self.req(self.URL_FB_MOBILE + "/search/top/?q=" + formatted)
        print(res["r"].html)

        return users_found

    def get_fullname(self, user_id) :
        res = self.req(self.URL_FB_MOBILE + "/" + str(user_id), render = True)
        # Name
        fullname = res.html.find("#cover-name-root")
        if len(fullname) > 0 :
            fullname = fullname[0].text
        else :
            fullname = ''
        alternate_name = res.html.find(".alternate_name")
        if len(alternate_name) > 0 :
            alternate_name = alternate_name[0].text
            fullname = fullname.replace(alternate_name, '').strip()
            alternate_name = alternate_name[1:(len(alternate_name)-1)]
        else :
            alternate_name = ''
        return fullname
        
        res = self.req("https://web.facebook.com/" + str(user_id), render = True)
        with open("profil.html", "w", encoding='utf-8') as f :
            f.write(res.html.html)
        return None
        img = res.html.find("a")
        for i in img :
            if "href" in i.attrs.keys() and i.attrs["href"] == "/photo.php?fbid=3691940797577539&id=100002849650660&set=a.106210962817225&refid=13&__tn__=%2B%3D" :
                print(i)

    def get_photos(self, user_id, album = "pdp", max = 50, face_only = False) :
        # Naviguer sur la page de la liste des albums
        res = self.req(self.URL_FB_MOBILE + "/" + str(user_id) + "/photos", render = False)
        links = res.html.find("a")
        link_to_album_php = ""
        # Identifier et choisir l'album correspondant
        for link in links :
            if "href" not in link.attrs.keys():
                continue
            if (album == "pdp" and link.text == "Photos de profil") or (album == "pdc" and link.text == "Photos de couverture") or (album == "self" and "photoset" in link.attrs["href"]) :
                link_to_album_php = self.URL_FB_MOBILE + link.attrs["href"]
                break
        photos = []
        photos_id = []
        if not len(link_to_album_php) == 0 :
            # Choisir la première photo
            res = self.req(link_to_album_php, render = False)
            links = res.html.find("#thumbnail_area a")
            if album == "self" :
                links = res.html.find("td.s a")
            i = 0
            photo_id = False
            for link in links :
                if "href" in link.attrs.keys() and "fbid=" in link.attrs["href"] :
                    photo_id = link.attrs["href"].split("fbid=")[1].split("&")[0]
                    href = link.attrs["href"]
                    break

            # A partir de la première photo on passe à la photo suivante
            while photo_id and i < max :
                if photo_id in photos_id :
                    break
                print(i, " : ", photo_id)
                res = self.req(self.URL_FB + href, render = False)
                imgs = res.html.find("img")
                max_width = 0
                max_img = ''
                alt = ''
                imext = ''
                for img in imgs :
                    if "width" in img.attrs.keys() and int(img.attrs["width"]) > max_width :
                        max_width = int(img.attrs["width"])
                        max_img = img.attrs["src"]
                        imext = max_img.split("?")[0].split(".")[-1]
                        if "alt" in img.attrs.keys() :
                            alt = img.attrs["alt"]
                if alt == "Facebook logo" :
                    print("THERE IS SOMETHING WRONGG")
                    break
                # Check if there is a face if face_only mode
                if face_only :
                    self.download_photo(max_img, "here."+imext)
                    im = face_recognition.load_image_file("here."+imext)
                    face_locations = face_recognition.face_locations(im)
                    os.remove("here."+imext)
                    nb_faces = len(face_locations)
                    if nb_faces > 0 :
                        print("-> face : ", nb_faces)
                    else :
                        print("-> NO face")
                    if nb_faces == 0 :
                        i -= 1
                    else :
                        photos.append({"photo_id": photo_id, "src": max_img, "alt": alt})
                else :
                    photos.append({"photo_id": photo_id, "src": max_img, "alt": alt})

                photos_id.append(photo_id)
                res = self.req(self.URL_FB_MOBILE + "/photo.php?fbid=" + str(photo_id), render = False)
                links = res.html.find("a")
                for a in links :
                    if "href" in a.attrs.keys() and "%2B%3D" in a.attrs["href"] :
                        photo_id = a.attrs["href"].split("fbid=")[1].split("&")[0]
                        href = a.attrs["href"]
                        break
                    else :
                        photo_id = False
                i += 1
        return photos

    def get_friends(self, user_id, max = 10000) :
        url = self.URL_FB_MOBILE + "/" + str(user_id) + "/friends"
        friends = []
        res = self.req(url)
        nb_friends = res.html.find("h3.ca")
        i = 0
        if len(nb_friends) > 0 :
            nb_friends = res.html.find("h3.ca")[0].text.replace("Amis", "").replace("(", "").replace(")", "").replace(" ", "")
        while True :
            friend_html = res.html.find("td.w.t")
            if len(friend_html) > 0 :
                for fr in friend_html :
                    name = fr.find("a")[0].text
                    try :
                        id = fr.find("a")[1].attrs["href"].split("id=")[1].split("&")[0]
                    except IndexError :
                        if "profile.php" in fr.find("a")[0].attrs["href"] :
                            id = fr.find("a")[0].attrs["href"].split("?id=")[1].split("&")[0]
                        else :
                            id = fr.find("a")[0].attrs["href"].split("/")[1].split("?")[0]
                    print(name, " : ", id)
                    friends.append({"name": name, "user_id": id})
                    print("Nb friends until now : ", len(friends))
                    i += 1
                    if i >= max :
                        return friends
                if len(res.html.find("#m_more_friends a")) > 0 :
                    url = self.URL_FB_MOBILE + res.html.find("#m_more_friends a")[0].attrs["href"]
                    res = self.req(url)
                else :
                    return friends
            else :
                return friends

    def download_photos(self, photos, directorypath = '') :
        if directorypath == '' :
            directorypath = os.path.join(os.getcwd(), 'photos', 'all')
        if not os.path.exists(directorypath) :
            os.makedirs(directorypath)
        for photo in photos :
            ext = photo["src"].split("?")[0].split(".")[-1]
            filename = self.generateName() + '.' + ext
            path = os.path.join(directorypath, filename)
            self.download_photo(photo["src"], path)
            print("Downloaded : ", filename)

    def download_photo(self, link, path) :
        r = requests.get(link, stream=True)
        with open(path, 'wb+') as f :
            shutil.copyfileobj(r.raw, f)

    def generateName(self) :
        randomletters = ''
        for i in range(6) :
            randomletters += random.choice("abcdefghijklmnopqrstuvwxz")
        name = datetime.datetime.now().strftime("%b_%d_%Y %H_%M_%S") + ' ' + randomletters
        return name

    def get_distance_images(self, faces, face_to_compare) :
        faces_encoding = []
        for face in faces :
            faces_encoding.append(face_recognition.face_encodings(face_recognition.load_image_file(face))[0])
        face_to_compare_enc = face_recognition.face_encodings(face_recognition.load_image_file(face_to_compare))[0]
        distances = face_recognition.face_distance(faces_encoding, face_to_compare_enc)
        res = []
        for i, dist in enumerate(distances) :
            res.append({"image_path": faces[i], "distance": dist})
        return sorted(res, key=lambda k : k["distance"])

    def get_distance_image(self, face_model_enc, face_current_enc) :
        return face_recognition.face_distance([face_model_enc], face_current_enc)[0]

    def hasFace(self, path) :
        im = face_recognition.load_image_file(path)
        face_locations = face_recognition.face_locations(im)
        return len(face_locations) > 0

    def get_image_encoding(self, path) :
        im = face_recognition.load_image_file(path)
        encoding = face_recognition.face_encodings(im)[0]
        return encoding
        
if __name__ == "__main__" :
    fb = Facebook()
    #if fb.login("biotech000001@gmail.com", "Bloodlad666") :
    if fb.login("lunerougeflunflik@gmail.com", "Bloodlad666") :
        #fb.get_main_info_user(100027315068475)
        #fb.photos(100002849650660)
        user = 'medusadusa149'
        #user = 100007045755147
        photos = fb.get_photos(user, album="pdp", max = 20, face_only=True)
        print(photos)
        fb.download_photos(photos, 'photos/faces/' + str(user))
    """l = []
    for f in os.listdir("photos/faces/100002849650660/") :
        path = os.path.join("photos/faces/100002849650660/", f)
        l.append(path)
    distance = fb.get_distance_images(l, "photos/faces/tanelmikazuchi/Jul_10_2021 11_09_32 xoncoj.jpg")
    print(distance)"""