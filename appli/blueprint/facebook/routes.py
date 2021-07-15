from flask import Blueprint, json, render_template, request, redirect, jsonify, url_for, abort, current_app
from werkzeug.utils import secure_filename

import numpy as np
from appli.service.facebook.Facebook import Facebook
from appli.models import db, User, Image, Upload, insert_first_data, Account
import datetime
import requests
import os
import json
from mimetypes import guess_extension, guess_type
import base64
from io import BytesIO
from PIL import Image as ImagePIL

facebook_bp = Blueprint('facebook_bp', __name__, template_folder='template', static_folder='static', static_url_path='/facebook-static')

PATH_IMAGE_UPLOAD = 'appli/blueprint/facebook/static/img/uploads/'
PATH_IMAGE_FACES = 'appli/blueprint/facebook/static/img/faces/'

@facebook_bp.route('/fb/api/similarity', methods=["POST"])
def similarity():
    if "file" not in request.form :
        return jsonify({"status": "error", "msg": "keyword_file_not_found"})
    uploaded_file = request.form["file"]
    if uploaded_file != '' :
        file_ext = guess_extension(guess_type(uploaded_file)[0])
        if file_ext not in [".jpg", ".png", ".gif", ".jpeg"]:
            return jsonify({"status": "error", "msg": "extension_not_supported"}) 

        upload = Upload()
        if "filename" in request.form :
            upload.up_original_name = request.form["filename"]
        

        fb = Facebook()
        filename = fb.generateName() + file_ext
        path_im = os.path.join(PATH_IMAGE_UPLOAD, filename)
        upload.up_filename = filename
        
        starter = uploaded_file.find(',')
        image_data = uploaded_file[starter+1:]
        image_data = bytes(image_data, encoding="ascii")
        im = ImagePIL.open(BytesIO(base64.b64decode(image_data)))
        im.save(path_im)

        hasface = fb.hasFace(path_im)
        upload.up_has_face = hasface
        upload.up_date_creation = datetime.datetime.utcnow()
        upload.up_ip_adress = request.remote_addr
        upload.up_user_agent = request.user_agent.string
        if not hasface :
            db.session.add(upload)
            db.session.commit()
            return jsonify({"status": "error", "msg": "no_face"})

        print("PROCESSING !")
        img_faces = getImgFaces(path_im)
        if len(img_faces) == 0 :
            return jsonify({"status": "error", "msg": "no_data"})

        top = []
        user_fb_ids = []
        top_unique = []
        for img in img_faces :
            top.append(img)
            if img["fb_user_id"] not in user_fb_ids :
                user_fb_ids.append(img["fb_user_id"])
                top_unique.append(img)

        upload.up_encoding = str(fb.get_image_encoding(path_im).tolist()).replace('[', '').replace(']', '').replace(' ', '')
        db.session.add(upload)
        db.session.commit()

        print("FINISHED")
        return jsonify({"status": "success", "top": top[:20], "top_unique": top_unique[:20]})
    else :
        return jsonify({"status": "error", "msg": "empty_file"})

@facebook_bp.route('/fb/drop-db')
def dropDb() :
    key = request.args.get("key")
    if key is not None and key == os.environ.get("SECRET_KEY_FBFACE") :
        db.drop_all()
        db.create_all()
        insert_first_data()
        return jsonify({"drop": True})
    else :
        return jsonify({"drop": False})

@facebook_bp.route('/fb/download')
def downloadFaces() :
    ret = {"success": True, "msg": ""}
    account = Account.query.filter(Account.account_active == True).order_by(Account.account_nb_use.asc()).first()
    fb = Facebook()
    if account is not None :
        account.account_nb_use += 1
        account.account_date_last_use = datetime.datetime.utcnow()
        if fb.login(account.account_email, account.account_password, use_session=False) :
            download(fb)
        else :
            account.account_active = False
            account.account_nb_problem += 1
            account.account_problem_info = "account_not_logged"
            ret["success"] = False
            ret["msg"] = "Account not logged with " + account.account_email
        db.session.commit()
    else :
        print("NO ACCOUNT ANYMORE !")
        ret["success"] = False
        ret["msg"] = "Account is none"
    return jsonify(ret)

def download(fb_obj, current_attempt = 1) :
    users_not_pic = User.query.filter(User.user_retrieved_pictures == False).order_by(User.user_date_creation.asc())
    print("NB USERS NOT PICTURE : ", users_not_pic.count())
    if users_not_pic.count() == 0 :
        users_not_friends = User.query.filter(User.user_retrieved_friends == False).order_by(User.user_date_creation.asc())
        print("NB USERS NOT FRIEND : ", users_not_friends.count())
        if users_not_friends.count() == 0 :
            users = User.query.all()
            print("NB USERS : ", len(users))
            if len(users) == 0 and current_attempt == 1 :
                user = User()
                user.user_fb_id = "david.rambolajaona"
                user.user_fb_name = "David Rambolajaona"
                friends = []
                user.user_friends = json.dumps(friends)
                user.user_retrieved_friends = False
                user.user_retrieved_pictures = False
                d = datetime.datetime.utcnow()
                user.user_date_creation = d
                db.session.add(user)
                db.session.commit()

                if current_attempt == 1 :
                    download(fb_obj, current_attempt = current_attempt + 1)
                else :
                    return False
            else :
                return False
        else :
            if current_attempt > 3 :
                return False
            user_fb_ids = [u.user_fb_id for u in User.query.with_entities(User.user_fb_id)]
            for user in users_not_friends[:2] :
                friends = fb_obj.get_friends(user.user_fb_id)
                friends_to_update = []
                for friend in friends :
                    friends_to_update.append(friend["user_id"])
                    if friend["user_id"] in user_fb_ids :
                        continue
                    user_fr = User()
                    user_fr.user_fb_id = friend["user_id"]
                    user_fr.user_fb_name = friend["name"]
                    user_fr.user_friends = json.dumps([])
                    user_fr.user_retrieved_friends = False
                    user_fr.user_retrieved_pictures = False
                    d = datetime.datetime.utcnow()
                    user_fr.user_date_creation = d
                    db.session.add(user_fr)
                    db.session.commit()
                user.user_friends = json.dumps(friends_to_update)
                user.user_retrieved_friends = True
                user.user_date_retrieved_friends = datetime.datetime.utcnow()
                db.session.commit()
            download(fb_obj, current_attempt = current_attempt + 1)
                    
    else :
        i = 0
        for user in users_not_pic[:5] :
            i += 1
            print("(", i, ") DOWNLOADING PICTURES => ", user.user_fb_name, " : ", user.user_fb_id)
            pics = fb_obj.get_photos(user.user_fb_id, album="pdp", max=20, face_only=True)
            lenpics = len(pics)
            print("LENGTH OF PICTURES : ", lenpics)
            j = 0
            for pic in pics :
                j += 1
                ext = pic["src"].split("?")[0].split(".")[-1]
                filename = fb_obj.generateName() + '.' + ext
                path = os.path.join(PATH_IMAGE_FACES, filename)
                fb_obj.download_photo(pic["src"], path)

                image = Image()
                image.img_fb_id = pic["photo_id"]
                image.img_url = pic["src"]
                image.img_filename = filename
                image.img_alt = pic["alt"]
                image.img_has_face = True
                image.img_encoding = str(fb_obj.get_image_encoding(path).tolist()).replace('[', '').replace(']', '').replace(' ', '')
                d = datetime.datetime.utcnow()
                image.img_date_creation = d
                image.img_user_id = user.user_id
                db.session.add(image)
                db.session.commit()

                print("Picture downloaded (", j, "/", lenpics, ")")
            if fb_obj.fine :
                print("FINE !")
                user.user_retrieved_pictures = True
                user.user_date_retrieved_pictures = datetime.datetime.utcnow()
                db.session.commit()
            else :
                print("OOPS ! NOT FINE")
                account = Account.query.filter(Account.account_email == fb_obj.email).first()
                if account is not None :
                    account.account_nb_problem += 1
                    account.account_problem_info = fb_obj.msg[-1]
                    account.account_active = False
                    db.session.commit()
                return False
            

def getImgFaces(path) :
    imgs = []
    images = Image.query.all()
    fb = Facebook()
    enc = fb.get_image_encoding(path)
    i = 0
    for im in images :
        i += 1
        im_data = {}
        im_data["url"] = im.img_url
        im_data["img_fb_id"] = im.img_fb_id
        im_data["file_url"] = url_for('facebook_bp.static', filename="img/faces/" + im.img_filename)
        im_data["alt"] = im.img_alt
        im_data["fb_user_id"] = im.img_user.user_fb_id
        im_data["fb_user_name"] = im.img_user.user_fb_name
        im_enc_list = np.array([float(elem) for elem in im.img_encoding.split(',')])
        im_data["dist"] = fb.get_distance_image(im_enc_list, enc)
        # print("(", i, ") Comparaison with : ", im.img_filename, " => dist : ", im_data["dist"])
        imgs.append(im_data)
    return sorted(imgs, key=lambda k : k["dist"])