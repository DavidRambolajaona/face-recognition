from flask import Blueprint, render_template, request, redirect, jsonify, url_for
from appli.models import db, User, Image, Upload, insert_first_data, Account
import os

admin_bp = Blueprint('admin_bp', __name__, template_folder='template', static_folder='static', static_url_path='/admin-static')

@admin_bp.route('/admin/uploads')
def uploads():
    lim = 100
    limit = request.args.get("limit")
    if limit is not None :
        if int(limit) > 0 :
            lim = int(limit)
    uploads = Upload.query.order_by(Upload.up_date_creation.desc()).limit(lim)
    uploads_list = []
    for upload in uploads :
        uploads_list.append({
            "url" : url_for('facebook_bp.static', filename="img/uploads/" + upload.up_filename),
            "original_name" : upload.up_original_name,
            "has_face": upload.up_has_face,
            "date": upload.up_date_creation,
            "ip_adress": upload.up_ip_adress,
            "user_agent": upload.up_user_agent
        })
    return render_template("uploads.html", uploads = uploads_list)

@admin_bp.route('/admin/faces')
def faces():
    lim = 100
    limit = request.args.get("limit")
    if limit is not None :
        if int(limit) > 0 :
            lim = int(limit)
    faces = Image.query.order_by(Image.img_date_creation.desc()).limit(lim)
    faces_list = []
    for face in faces :
        faces_list.append({
            "url" : url_for('facebook_bp.static', filename="img/faces/" + face.img_filename),
            "fb_link": "https://facebook.com/photo/?fbid=" + face.img_fb_id,
            "alt": face.img_alt,
            "has_face": face.img_has_face,
            "date": face.img_date_creation,
            "username": face.img_user.user_fb_name,
            "link_user": "https://facebook.com/" + face.img_user.user_fb_id
        })
    return render_template("faces.html", faces = faces_list)