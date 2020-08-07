from flask import Flask
from flask_restful import Api, Resource, reqparse
from mixdop import checkDocSimilarity


app = Flask(__name__)
api = Api(app)



class Getsimilarity(Resource):

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("article")
        args = parser.parse_args()
        article = args["article"]
        return checkDocSimilarity(article)
        

api.add_resource(Getsimilarity, '/checksimilarity/')  # route 1



# check the least distance of all , if less than 1 then there is some similarity, if 0.0x very similar
if(__name__) == '__main__':
    app.run(port=8080)


