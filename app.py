import flask 
#todo: rewrite to use osmosis class from movie project? 

class word_db:
    def __init__(self, **kwargs): 
        self.db_path = kwargs[db_path]
        self.target_lang = kwargs[target_lang]
        self.base_lang = kwargs[base_lang]

    def add(self, word):
        #word = lemmatized word 
        #id_target_lang = write to db
        # get translation 
        #write to base lang db with fk to lemmatized base
        pass

    def rand_word(self, lang=None):
        if lang == None: 
            lang = self.target_lang
        #open db
        #get random word from lang table in db_path

    def translate(word):
        """get translation from google or somethin"""
        pass 
    
    
        
@app.route("/", methods = ['GET', 'POST'])
def index():
    if request.method == 'GET':
        #SG: whisper api to render text on screen from microphone. tap to add to db 
        return render_template('index.html')
    elif request.method == 'POST':
        #word.html can show translation base word + example use cases. Chatgpt? 
        return render_template(f'word.html?word=%s',word_db.translate(word))

#todo: setup login? for storage?
#login required?
@app.route("/anki_render", methods = ['GET','POST'])        
def learn(): 
    if request.methods == 'GET':
        #right into spaced repetition with random word form db
        return render_template('vocab.html')
    elif request.methods == 'POST': 
        #add spaced repetition library somehow 
        #open train.db 
        #request.query_parameters["difficulty"]
        #store difficulty + timestamp in db 
        #timeseries database? 
        pass


if __name__ == '__main__':
      app.run(host='0.0.0.0', port=123)
