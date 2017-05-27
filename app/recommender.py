from flask import Flask, request, render_template, url_for, redirect
app = Flask(__name__)

@app.route('/result/<search>')
def result(search):
    if len(request.args) > 0:
        search = request.args['search']
        
    results = ["Writing, Hieroglyphic", "Religion", "Egypt", "Inscriptions", "Papyri, Hieratic", "Obelisks",
               "Study and teaching", "Foreign speakers", "Inscriptions, Greek", "Herbs"]
        
    return render_template('result.html', search=search, results=results)

@app.route('/search/')
def search():
    if len(request.args) > 0:
        search = request.args['search']

        return redirect(url_for('result', search=search))
    
    return render_template('search.html')

@app.route('/about/')
def about():
    return render_template('about.html')

@app.route('/help/')
def help():
    return render_template('help.html')

if __name__ == '__main__':
    app.run()
