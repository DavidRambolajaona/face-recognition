from appli import create_app

app = create_app()

if __name__ == "__main__" :
    app.run(debug=True, host='0.0.0.0', use_reloader=False)
    #app.run(debug=True, host='0.0.0.0', use_reloader=True) 